import aioredis
from typing import Optional, Union

from cache.store import CacheStore


class Redis(CacheStore):
    def __init__(self, host: str, port: int, minsize: int, maxsize: int):
        self.cache_store = None
        self.host = host
        self.port = port
        self.minsize = minsize
        self.maxsize = maxsize

    async def init(self):
        self.cache_store = await aioredis.create_redis_pool((self.host, self.port),
                                                            minsize=self.minsize, maxsize=self.maxsize)

    async def get(self, key: str) -> Optional[bytes]:
        return await self.cache_store.get(key=key) or None

    async def set(self, key: str, value: Union[bytes, str], expire: int) -> None:
        await self.cache_store.set(key=key, value=value, expire=expire)

    async def close(self):
        self.cache_store.close()
        await self.cache_store.wait_closed()
