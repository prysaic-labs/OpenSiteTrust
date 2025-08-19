# OpenSiteTrust DEVLOG

Version baseline: v0.01

## v0.01 (2025-08-17)
- Add markdownlint config to reduce noise during drafting.

Next:
- Scaffold apps/api (FastAPI or NestJS) with /v1/sites,
  /v1/sites/{host}/explain, /v1/votes.
- Scaffold apps/web (Next.js) with detail page and minimal forum.
- Implement minimal scoring engine and caching.

## v0.02 (2025-08-17)
- Clarify scope: Added MVP PRD (docs/specs/mvp-prd.md), prioritized backlog,
  release plan.
- Added OpenAPI spec (docs/specs/api/openapi.yaml).
- Added ADR 0001 selecting containerized stack: FastAPI + Celery + PostgreSQL +
  Redis + Next.js.
- Updated README and README.zh-CN to emphasize default English language and domain.
- Bumped VERSION to v0.02.

## v0.03 (2025-08-17)
- Backend bootstrap: FastAPI minimal API with scoring skeleton and in-memory votes.
- Added Dockerfile and requirements for API service.
- Updated deployment docs for Ubuntu 24.04.1 baseline and compose steps.
- Updated README deployment section to reflect Ubuntu baseline.
- Bumped VERSION to v0.03.

## v0.04 (2025-08-17)
- Web UI bootstrap (Next.js App Router): home + site detail page fetching /v1.
- Added Caddy reverse proxy with automatic HTTPS for opensitetrust.com.
- Updated docker-compose to include caddy and wire api/web internally.
- Fixed compose volumes key duplication.
- Bumped VERSION to v0.04.

## v0.05 (2025-08-18)
- API: Added /v1/health, exposed docs at /v1/docs and openapi at /v1/openapi.json.
- Web: Home page tweaks (links to examples and API), Site page adds simple
  community voting to POST /v1/votes.
- Caddy: Added www to apex redirect and HSTS header; removed invalid auto_https directive.
- Compose: Removed obsolete version key to silence warnings.
- Deployment: Restart caddy to pick up config; verify ports 80/443 and domain HTTPS.

## v0.06 (2025-08-18)
- API/DB: Fix startup DuplicateTableError by removing redundant explicit Index
  declarations and column index duplication. Keep unique constraint on
  sites.host; let SQLAlchemy generate indexes once. Safe with existing DB.
- Bumped VERSION to v0.06.

## v0.07 (2025-08-18)
- Scoring: Strengthened S by checking more security headers and HTTP→HTTPS
  upgrade.
- Scoring: Implemented transparency discovery (privacy/terms/about/contact,
  security.txt, humans.txt) to build T.
- Probes: Added discover_transparency_pages; enhanced http_probe return fields.
- API: Integrate new probes into GET /v1/sites/{host} and POST /v1/votes.

## v0.08 (2025-08-18)
- Probes: Add DNS email auth probe (SPF/DMARC/MX) and TLS certificate expiry days.
- Scoring: Use email auth to boost T; use cert expiry to tweak S.
- Explain: /v1/sites/{host}/explain now returns detailed signals including
  security headers, transparency pages, email auth, and cert expiry.

## v0.09 (2025-08-19)
- API: Add Redis JSON cache with safe fallbacks; introduce
  cache_get_json/cache_set_json.
- Probes: Introduce optional Google Safe Browsing v4 check (requires
  GOOGLE_SAFE_BROWSING_API_KEY), and lightweight SEO presence signals
  (title/meta/canonical/robots.txt).
- Scoring: Add compose_score_dynamic to re-normalize weights when U is
  excluded.

## v0.10 (2025-08-19)
- API: Rebuild main.py cleanly after a broken merge; integrate caching and
  all new probes.
- Rule: If there are no community votes, display U=0 with "暂无评价" and exclude
  U from the composite score. Response now includes votes_total and u_included
  flags to aid the UI.
- Explain: Include GSB flag and SEO presence signals in /explain; bump
  model_version to v0.3.
- Web: Site page shows the "暂无评价，不计入总分" note when no votes are present.
- Version: Bump VERSION to v0.10; /v1/health reports v0.10.
