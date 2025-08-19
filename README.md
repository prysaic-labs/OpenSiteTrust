# OpenSiteTrust

[opensitetrust.com](https://opensitetrust.com) · Version: v0.11 · Default language: English ([中文 README](./README.zh-CN.md))

Give every website a transparent 0–100 trust/risk score using Rules + Community + Explanations. Ship a browser extension, open API, and a lightweight forum.

Status: v0.11 implements a working API and UI with caching,
probes, dynamic scoring, and basic i18n.

## What is this?

OpenSiteTrust is an open, explainable, and reusable website scoring ecosystem.
We compose multiple dimensions into one score and show evidence cards:
- S Security (HTTPS, security headers, TLS expiry, DNSSEC)
- C Credibility (domain heuristics, optional Google Safe Browsing v4,
  lightweight SEO presence)
- T Transparency (privacy/terms/about/contact, security.txt, humans.txt,
  imprint, security page, bounty)
- U User/Community signals (Wilson lower bound; excluded when no votes)

Use cases:
- Users: see a green/amber/red bar with a score and “why” at a glance.
- Creators/Media: assess source credibility quickly.
- Researchers/Developers: consume an open API and data for tools and studies.
- Site owners: appeal and improve transparency signals.

## Scope (v0.11)

- Scoring engine with probes and explanations (caching via Redis, Postgres persistence).
- Open API: GET /v1/sites/{host}, GET /v1/sites/{host}/explain, POST /v1/votes.
- Web UI (Next.js + Tailwind + shadcn-like components), basic i18n via
	`?lang=` (en default; zh/zh-Hant/ja/es supported).
- Caddy reverse proxy, Docker Compose deployment.

## Architecture and tech stack

Two paths (can be mixed):

1) Serverless rapid path
- Frontend: UniApp H5
- Backend: uniCloud (Node)
- DB: managed document store (Mongo-like)
- Cache/Rate limiting: managed cache or built-ins

2) Containerized and controllable (recommended)
- Frontend: Next.js (or UniApp H5)
- API: FastAPI (Python) or NestJS (Node)
- Worker: Celery/RQ (Python) or BullMQ (Node)
- Database: PostgreSQL
- Cache/Queue/Rate limit: Redis
- Proxy: Caddy/Nginx; CDN/WAF: Cloudflare
- Orchestration: Docker Compose (dev), then split services later

## Data model and APIs

- SQL schema: see docs/data-model.sql
- API spec and examples: see docs/api.md
	- No votes: U displays 0 with a "No ratings" note and is EXCLUDED from
		the score (weights re-normalize over S/C/T).
	- Google Safe Browsing v4 (optional): set
		`GOOGLE_SAFE_BROWSING_API_KEY`; supports raw key or full API URL with
		`?key=`.
	- SEO signals: title, description, canonical, robots.txt/meta, Open Graph,
		JSON-LD, sitemap.xml.
	- Transparency: privacy, terms, about, contact, imprint/impressum,
		security page, bug bounty, security.txt, humans.txt.
	- Security: HTTPS behavior, headers
		(HSTS/CSP/XCTO/XFO/Referrer-Policy/Permissions-Policy), TLS expiry,
		DNSSEC.

## Deployment (Ubuntu 24.04 baseline)

- Target OS: Ubuntu 24.04.1 LTS (GNU/Linux 6.8 x86_64). See docs/deployment.md.
- A sample docker-compose.yml and .env.example are provided.
- Caddy is included as the edge reverse proxy on ports 80/443. Point your DNS
	A/AAAA to the server, and Caddy will handle certificates automatically.
- ENV: `.env` alongside `docker-compose.yml` (optional
	`GOOGLE_SAFE_BROWSING_API_KEY=` as raw key or full URL with `?key=`).

## Privacy, security, and abuse mitigation

See docs/privacy-security.md for details on data minimization, k-anonymity,
CSRF/XSS protections, rate limits, reputation weighting, and signed snapshots.

## Open-source policy and licenses

- Backend / scoring engine: AGPL-3.0
- Browser extension / SDKs: Apache-2.0
- User-labeled data: CC BY-SA 4.0

Details in docs/open-source-governance.md.

## Contributing

See CONTRIBUTING.md and CODE_OF_CONDUCT.md. For security issues, use SECURITY.md.

## Versioning and development log

- Default project language is English; switch via `?lang=xx` (en/zh/zh-Hant/ja/es).
- We version starting from v0.01 and update DEVLOG.md on every meaningful change.

— OpenSiteTrust Contributors
