# OpenSiteTrust API (MVP Bootstrap)

## Run locally
- Python 3.11+
- Install deps: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

Open http://localhost:8000/v1/sites/example.com

## Docker
- Build: `docker build -t ost-api .`
- Run: `docker run -p 8000:8000 ost-api`

## Endpoints
- GET /v1/sites/{host}
- GET /v1/sites/{host}/explain
- POST /v1/votes

Note: Auth is stubbed for MVP; provide `user` in body to simulate unique votes.
