"""
Redis client manager with resilient in-memory fallback.
"""

import logging
import time
from typing import Any, Dict, Optional, Union
import json

from app.core.config import settings

logger = logging.getLogger("app.core.redis")


class MemoryCache:
    """In-memory fallback cache implementing core Redis key-value operations."""

    def __init__(self) -> None:
        self._store: Dict[str, tuple[str, Optional[float]]] = {}

    async def get(self, key: str) -> Optional[str]:
        item = self._store.get(key)
        if not item:
            return None
        val, expiry = item
        if expiry and time.time() > expiry:
            del self._store[key]
            return None
        return val

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        expiry = (time.time() + ex) if ex else None
        self._store[key] = (str(value), expiry)
        return True

    async def delete(self, key: str) -> int:
        if key in self._store:
            del self._store[key]
            return 1
        return 0

    async def exists(self, key: str) -> bool:
        val = await self.get(key)
        return val is not None


class RedisManager:
    """Manages Redis connection or gracefully falls back to memory cache."""

    def __init__(self) -> None:
        self._client: Optional[Any] = None
        self._fallback = MemoryCache()
        self._is_connected = False

    async def connect(self) -> None:
        if settings.REDIS_ENABLED and settings.REDIS_URL:
            try:
                import redis.asyncio as aioredis

                self._client = aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                )
                await self._client.ping()
                self._is_connected = True
                logger.info("Successfully connected to Redis instance at %s", settings.REDIS_URL)
            except Exception as err:
                logger.warning(
                    "Could not connect to Redis (%s). Operating in in-memory fallback mode.",
                    str(err),
                )
                self._is_connected = False
        else:
            self._is_connected = False

    async def close(self) -> None:
        if self._client and self._is_connected:
            await self._client.aclose()

    @property
    def client(self) -> Union[Any, MemoryCache]:
        if self._is_connected and self._client:
            return self._client
        return self._fallback

    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        raw = await self.client.get(key)
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                return None
        return None

    async def set_json(self, key: str, data: Any, expire_seconds: Optional[int] = 300) -> bool:
        raw = json.dumps(data, default=str)
        return await self.client.set(key, raw, ex=expire_seconds)


redis_manager = RedisManager()


def get_redis_client() -> Union[Any, MemoryCache]:
    return redis_manager.client
