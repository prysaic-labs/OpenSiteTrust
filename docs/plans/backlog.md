# Prioritized Backlog (MVP)

MoSCoW Prioritization

## Must
- Scoring engine rules + explanations
- GET /v1/sites/{host}
- GET /v1/sites/{host}/explain
- POST /v1/votes + JWT auth + rate limits
- Site detail page (score, radar, evidence)
- Extension top bar + cache + quick vote
- DB schema + migrations; Redis cache

## Should
- Forum: posts/comments/reactions
- Appeal endpoint + simple review workflow
- Signed score snapshot

## Could
- API key for read queries
- Hot sites and controversial boards

## Won't (MVP)
- Heavy LLM/agents, global crawling, threat feeds integration
- Complex admin, multi-region workers, domain verification
