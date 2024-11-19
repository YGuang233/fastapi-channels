from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Annotated, Any, Callable, Optional, cast
from urllib.parse import urlparse

from fastapi import Request, Response
from limits import RateLimitItemPerSecond
from pydantic import Field
from starlette.websockets import WebSocket


class RateLimiter:
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
        self.times = times
        self.milliseconds = (
            milliseconds + 1000 * seconds + 60000 * minutes + 3600000 * hours
        )
        self.identifier = identifier
        self.callback = callback

    async def _check(self, key) -> int:
        raise NotImplementedError()

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
        identifier = self.identifier or Throttle.identifier
        callback = self.callback or Throttle.http_callback
        rate_key = await identifier(request)
        key = f"{Throttle.prefix}:{rate_key}:{route_index}:{dep_index}"

        pexpire = await self._check(key)
        if pexpire != 0:
            return await callback(request, response, pexpire)


class WebSocketRateLimiter(RateLimiter):
    async def __call__(self, ws: WebSocket, context_key="") -> None:
        identifier = self.identifier or Throttle.identifier
        rate_key = await identifier(ws)
        key = f"{Throttle.prefix}:ws:{rate_key}:{context_key}"

        pexpire = await self._check(key)
        if pexpire != 0:
            callback = self.callback or Throttle.ws_callback
            return await callback(ws, pexpire)


class ThrottleBackend(ABC):
    def __init__(
        self,
        url: str,
    ) -> None:
        self.url = url
        self._new_backend = (
            False  # 自己注册或调用第三方库注册了，默认自己处理关闭逻辑,否则就自己新建
        )

    @abstractmethod
    async def conn(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def reset(self) -> int:
        """
        resets the storage if it supports being reset
        """
        raise NotImplementedError()

    @abstractmethod
    async def close(self) -> None:
        """
        close the storage conn if it supports being close
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def ratelimiter(self) -> RateLimiter:
        raise NotImplementedError()

    @property
    @abstractmethod
    def websocket_ratelimiter(self) -> WebSocketRateLimiter:
        raise NotImplementedError()


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


class _RateLimitItemPerSecond(RateLimitItemPerSecond):
    def key_for(self, *identifiers: str) -> str:
        return identifiers[0]


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
        print("ratelimiter:", cls.backend)
        return cls.backend.ratelimiter

    @classmethod
    def websocket_ratelimiter(cls) -> Callable:
        return cls.backend.websocket_ratelimiter
