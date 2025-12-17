import json
import hashlib
from redis import Redis
from app.config import REDIS_URL, CACHE_TTL_SECONDS

redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

def _key(namespace: str, payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{namespace}:{digest}"

def cache_get(namespace: str, payload: dict) -> str | None:
    return redis_client.get(_key(namespace, payload))

def cache_set(namespace: str, payload: dict, value: str) -> None:
    redis_client.setex(_key(namespace, payload), CACHE_TTL_SECONDS, value)
