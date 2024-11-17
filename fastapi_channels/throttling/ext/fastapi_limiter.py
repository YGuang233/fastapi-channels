from importlib.metadata import version
from typing import Callable

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter, WebSocketRateLimiter
from packaging import version as pkg_version

from fastapi_channels.throttling import Throttle
from fastapi_channels.throttling.ext._base import ThrottleBackend

_current_version = version("fastapi-limiter")
_required_version = "0.1.6"

if pkg_version.parse(_current_version) > pkg_version.parse(_required_version):
    raise ImportError(
        f"fastapi-limiter version {_current_version} is higher than the required version {_required_version}. "
        "Please ensure compatibility with your application."
    )


class RedisThrottleBackend(ThrottleBackend):
    async def conn(self) -> None:
        if not FastAPILimiter.redis or not Throttle.redis:
            from redis.asyncio import Redis

            Throttle.redis = await Redis.from_url(self.url)
            await FastAPILimiter.init(
                redis=Throttle.redis,
                prefix=Throttle.prefix,
                identifier=Throttle.identifier,
                ws_callback=Throttle.ws_callback,
                http_callback=Throttle.http_callback,
            )
            self._new_backend1 = True
        else:
            await FastAPILimiter.init(redis=Throttle.redis)

    async def close(self) -> None:
        if self._new_backend1:
            await FastAPILimiter.close()

    @property
    def ratelimiter(self) -> Callable:
        return RateLimiter

    @property
    def websocket_ratelimiter(self) -> Callable:
        return WebSocketRateLimiter
