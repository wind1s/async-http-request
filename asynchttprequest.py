"""
Provides functionality to make async http requests.
"""
from typing import Optional, Any, Iterable, Callable, Union
from itertools import islice
from asyncio import ensure_future, sleep, run
from aiohttp import ClientSession

ParseRequest = Callable[ClientSession, Any]


class AsyncRequest:
    """
    Wrapper class for storing request data and sending async request.
    """

    def __init__(self, method: str, url: str, **kwargs: Any):
        self.__data: dict[str, str] = {"method": method, "url": url, **kwargs}

    @property
    def method(self) -> str:
        return self.__data["method"]

    @property
    def url(self) -> str:
        return self.__data["url"]

    def get(self, key: str) -> str:
        return self.__data[key]

    def set(self, key: str, value: Any) -> None:
        self.__data[key] = value

    def __getitem__(self, key: str) -> str:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    async def send(self, session: ClientSession, **extra_data: Any) -> str:
        async with session.request(**self.__data, **extra_data) as response:
            response.raise_for_status()
            return await response.read()


async def limited_as_completed(coros: Iterable[Any], limit: int) -> Iterable[Any]:
    """
    Runs a limited amount of coroutines at a time. Runs a new coroutine when one finishes.
    """
    futures = [ensure_future(c) for c in islice(coros, 0, limit)]
    push_future = futures.append
    remove_future = futures.remove

    while futures:
        await sleep(0)

        for fut in futures:
            if fut.done():
                remove_future(fut)
                next_fut = next(coros, None)

                # If next returns the default value None, there is no more coroutines to run.
                if next_fut is not None:
                    push_future(ensure_future(next_fut))

                await fut


def run_async_requests(
    requests_data: Iterable[Any],
    process_request: Union[ParseRequest, Iterable[ParseRequest]],
    base_url: Optional[str] = None,
    limit: int = 1000,
) -> None:
    """
    Creates coroutines for all requests and runs them async.
    """

    async def launch():
        async with ClientSession(base_url=base_url) as session:
            if isinstance(process_request, Iterable):
                coros = (proc(session, data) for proc, data in zip(process_request, requests_data))
            else:
                coros = (process_request(session, data) for data in requests_data)

            return await limited_as_completed(coros, limit)

    run(launch())
