from importlib.metadata import version
from typing import Callable

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter, WebSocketRateLimiter
from packaging import version as pkg_version

from ..base import Throttle, ThrottleBackend

_current_version = version("fastapi-limiter")
_required_version = "0.1.6"

if pkg_version.parse(_current_version) > pkg_version.parse(_required_version):
    raise ImportError(
        f"fastapi-limiter version {_current_version} is higher than the required version {_required_version}. "
        "Please ensure compatibility with your application."
    )


class RedisThrottleBackend(ThrottleBackend):
    lua_script = FastAPILimiter.lua_script
    reset_lua_script = """
        local keys = redis.call('keys', ARGV[1])
        for i=1,#keys,5000 do
            redis.call('del', unpack(keys, i, math.min(i+4999, #keys)))
        end
        return #keys
        """

    async def conn(self) -> None:
        if not FastAPILimiter.redis:
            # 使用 fastapi-limiter 没有挂载redis且没有storage传入，
            # 则说明用户没有手动注册将会使用以下注册步骤
            if not Throttle.storage:
                from redis.asyncio import Redis

                Throttle.storage = await Redis.from_url(self.url)
                self._new_backend = True
            await FastAPILimiter.init(
                redis=Throttle.storage,
                prefix=Throttle.prefix,
                identifier=Throttle.identifier,
                ws_callback=Throttle.ws_callback,
                http_callback=Throttle.http_callback,
            )
        else:
            FastAPILimiter.ws_callback = Throttle.ws_callback  # 确保ws的返回

    async def close(self) -> None:
        if self._new_backend:
            await FastAPILimiter.close()

    async def reset(self):
        if not Throttle.storage or not Throttle.url.startswith("redis"):
            raise ValueError("Throttle storage is not set or URL is not a Redis URL.")
        deleted_count: int = await Throttle.storage.eval(  # noqa: F841
            self.reset_lua_script, keys=[], args=[f"{Throttle.prefix}*"]
        )

    @property
    def ratelimiter(self) -> Callable:
        return RateLimiter

    @property
    def websocket_ratelimiter(self) -> Callable:
        return WebSocketRateLimiter
