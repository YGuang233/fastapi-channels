from abc import ABC, abstractmethod
from typing import Annotated, Callable, Optional

from fastapi import Request, Response
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

    async def __call__(self, request: Request, response: Response) -> None:
        raise NotImplementedError


class WebSocketRateLimiter(RateLimiter):
    async def __call__(self, ws: WebSocket, context_key="") -> None:
        raise NotImplementedError


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
    async def reset(self):
        """
        resets the storage if it supports being reset
        """
        raise NotImplementedError()

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError()

    @property
    @abstractmethod
    def ratelimiter(self) -> Callable:
        print("ratelimiter backend")
        raise NotImplementedError

    @property
    @abstractmethod
    def websocket_ratelimiter(self) -> Callable:
        raise NotImplementedError
