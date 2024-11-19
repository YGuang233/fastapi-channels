import time
from math import ceil
from typing import Annotated, Callable, Optional

from limits.aio.storage import MemoryStorage
from limits.aio.strategies import FixedWindowRateLimiter
from pydantic import Field

from ..base import (
    RateLimiter,
    ThrottleBackend,
    WebSocketRateLimiter,
    _RateLimitItemPerSecond,
)

_memory_storage = MemoryStorage()
_fixed_window = FixedWindowRateLimiter(_memory_storage)


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
    ) -> None:
        super().__init__(
            times, milliseconds, seconds, minutes, hours, identifier, callback
        )
        self.rate_limit = _RateLimitItemPerSecond(
            amount=self.times, multiples=ceil(self.milliseconds / 1000)
        )

    async def _check(self, key) -> int:
        if not await _fixed_window.hit(self.rate_limit, key):
            expiry_time = await _memory_storage.get_expiry(key)
            current_time = time.time()
            return int(expiry_time - current_time) * 1000
        return 0


class MemoryWebSocketRateLimiter(MemoryRateLimiter, WebSocketRateLimiter): ...


class MemoryThrottleBackend(ThrottleBackend):
    async def conn(self) -> None:
        pass

    async def reset(self):
        return await _memory_storage.reset()

    async def close(self) -> None:
        pass

    @property
    def ratelimiter(self) -> Callable:
        return MemoryRateLimiter

    @property
    def websocket_ratelimiter(self) -> Callable:
        return MemoryWebSocketRateLimiter
