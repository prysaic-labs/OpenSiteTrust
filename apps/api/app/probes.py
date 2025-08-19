from __future__ import annotations
import httpx
from typing import Dict, Tuple
import ssl
import socket
from datetime import datetime, timezone
import asyncio

# optional dependency: dnspython
dns = None
try:  # pragma: no cover - best effort
    import dns.resolver  # type: ignore
    dns = dns  # type: ignore  # keep module binding for truthy check
except Exception:
    dns = None

import os
import urllib.parse
from bs4 import BeautifulSoup  # type: ignore


def _extract_gsb_key(value: str | None) -> str | None:
    if not value:
        return None
    v = value.strip()
    # If full URL, parse ?key=...
    if v.lower().startswith("http://") or v.lower().startswith("https://"):
        try:
            q = urllib.parse.urlparse(v).query
            params = urllib.parse.parse_qs(q)
            k = params.get("key", [None])[0]
            return k
        except Exception:
            return None
    # If looks like '...key=XXXX', extract after '='
    if "key=" in v and "\n" not in v and " " not in v:
        try:
            return v.split("key=", 1)[1]
        except Exception:
            return None
    # Otherwise assume it's the raw API key
    return v


async def google_safe_browsing_check(host: str) -> Dict[str, bool]:
    """Optional Google Safe Browsing v4 check (site-level heuristic).
    Requires env GOOGLE_SAFE_BROWSING_API_KEY. Returns { flagged: bool }.
    """
    api_key = _extract_gsb_key(os.getenv("GOOGLE_SAFE_BROWSING_API_KEY"))
    if not api_key:
        return {"flagged": False}
    url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    body = {
        "client": {"clientId": "opensitetrust", "clientVersion": "0.10"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": f"http://{host}"}, {"url": f"https://{host}"}],
        },
    }
    try:
        async with httpx.AsyncClient(timeout=6) as client:
            r = await client.post(url, json=body)
            if r.status_code == 200:
                j = r.json()
                return {"flagged": bool(j.get("matches"))}
    except Exception:
        pass
    return {"flagged": False}


async def seo_signals_probe(host: str) -> Dict[str, bool]:
    """Lightweight SEO presence signals: title, meta description, canonical, robots.txt, robots meta, OG, JSON-LD, sitemap.xml."""
    out: Dict[str, bool] = {
        "has_title": False,
        "has_meta_description": False,
        "has_canonical": False,
        "has_robots": False,
        "has_meta_robots": False,
        "has_open_graph": False,
        "has_jsonld": False,
        "has_sitemap": False,
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=6) as client:
            r = await client.get(f"https://{host}")
            html = r.text
            soup = BeautifulSoup(html, "html.parser")
            title = soup.find("title")
            if title and title.text.strip():
                out["has_title"] = True
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                out["has_meta_description"] = True
            meta_robots = soup.find("meta", attrs={"name": "robots"})
            if meta_robots and meta_robots.get("content"):
                out["has_meta_robots"] = True
            link_canonical = soup.find("link", attrs={"rel": "canonical"})
            if link_canonical and link_canonical.get("href"):
                out["has_canonical"] = True
            # Open Graph
            og_title = soup.find("meta", attrs={"property": "og:title"})
            if og_title and og_title.get("content"):
                out["has_open_graph"] = True
            # JSON-LD schema.org
            jsonld = soup.find("script", attrs={"type": "application/ld+json"})
            if jsonld and jsonld.text.strip():
                out["has_jsonld"] = True
            # robots.txt
            try:
                r2 = await client.get(f"https://{host}/robots.txt")
                out["has_robots"] = r2.status_code == 200 and len(r2.text) > 0
            except Exception:
                pass
            # sitemap.xml
            try:
                r3 = await client.get(f"https://{host}/sitemap.xml")
                out["has_sitemap"] = r3.status_code == 200 and len(r3.text) > 0
            except Exception:
                pass
    except Exception:
        pass
    return out


async def http_probe(host: str) -> Tuple[bool, dict]:
    """Fetch over HTTPS and HTTP, collect security headers and upgrade info.
    Returns (https_ok, info)
    info keys: http_ok, https_ok, status, hsts, csp, xcto, xfo, refpol, permspol, xxss, http_upgrades_https
    """
    url_http = f"http://{host}"
    url_https = f"https://{host}"
    info = {
        "http_ok": False,
        "https_ok": False,
        "status": None,
        "hsts": False,
        "csp": False,
        "xcto": False,
        "xfo": False,
        "refpol": False,
        "permspol": False,
        "xxss": False,
        "http_upgrades_https": False,
    }
    https_ok = False
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=8) as client:
            r = await client.get(url_https)
            info["https_ok"] = True
            info["status"] = r.status_code
            h = {k.lower(): v for k, v in r.headers.items()}
            info["hsts"] = "strict-transport-security" in h
            info["csp"] = bool(h.get("content-security-policy"))
            info["xcto"] = h.get("x-content-type-options", "").lower().strip() == "nosniff"
            info["xfo"] = bool(h.get("x-frame-options"))
            info["refpol"] = bool(h.get("referrer-policy"))
            info["permspol"] = bool(h.get("permissions-policy"))
            info["xxss"] = bool(h.get("x-xss-protection"))
            https_ok = True
    except Exception:
        https_ok = False

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=8) as client:
            r = await client.get(url_http)
            info["http_ok"] = True
            # Detect upgrade: if final URL scheme is https
            try:
                info["http_upgrades_https"] = (r.url.scheme.lower() == "https")
            except Exception:
                pass
            if not info.get("status"):
                info["status"] = r.status_code
    except Exception:
        pass

    return https_ok, info


