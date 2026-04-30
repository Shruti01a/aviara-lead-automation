import json
import hashlib
import redis
from app.config import REDIS_URL
from app.utils.logger import get_logger

logger = get_logger(__name__)

# try to connect, but don't crash if redis isn't running
try:
    r = redis.from_url(REDIS_URL, decode_responses=True)
    r.ping()
    logger.info("Redis connected")
except Exception:
    logger.warning("Redis not available - caching disabled")
    r = None


def make_key(prefix: str, data: dict) -> str:
    raw = json.dumps(data, sort_keys=True)
    hash_str = hashlib.md5(raw.encode()).hexdigest()
    return f"{prefix}:{hash_str}"


def get_cache(key: str):
    if r is None:
        return None
    try:
        val = r.get(key)
        return json.loads(val) if val else None
    except Exception:
        return None


def set_cache(key: str, value: dict, ttl: int = 3600):
    if r is None:
        return
    try:
        r.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.warning(f"Cache set failed: {e}")
