from datetime import datetime, timezone
import os
import re
from fastapi import FastAPI
from sqlalchemy import select

from .schemas import SiteScore, Breakdown, Explanation, Signal, VoteRequest, VoteResponse
from .scoring import (
    compose_score_dynamic,
    compute_u_from_votes,
    classify_level,
    compute_u_adjusted,
    compose_score_weighted,
)
from .db import SessionLocal, init_db, Site, Vote
from .probes import (
    http_probe,
    domain_heuristics,
    discover_transparency_pages,
    dns_email_auth_probe,
    dnssec_probe,
    tls_expiry_days,
    google_safe_browsing_check,
    seo_signals_probe,
)
from .cache import cache_get_json, cache_set_json


app = FastAPI(
    title="OpenSiteTrust API (MVP Bootstrap)",
    docs_url="/v1/docs",
    openapi_url="/v1/openapi.json",
    redoc_url=None,
)

API_PREFIX = "/v1"


def normalize_host(value: str) -> str:
    t = (value or "").strip().lower()
    if not t:
        return t
    try:
        # Prepend scheme if missing so URL parsing works
        u = __import__("urllib.parse").urllib.parse.urlparse(
            t if re.match(r"^[a-z]+://", t, flags=re.I) else f"http://{t}"
        )
        host = u.hostname or t
    except Exception:
        # Fallback: strip scheme-like prefix and any path/query/fragment
        s = re.sub(r"^[a-z]+://", "", t, flags=re.I)
        host = s.split("/")[0].split("?")[0].split("#")[0]
    return host.rstrip('.')


@app.on_event("startup")
async def _startup():
    await init_db()


@app.get(f"{API_PREFIX}/sites/{{host}}", response_model=SiteScore)
async def get_site_score(host: str):
    host = normalize_host(host)

    # cache first
    cached = await cache_get_json(f"site:{host}")
    if cached:
        return cached

    # votes from DB
    async with SessionLocal() as session:
        res = await session.execute(select(Vote).where(Vote.host == host))
        votes = [
            {"label": v.label, "reason": v.reason, "ts": v.ts.isoformat()}
            for v in res.scalars().all()
        ]

    # probes
    https_ok, info = await http_probe(host)
    heur = domain_heuristics(host)
    transp = await discover_transparency_pages(host)
    email_auth = await dns_email_auth_probe(host)
    dnssec = await dnssec_probe(host)
    cert_days = await tls_expiry_days(host)
    gsb = await google_safe_browsing_check(host)
    seo = await seo_signals_probe(host)

    # U
    U, counts = compute_u_from_votes(votes)
    n_votes = sum(counts.values())
    include_u = n_votes > 0

    # S
    S = 0.9 if https_ok else 0.5
    if info.get("http_upgrades_https"):
        S += 0.05
    for key in ("csp", "hsts", "xcto", "xfo", "refpol", "permspol"):
        if info.get(key):
            S += 0.02
    if dnssec.get("dnssec"):
        S += 0.03
    if isinstance(cert_days, int):
        if cert_days >= 60:
            S += 0.02
        elif cert_days <= 7:
            S -= 0.05
    S = max(0.0, min(1.0, S))

    # C
    C = heur["credibility"]
    if gsb.get("flagged"):
        C = max(0.0, C - 0.3)
    seo_bonuses = [
        seo.get("has_title"), seo.get("has_meta_description"), seo.get("has_canonical"),
        seo.get("has_open_graph"), seo.get("has_jsonld"), seo.get("has_robots"), seo.get("has_sitemap")
    ]
    C = min(1.0, C + 0.01 * sum(1 for b in seo_bonuses if b))

    # T
    t_hits = sum(1 for v in transp.values() if v)
    # email auth transparency
    t_hits += sum(1 for k, v in email_auth.items() if k in ("spf", "dmarc", "mx") and v)
    # strong policies bonus
    strong = 0
    if email_auth.get("dmarc_policy") in ("reject", "quarantine"):
        strong += 1
    if email_auth.get("spf_strict"):
        strong += 1
    t_hits += strong
    T = min(1.0, 0.4 + 0.1 * t_hits)

    # Adjust U and its effective weight with a ramp to reduce early-vote impact
    if include_u:
        ramp_n = int(os.getenv("COMMUNITY_RAMP_N", "10") or 10)
        baseline = float(os.getenv("COMMUNITY_BASELINE", "0.5") or 0.5)
        U_adj, u_factor = compute_u_adjusted(U, n_votes, baseline=baseline, ramp_n=ramp_n)
        score = compose_score_weighted(S, C, T, U_adj, u_factor)
        breakdown = {"S": S, "C": C, "T": T, "U": U_adj}
    else:
        breakdown = {"S": S, "C": C, "T": T, "U": 0.0}
        score = compose_score_dynamic(S, C, T, U, include_u)
    level = classify_level(score)

    now = datetime.now(timezone.utc)
    async with SessionLocal() as session:
        existing = (await session.execute(select(Site).where(Site.host == host))).scalar_one_or_none()
        if existing:
            existing.last_score = score
            existing.last_breakdown = breakdown
            existing.last_level = level
            existing.updated_at = now
        else:
            session.add(
                Site(host=host, last_score=score, last_breakdown=breakdown, last_level=level, updated_at=now)
            )
        await session.commit()

    resp = {
        "host": host,
        "score": score,
        "level": level,
        "breakdown": breakdown,
        "updated_at": now.isoformat(),
        "votes_total": n_votes,
        "u_included": include_u,
    }
    await cache_set_json(f"site:{host}", resp)
    return resp