async def discover_transparency_pages(host: str) -> Dict[str, bool]:
    """Best-effort checks for transparency pages.
    Returns flags for privacy, terms, about, contact, security_txt, humans_txt.
    """
    paths = {
        "privacy": ["/privacy", "/privacy-policy", "/policies/privacy"],
        "terms": ["/terms", "/terms-of-service", "/tos", "/legal/terms"],
        "about": ["/about", "/about-us"],
        "contact": ["/contact", "/contact-us"],
        "imprint": ["/imprint", "/impressum"],
        "security_page": ["/security", "/security-policy"],
        "bug_bounty": ["/bug-bounty", "/security#bounty"],
    }
    results = {k: False for k in [
        "privacy", "terms", "about", "contact", "imprint", "security_page", "bug_bounty",
        "security_txt", "humans_txt"
    ]}
    base = f"https://{host}"
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=6) as client:
            # well-known first
            try:
                r = await client.get(base + "/.well-known/security.txt")
                results["security_txt"] = r.status_code < 400
            except Exception:
                pass
            try:
                r = await client.get(base + "/humans.txt")
                results["humans_txt"] = r.status_code < 400
            except Exception:
                pass
            for key, pths in paths.items():
                if results[key]:
                    continue
                for p in pths:
                    try:
                        r = await client.get(base + p)
                        if r.status_code < 400:
                            results[key] = True
                            break
                    except Exception:
                        continue
    except Exception:
        pass
    return results


def domain_heuristics(host: str) -> Dict[str, float]:
    h = host.lower()
    susp_keywords = ["free", "deal", "cheap", "login", "verify", "gift", "win", "bonus"]
    danger_tld = ["zip", "mov", "xyz", "top"]
    trusted_tld = ["gov", "edu", "mil"]
    neutral_good_tld = ["org"]
    score_c = 0.6
    if any(k in h for k in susp_keywords):
        score_c -= 0.15
    if any(h.endswith("." + t) for t in danger_tld):
        score_c -= 0.1
    if any(h.endswith("." + t) for t in neutral_good_tld):
        score_c += 0.05
    if any(h.endswith("." + t) for t in trusted_tld):
        score_c += 0.25
    # subdomain / hyphen heuristics
    parts = h.split(".")
    if len(parts) >= 4:
        score_c -= 0.05
    if "--" in h or h.count("-") >= 3:
        score_c -= 0.05
    if len(h) > 60:
        score_c -= 0.05
    score_c = max(0.0, min(1.0, score_c))
    return {"credibility": score_c}


async def _resolve_txt(domain: str) -> list[str]:
    if not dns:
        return []
    try:
        res = dns.resolver.resolve(domain, 'TXT', lifetime=3.0)
        return [b"".join(r.strings).decode('utf-8', 'ignore') for r in res]  # type: ignore
    except Exception:
        return []


async def dns_email_auth_probe(host: str) -> Dict[str, bool]:
    """Check SPF for apex, DMARC at _dmarc, and MX records. Also provide dmarc_policy and spf_strict flags."""
    out: Dict[str, bool | str] = {"spf": False, "dmarc": False, "mx": False, "dmarc_policy": "", "spf_strict": False}
    if not dns:
        return out
    # MX
    try:
        ans = dns.resolver.resolve(host, 'MX', lifetime=3.0)
        out["mx"] = len(ans) > 0
    except Exception:
        out["mx"] = False
    # SPF at apex
    for txt in await _resolve_txt(host):
        if txt.lower().startswith("v=spf1"):
            out["spf"] = True
            if "-all" in txt:
                out["spf_strict"] = True
            break
    # DMARC at _dmarc
    for txt in await _resolve_txt(f"_dmarc.{host}"):
        if txt.lower().startswith("v=dmarc1"):
            out["dmarc"] = True
            # parse p= policy
            try:
                parts = [p.strip() for p in txt.split(";")]
                for p in parts:
                    if p.lower().startswith("p="):
                        out["dmarc_policy"] = p.split("=", 1)[1].strip()
                        break
            except Exception:
                pass
            break
    return out


async def dnssec_probe(host: str) -> Dict[str, bool]:
    """Check for presence of DS records indicating DNSSEC at the zone apex."""
    if not dns:
        return {"dnssec": False}
    try:
        ans = dns.resolver.resolve(host, 'DS', lifetime=3.0)
        return {"dnssec": len(ans) > 0}
    except Exception:
        return {"dnssec": False}


async def tls_expiry_days(host: str, port: int = 443) -> int | None:
    """Return days until certificate expiry, or None on failure."""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host, port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                not_after = cert.get('notAfter')
                if not_after:
                    dt = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z').replace(tzinfo=timezone.utc)
                    delta = dt - datetime.now(timezone.utc)
                    return max(0, delta.days)
    except Exception:
        return None
    return None
