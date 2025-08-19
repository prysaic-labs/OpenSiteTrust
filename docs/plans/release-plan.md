# Release Plan

Version: v0.02

## Sprint 0 (Setup)
- Scaffold repos, CI templates, docker-compose, env, docs.

## Sprint 1 (MVP Core)
- Implement scoring engine (rules + explanations) with unit tests.
- API endpoints: GET /v1/sites/{host}, GET /v1/sites/{host}/explain, POST /v1/votes.
- DB schema migration and connection pooling; in-memory cache via Redis.

## Sprint 2 (Web + Extension)
- Web detail page (score, radar, evidence); minimal forum (posts/comments/reactions).
- Browser extension (MV3) top bar, fetch + cache, quick vote flow.

## Sprint 3 (Stabilization)
- Auth (email) + JWT; rate limiting; moderation basics; logs/metrics dashboards.
- E2E tests; hardening (XSS/CSRF/validation); docs polish.

Exit criteria: PRD acceptance criteria met; OKR baselines instrumented.
