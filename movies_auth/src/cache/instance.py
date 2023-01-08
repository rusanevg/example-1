from typing import Optional

from cache.store import CacheStore

cache_store: Optional[CacheStore] = None


async def get_cache_store() -> CacheStore:
    return cache_store
