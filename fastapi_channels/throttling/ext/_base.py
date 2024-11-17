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
    ):
        self.times = times
        self.milliseconds = (
            milliseconds + 1000 * seconds + 60000 * minutes + 3600000 * hours
        )
        self.identifier = identifier
        self.callback = callback

    async def __call__(
        self, request: Request, response: Response, prefix: Optional[str] = None
    ):
        raise NotImplementedError


class WebSocketRateLimiter(RateLimiter):
    async def __call__(
        self, ws: WebSocket, context_key="", prefix: Optional[str] = None
    ):
        raise NotImplementedError


class ThrottleBackend:
    def __init__(
        self,
        url: str,
    ) -> None:
        self.url = url
        self._new_backend1 = False  # 自己关闭
        self._new_backend2 = False  # 调用第三方库的关闭

    async def conn(self) -> None:
        raise NotImplementedError()

    async def close(self) -> None:
        raise NotImplementedError()

    @property
    def ratelimiter(self) -> Callable:
        raise NotImplementedError

    @property
    def websocket_ratelimiter(self) -> Callable:
        raise NotImplementedError
