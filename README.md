# OpenSiteTrust

[opensitetrust.com](https://opensitetrust.com)
· Version: v0.26 · Default language: English
([中文 README](./README.zh-CN.md))

Project by Prysaic Libs · GitHub: [https://github.com/prysaic-labs/OpenSiteTrust](https://github.com/prysaic-labs/OpenSiteTrust)

Give every website a transparent 0–100 trust/risk score using Rules +
Community + Explanations. Ship a browser extension, open API, and a
lightweight forum.

Status: v0.25 delivers a working API and UI with caching, probes,
dynamic scoring, admin tools, GitHub/Email auth, and expanded i18n.

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

## Scope (MVP)

- Scoring engine with probes and explanations (caching via Redis, Postgres persistence).
- Open API: GET /v1/sites/{host}, GET /v1/sites/{host}/explain, POST /v1/votes.
- Web UI (Next.js + Tailwind + shadcn-like components), multi-language via `?lang=`
  (en default; zh/zh-Hant/ja/es supported). Added About/Contact/Privacy pages,
  robots.txt & sitemap, and a drawer menu with SEO links.
- Caddy reverse proxy, Docker Compose deployment.

## Project plan and roadmap

Vision: open, explainable site‑trust ecosystem with S/C/T/U signals,
public APIs, and community participation.

Near‑term roadmap (0.x):
- Enrich probes and evidence cards; improve transparency/credibility coverage
- Browser extension and basic moderation workflows
- Public data export and snapshotting; abuse safeguards
- More identity providers (optional) and appeal flows

1.x ideas (post‑MVP):
- Rule marketplace and pluggable scorers; data partnerships
- Advanced dashboards and research APIs; federation options

## Quick start (Docker Compose)

Prerequisites:
- Docker Engine 24+ and Docker Compose v2
- A domain pointing to your server if using Caddy for TLS

Steps (Linux server):
1) Clone repo and enter folder
2) Copy `.env.example` to `.env` and edit for your environment (see below)
3) Build and start

Services:
- api: FastAPI on 8000 (internal), proxied by Caddy
- web: Next.js on 3000 (internal), proxied by Caddy
- db: PostgreSQL 16 (with healthcheck)
- redis: Redis 7
- caddy: serves ports 80/443

See also `docs/deployment.md` for details.

## Local development (without Docker)

Recommended if you prefer running each service locally.

Prerequisites:
- Node.js 20+
- Python 3.11+
- PostgreSQL 16
- Redis 7

Setup:
1. Backend API

    - Create and export env vars: `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`
      (optional for votes), optional `GOOGLE_SAFE_BROWSING_API_KEY`
    - Install deps: `pip install -r apps/api/requirements.txt`
    - Run: `uvicorn app.main:app --reload` from `apps/api`
1. Web app

- From `apps/web`: `npm i` then `npm run dev`
- Visit <http://localhost:3000>

Notes:
- The web header shows version from `NEXT_PUBLIC_VERSION` (keep in `.env` and `VERSION`).
- i18n via `?lang=`; defaults to `en`. Supported: en, zh, zh-Hant, ja, es.

## Environment and .env

Do NOT commit `.env`. Copy `.env.example` to `.env` and set:
- DATABASE_URL (postgres), REDIS_URL (redis)
- JWT_SECRET (long random string)
- WEB_ORIGIN (e.g., `https://your.domain`)
- GitHub OAuth (optional): GITHUB_CLIENT_ID/SECRET/REDIRECT_URI
- SMTP (optional): host/user/pass/sender for email codes
- GSB key (optional): GSB_API_KEY for Safe Browsing
- NEXT_PUBLIC_VERSION (UI version badge)

See `.env.example` for details and safe defaults.

## Environment variables

Common variables (via `.env` or environment):
- `DATABASE_URL` (e.g., `postgres://user:pass@localhost:5432/site`)
- `REDIS_URL` (e.g., `redis://localhost:6379`)
- `JWT_SECRET` (optional; needed for protected endpoints if any later)
- `GOOGLE_SAFE_BROWSING_API_KEY` (optional; raw key or full API URL with `?key=`)
- `COMMUNITY_RAMP_N` (optional; ramp-up for U weight)
- `COMMUNITY_BASELINE` (optional; smoothing baseline for U)
- `NEXT_PUBLIC_VERSION` (optional; UI version badge)

## Architecture and tech stack

Two paths (can be mixed):

1) Serverless rapid path
- Frontend: UniApp H5
- Backend: uniCloud (Node)
- DB: managed document store (Mongo-like)
- Cache/Rate limiting: managed cache or built-ins

