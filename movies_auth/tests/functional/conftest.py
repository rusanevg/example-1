import asyncio
import typing
import aiohttp
import json
import pytest_asyncio
from dataclasses import dataclass
from multidict import CIMultiDictProxy

main_headers = {
    'Content-type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest_asyncio.fixture(scope="session", name="event_loop")
def fixture_event_loop() -> typing.Generator[asyncio.AbstractEventLoop, typing.Any, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture
def api_request(session):
    async def inner(method, path, body=None, headers=dict()):
        url = f"http://test-flask:5000/api/v1/auth{path}"
        async with session.request(method=method, url=url, data=json.dumps(body),
                                   headers=dict(main_headers, **headers)) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner
