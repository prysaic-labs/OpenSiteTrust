from __future__ import annotations
import os
import json
from typing import Any, Optional

try:
    from redis import asyncio as aioredis  # type: ignore
except Exception:
    aioredis = None  # optional

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "900"))

_redis = None


async def get_client():
    global _redis
    if aioredis is None:
        return None
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    return _redis


async def cache_get_json(key: str) -> Optional[Any]:
    client = await get_client()
    if not client:
        return None
    try:
        data = await client.get(key)
        if data:
            return json.loads(data)
    except Exception:
        return None
    return None


async def cache_set_json(key: str, value: Any, ttl: Optional[int] = None) -> None:
    client = await get_client()
    if not client:
        return
    try:
        await client.set(key, json.dumps(value), ex=ttl or CACHE_TTL_SECONDS)
    except Exception:
        pass
