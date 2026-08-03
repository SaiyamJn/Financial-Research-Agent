# backend/app/utils/cache.py
import json
from typing import Optional
import redis.asyncio as redis
from ..config import settings

_redis: Optional[redis.Redis] = None
_redis_disabled = False


def _cache_enabled() -> bool:
    return bool(settings.REDIS_URL and settings.REDIS_URL.strip())


def get_redis() -> Optional[redis.Redis]:
    """
    Returns a globally reused Redis async client, or None if Redis is disabled/unavailable.
    """
    global _redis, _redis_disabled
    if _redis_disabled or not _cache_enabled():
        return None
    if _redis is None:
        try:
            _redis = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=1,
            )
        except Exception:
            _redis_disabled = True
            return None
    return _redis


async def get_cached(key: str) -> Optional[dict]:
    r = get_redis()
    if r is None:
        return None
    try:
        v = await r.get(key)
    except Exception as e:
        # Don't keep retrying a bad host (e.g. docker hostname "redis" on Render)
        global _redis_disabled
        _redis_disabled = True
        print(f"⚠️ Cache read error (continuing): {e}")
        return None

    if not v:
        return None

    try:
        return json.loads(v)
    except Exception:
        return None


async def set_cached(key: str, value: dict, expire: int = 300):
    r = get_redis()
    if r is None:
        return
    try:
        await r.set(key, json.dumps(value, default=str), ex=expire)
    except Exception:
        global _redis_disabled
        _redis_disabled = True


async def close_redis():
    """
    Closes Redis gracefully.
    (Avoids crash if Redis not initialized)
    """
    global _redis
    if _redis is not None:
        try:
            await _redis.close()
        except Exception:
            pass
        _redis = None
