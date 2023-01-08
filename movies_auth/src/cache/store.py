from abc import ABC, abstractmethod


class CacheStore(ABC):
    @abstractmethod
    async def get(self):
        pass

    @abstractmethod
    async def set(self):
        pass

    @abstractmethod
    async def close(self):
        pass
