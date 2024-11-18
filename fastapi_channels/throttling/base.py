from functools import lru_cache
from typing import Any, Callable, Optional, cast
from urllib.parse import urlparse

from fastapi_channels.throttling.ext._base import ThrottleBackend

# 决定使用那种限流器
# 决定使用哪个后端
# 决定使用在ws还是http


# slowapi支持多种后端，但只支持http
# fastapi-limiter直支持redis作为后端，但只支持http和ws
# slowapi还是不要想了，因为它是构建在中间件的:slowapi.middleware.py，但是它限流的过程还是可以抄一下的
@lru_cache
def _create_backend(url: str) -> ThrottleBackend:
    parsed_url = urlparse(url)
    if parsed_url.scheme == "memory":
        from .ext.memory import MemoryThrottleBackend

        return MemoryThrottleBackend(url=url)
    elif parsed_url.scheme == "redis":
        from .ext.fastapi_limiter import RedisThrottleBackend

        return RedisThrottleBackend(url=url)
    else:
        raise ValueError(f"Unsupported storage type: {parsed_url.scheme}")


class Throttle:
    url: Optional[str] = None
    backend: Optional[ThrottleBackend] = None
    storage = None
    prefix: Optional[str] = "fastapi-channel"
    identifier: Optional[Callable] = None
    http_callback: Optional[Callable] = None
    ws_callback: Optional[Callable] = None
    kwargs: dict = {}

    @classmethod
    async def init(
        cls,
        url: str,
        *,
        backend: Optional[ThrottleBackend] = None,
        storage: Any,
        prefix: str,
        identifier: Callable,
        http_callback: Callable,
        ws_callback: Callable,
        **kwargs,
    ) -> None:
        cls.url = url
        cls.storage = storage
        cls.prefix = prefix
        cls.identifier = identifier
        cls.http_callback = http_callback
        cls.ws_callback = ws_callback
        cls.kwargs = kwargs
        cls.backend = backend or _create_backend(cast(str, url))
        print("init:", cls.backend)
        await cls.backend.conn()

    @classmethod
    def params(cls):
        return {
            "url": cls.url,
            "storage": cls.storage,
            "prefix": cls.prefix,
            "identifier": cls.identifier,
            "http_callback": cls.http_callback,
            "ws_callback": cls.ws_callback,
            **cls.kwargs,
        }

    @classmethod
    async def conn(cls):
        await cls.backend.conn()

    @classmethod
    async def close(cls):
        await cls.backend.close()

    @classmethod
    def ratelimiter(cls) -> Callable:
        print("ratelimiter")
        print("ratelimiter:", cls.backend)

        return cls.backend.ratelimiter

    @classmethod
    def websocket_ratelimiter(cls) -> Callable:
        print("websocket_ratelimiter")
        return cls.backend.websocket_ratelimiter