@app.get(f"{API_PREFIX}/sites/{{host}}/explain", response_model=Explanation)
async def get_explain(host: str):
    host = normalize_host(host)
    # votes from DB for consistent counts
    async with SessionLocal() as session:
        res = await session.execute(select(Vote).where(Vote.host == host))
        votes = [
            {"label": v.label, "reason": v.reason, "ts": v.ts.isoformat()}
            for v in res.scalars().all()
        ]
    u, counts = compute_u_from_votes(votes)
    https_ok, info = await http_probe(host)
    transp = await discover_transparency_pages(host)
    email_auth = await dns_email_auth_probe(host)
    dnssec = await dnssec_probe(host)
    cert_days = await tls_expiry_days(host)
    gsb = await google_safe_browsing_check(host)
    seo = await seo_signals_probe(host)

    signals = [
        Signal(key="https_ok", value=https_ok),
        *[Signal(key=k, value=v) for k, v in info.items()],
        *[Signal(key=f"transparency_{k}", value=v) for k, v in transp.items()],
        *[Signal(key=f"email_{k}", value=v) for k, v in email_auth.items()],
        Signal(key="tls_cert_days_to_expire", value=cert_days),
        Signal(key="google_safe_browsing_flagged", value=gsb.get("flagged")),
        *[Signal(key=f"seo_{k}", value=v) for k, v in seo.items()],
        Signal(key="community_wilson", value=round(u, 2)),
        Signal(key="votes_counts", value=counts),
    ]
    return Explanation(host=host, model_version="v0.3", signals=signals)


@app.post(f"{API_PREFIX}/votes", response_model=VoteResponse)
async def post_vote(payload: VoteRequest):
    host = normalize_host(payload.host)
    user = payload.user or "anonymous"
    now = datetime.now(timezone.utc)
    async with SessionLocal() as session:
        session.add(Vote(host=host, user_id=user, label=payload.label, reason=payload.reason, ts=now))
        await session.commit()

    # recompute
    async with SessionLocal() as session:
        res = await session.execute(select(Vote).where(Vote.host == host))
        votes = [
            {"label": v.label, "reason": v.reason, "ts": v.ts.isoformat()}
            for v in res.scalars().all()
        ]
    U, counts = compute_u_from_votes(votes)
    n_votes = sum(counts.values())
    include_u = n_votes > 0
    https_ok, info = await http_probe(host)
    heur = domain_heuristics(host)
    transp = await discover_transparency_pages(host)
    email_auth = await dns_email_auth_probe(host)
    dnssec = await dnssec_probe(host)
    cert_days = await tls_expiry_days(host)
    gsb = await google_safe_browsing_check(host)
    seo = await seo_signals_probe(host)

    S = 0.9 if https_ok else 0.5
    if info.get("http_upgrades_https"):
        S += 0.05
    for key in ("csp", "hsts", "xcto", "xfo", "refpol", "permspol"):
        if info.get(key):
            S += 0.02
    if dnssec.get("dnssec"):
        S += 0.03
    if isinstance(cert_days, int):
        if cert_days >= 60:
            S += 0.02
        elif cert_days <= 7:
            S -= 0.05
    S = max(0.0, min(1.0, S))

    C = heur["credibility"]
    if gsb.get("flagged"):
        C = max(0.0, C - 0.3)
    seo_bonuses = [
        seo.get("has_title"), seo.get("has_meta_description"), seo.get("has_canonical"),
        seo.get("has_open_graph"), seo.get("has_jsonld"), seo.get("has_robots"), seo.get("has_sitemap")
    ]
    C = min(1.0, C + 0.01 * sum(1 for b in seo_bonuses if b))

    t_hits = sum(1 for v in transp.values() if v)
    t_hits += sum(1 for k, v in email_auth.items() if k in ("spf", "dmarc", "mx") and v)
    strong = 0
    if email_auth.get("dmarc_policy") in ("reject", "quarantine"):
        strong += 1
    if email_auth.get("spf_strict"):
        strong += 1
    t_hits += strong
    T = min(1.0, 0.4 + 0.1 * t_hits)

    if include_u:
        ramp_n = int(os.getenv("COMMUNITY_RAMP_N", "10") or 10)
        baseline = float(os.getenv("COMMUNITY_BASELINE", "0.5") or 0.5)
        U_adj, u_factor = compute_u_adjusted(U, n_votes, baseline=baseline, ramp_n=ramp_n)
        breakdown = {"S": S, "C": C, "T": T, "U": U_adj}
        new_score = compose_score_weighted(S, C, T, U_adj, u_factor)
    else:
        breakdown = {"S": S, "C": C, "T": T, "U": 0.0}
        new_score = compose_score_dynamic(S, C, T, U, include_u)

    async with SessionLocal() as session:
        existing = (await session.execute(select(Site).where(Site.host == host))).scalar_one_or_none()
        if existing:
            existing.last_score = new_score
            existing.last_breakdown = breakdown
            existing.last_level = classify_level(new_score)
            existing.updated_at = now
        else:
            session.add(
                Site(
                    host=host,
                    last_score=new_score,
                    last_breakdown=breakdown,
                    last_level=classify_level(new_score),
                    updated_at=now,
                )
            )
        await session.commit()

    # invalidate cache by overwriting small TTL
    await cache_set_json(f"site:{host}", None, ttl=1)
    return VoteResponse(ok=True, new_score=new_score)


@app.get(f"{API_PREFIX}/health")
async def health():
    return {
        "ok": True,
        "service": "api",
    "version": "v0.11",
        "time": datetime.now(timezone.utc).isoformat(),
    }
