import asyncio
from typing import Annotated, Callable, Optional

from pydantic import Field
from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket

from .. import Throttle
from ._base import RateLimiter, ThrottleBackend


class MemoryRateLimiter(RateLimiter):
    def __init__(
        self,
        times: Annotated[int, Field(ge=0)] = 1,
        milliseconds: Annotated[int, Field(ge=-1)] = 0,
        seconds: Annotated[int, Field(ge=-1)] = 0,
        minutes: Annotated[int, Field(ge=-1)] = 0,
        hours: Annotated[int, Field(ge=-1)] = 0,
        identifier: Optional[Callable] = None,
        callback: Optional[Callable] = None,
    ):
        super().__init__(
            times, milliseconds, seconds, minutes, hours, identifier, callback
        )
        self._requests = {}  # 这样子的_request、locks和下面的是分开的
        self._locks = {}

    async def _reset(self, key):
        await asyncio.sleep(self.milliseconds / 1000)
        self._requests[key] = 0

    async def _check(self, key):
        if key not in self._requests:
            self._requests[key] = 0
            asyncio.create_task(self._reset(key))
        self._requests[key] += 1
        return self._requests[key] <= self.times

    async def __call__(self, request: Request, response: Response):
        route_index = 0
        dep_index = 0
        for i, route in enumerate(request.app.routes):
            if route.path == request.scope["path"] and request.method in route.methods:
                route_index = i
                for j, dependency in enumerate(route.dependencies):
                    if self is dependency.dependency:
                        dep_index = j
                        break
        # moved here because constructor run before app startup
        identifier = self.identifier or Throttle.identifier
        callback = self.callback or Throttle.http_callback
        rate_key = await identifier(request)
        key = f"{Throttle.prefix},{rate_key}:{route_index}:{dep_index}"

        if key not in self._locks:
            self._locks[key] = asyncio.Lock()

        async with self._locks[key]:
            is_allowed = await self._check(key)

        if not is_allowed:
            return await callback(request, response)


class MemoryWebSocketRateLimiter(MemoryRateLimiter):
    async def __call__(self, ws: WebSocket, context_key="") -> None:
        identifier = self.identifier or Throttle.identifier
        rate_key = await identifier(ws)
        key = f"{Throttle.prefix}:ws:{rate_key}:{context_key}"
        pexpire = await self._check(key)
        callback = self.callback or Throttle.ws_callback
        if pexpire != 0:
            return await callback(ws, pexpire)


class MemoryThrottleBackend(ThrottleBackend):
    async def conn(self) -> None:
        pass

    async def close(self) -> None:
        pass

    @property
    def ratelimiter(self) -> Callable:
        return MemoryRateLimiter

    @property
    def websocket_ratelimiter(self) -> Callable:
        return MemoryWebSocketRateLimiter
