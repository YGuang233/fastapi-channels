import asyncio
from typing import Callable

from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket

from .. import Throttle
from ._base import RateLimiter, ThrottleBackend

_requests = {}
_locks = {}


class MemoryRateLimiter(RateLimiter):
    async def _reset(self, key):
        await asyncio.sleep(self.milliseconds / 1000)
        _requests[key] = 0

    async def _check(self, key):
        if key not in _requests:
            _requests[key] = 0
            asyncio.create_task(self._reset(key))
        _requests[key] += 1
        return _requests[key] <= self.times

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

        if key not in _locks:
            _locks[key] = asyncio.Lock()

        async with _locks[key]:
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
