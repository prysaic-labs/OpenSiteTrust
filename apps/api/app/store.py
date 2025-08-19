from __future__ import annotations
from typing import Dict, List

# Simple in-memory store for MVP bootstrap only. Kept for fallback/testing.
# host -> user -> vote
VOTES: Dict[str, Dict[str, dict]] = {}


def add_vote(host: str, user: str, vote: dict):
    users = VOTES.setdefault(host, {})
    users[user] = vote  # unique (host,user)


def get_votes(host: str) -> List[dict]:
    return list(VOTES.get(host, {}).values())