1) Containerized and controllable (recommended)
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
  - No votes: U displays 0 with a "No ratings" note and is EXCLUDED from the
    score (weights re-normalize over S/C/T).
  - Google Safe Browsing v4 (optional): set `GOOGLE_SAFE_BROWSING_API_KEY`;
    supports raw key or full API URL with `?key=`.
  - SEO signals: title, description, canonical, robots.txt/meta, Open Graph,
    JSON-LD, sitemap.xml.
  - Transparency: privacy, terms, about, contact, imprint/impressum, security
    page, bug bounty, security.txt, humans.txt.
  - Security: HTTPS behavior, headers (HSTS/CSP/XCTO/XFO/Referrer-Policy/
    Permissions-Policy), TLS expiry, DNSSEC.

## Deployment (Ubuntu 24.04 baseline)

- Target OS: Ubuntu 24.04 LTS. See docs/deployment.md.
- Compose and `.env.example` are provided.
- Caddy terminates TLS on 80/443; point your DNS A/AAAA to the server
  and Caddy will issue certs.
- Env lives in `.env` next to `docker-compose.yml`.

Minimum server spec (for a small instance):
- 1 vCPU, 1–2 GB RAM, 10 GB disk (demo)
Recommended: 2 vCPU, 2–4 GB RAM, 20+ GB disk

### Step-by-step (Docker Compose)

Prerequisites:
- Ubuntu 24.04 LTS or similar Linux
- Docker Engine 24+ and Docker Compose v2
- A domain pointing to this server (A/AAAA records)

1. Clone and prepare env

- Clone the repo and enter it.
- Copy `.env.example` to `.env` and fill values:
  - `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `WEB_ORIGIN`
  - Optional: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`,
    `GITHUB_REDIRECT_URI`
  - Optional: SMTP settings for email codes
  - Optional: `GSB_API_KEY` for Safe Browsing
  - `NEXT_PUBLIC_VERSION` (keep consistent with `VERSION`)

1. Configure DNS and Caddy

- Point your domain to this server's public IP.
- Caddy will terminate TLS automatically using the `Caddyfile`.

1. Build and start services

Run on the server:

```bash
docker compose up -d --build
docker compose ps
```

1. Verify

- API health: `GET /v1/health` should return version and time.
- Public config: `GET /v1/config` shows flags like SMTP/GitHub configured.
- Visit your domain in a browser; TLS should be valid.

1. Create or use an account

- Email code registration needs SMTP env set.
- GitHub registration requires OAuth app configured (see below).
- Admin features are gated by the `ADMIN_EMAILS` list.

1. Update/redeploy

```bash
git pull
docker compose up -d --build api web
docker compose logs -f --tail=200 api
```

1. Logs and maintenance

```bash
docker compose logs -f api
docker compose logs -f web
docker compose ps
docker compose restart api web
```

1. Backup (PostgreSQL volume)

```bash
# Dump
docker compose exec -T db pg_dump -U postgres site > backup.sql
# Restore (destructive)
docker compose exec -T db psql -U postgres site < backup.sql
```

### GitHub OAuth setup

1) Create an OAuth app at GitHub Developers.
2) Homepage URL: your `WEB_ORIGIN`.
3) Authorization callback URL:
   `WEB_ORIGIN/login/github-callback`.
4) Put `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, and optionally
   `GITHUB_REDIRECT_URI` into `.env`.

### SMTP (email verification codes)

- Fill `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, and
  `SMTP_SENDER` in `.env`.
- Test `POST /v1/auth/send-code` with your email; check logs for delivery.

### Troubleshooting

- Compose fails to build:
  - Check Docker version and available disk space.
  - Verify `.env` exists next to `docker-compose.yml`.
- GitHub OAuth returns 400/redirect issues:
  - Ensure `GITHUB_CLIENT_ID/SECRET` and redirect URI match exactly.
  - Check `/v1/config` for `github_configured: true`.
- Email code not received:
  - Verify SMTP creds; check provider console.
  - Rate limit: see `/v1/config.email_code_rate_limit`.
- DB column missing (e.g., `users.handle`):
  - The API runs best-effort DDL on startup; restart `api` after upgrade.
- Port conflicts:
  - Ensure ports 80/443 are free (stop any nginx/apache).

### Windows PowerShell (optional)

For Windows developers using PowerShell:

```powershell
docker compose up -d --build
docker compose ps
docker compose logs -f --tail 200 api
```

## Privacy, security, and abuse mitigation

See docs/privacy-security.md for details on data minimization, k-anonymity,
CSRF/XSS protections, rate limits, reputation weighting, and signed snapshots.

## Open-source policy and licenses

- Backend / scoring engine: AGPL-3.0
- Browser extension / SDKs: Apache-2.0
- User-labeled data: CC BY-SA 4.0

Details in docs/open-source-governance.md.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).
Security issues: see [SECURITY.md](./SECURITY.md).
Contact: [prysaic@gmail.com](mailto:prysaic@gmail.com)

## Versioning and development log

- Default project language is English; switch via `?lang=xx` (en/zh/zh-Hant/ja/es).
- We version starting from v0.01 and update DEVLOG.md on every meaningful change.

— OpenSiteTrust Contributors
