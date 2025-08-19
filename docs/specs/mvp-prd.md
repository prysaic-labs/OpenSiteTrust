# MVP Product Requirements (PRD)

Version: v0.02
Status: Draft (Locked for MVP scope)

## 1. Goals
- Deliver an explainable 0–100 website trust/risk score with evidence cards.
- Provide a minimal web UI, REST API, and browser extension to consume scores.
- Enable community voting with basic anti-abuse and recompute impact on scores.

## 2. Non-Goals (MVP)
- Heavy LLM/agents, global crawling, large knowledge graphs, complex admin.
- External threat feeds integration, domain verification, multi-region workers.

## 3. Personas & Top Scenarios
- End user: sees color bar + score on any site; can view “why” and vote.
- Developer: queries scores and explanations via REST API.
- Site owner: can appeal.

## 4. Functional Scope
- Scoring engine
  - Rule-based S/C/T/U features; Wilson lower bound for community U.
  - Explanation output: list of signals with contributions.
  - Caching with TTL (5–15 minutes per host).
- API
  - GET /v1/sites/{host}: latest score and breakdown.
  - GET /v1/sites/{host}/explain: signals and contributions.
  - POST /v1/votes: label={safe|suspicious|danger}, reason optional; auth required.
- Web app
  - Site detail page: score, radar chart, evidence cards, vote distribution.
  - Minimal forum: posts, comments, reactions (like/dislike).
  - Auth (email/third-party acceptable stub) + rate limiting.
- Browser extension (MV3)
  - Top bar color + score, expand to show evidence, quick vote → auth flow.

## 5. Data Model
- See docs/data-model.sql for relational schema (PostgreSQL).

## 6. Acceptance Criteria
- API returns deterministic score for test fixtures; explanation includes signals.
- Voting updates U dimension; recomputed total reflects within 1 minute (worker or inline for MVP).
- Web shows correct breakdown and evidence; forum supports basic CRUD with rate limits.
- Extension displays bar and fetches score/explain with cache.
- Basic security: input validation, XSS-safe markdown, CSRF protection, JWT auth, rate limits.

## 7. Success Metrics (post-MVP)
- P95 API latency < 300ms (cache hit); availability ≥ 99.5%.
- Evidence card expand rate ≥ 40%; extension top-bar CTR ≥ 10%.

## 8. Release Gates
- Unit tests for scoring function (50+ fixtures, happy/edge cases).
- E2E: register → vote → recompute → query score; forum basic flows.
- Docs: README, API, deployment, privacy/security.
