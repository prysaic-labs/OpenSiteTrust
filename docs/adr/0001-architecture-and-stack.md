# ADR 0001: Architecture and Tech Stack

Status: Accepted
Date: 2025-08-17
Version: v0.02

## Decision
- Default deployment model: containerized (Docker Compose for dev).
- API: FastAPI (Python)
- Web: Next.js (React)
- Worker: Celery (Python)
- DB: PostgreSQL
- Cache/Rate limit/Queue: Redis
- Proxy: Caddy or Nginx; CDN/WAF: Cloudflare

## Rationale
- FastAPI provides excellent performance, typing, and ecosystem for Python-based scoring.
- Python suits the scoring engine and future data/ML extensions.
- Next.js offers SSR/ISR and strong DX for dashboard and detail pages.
- Celery integrates well with Python stack for async recompute and tasks.
- Postgres + Redis is a reliable, common baseline enabling transactions + caching/queues.

## Consequences
- Single-language backend (Python) reduces complexity.
- Node.js present only for web build/runtime (Next.js).
- Clear path to scale: split API/Worker, managed DB/Redis.
