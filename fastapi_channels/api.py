from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Callable, Optional, Sequence, TypeVar, Union

from broadcaster import Broadcast, BroadcastBackend
from fastapi import APIRouter, FastAPI
from fastapi_channels.permission import AllowAny, BasePermission
from fastapi_channels.throttling import Throttle
from fastapi_channels.throttling.callback import default_identifier,ws_default_callback,ws_action_default_callback,http_default_callback
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import WebSocketRateLimiter
from redis.asyncio import Redis

ParentT = TypeVar("ParentT", APIRouter, FastAPI)

DEFAULT_QUERY_TOKEN_KEY = "token"
DEFAULT_COOKIE_TOKEN_KEY = "token"
# DEFAULT_PERMISSION_CLASSES = ("fastapi_channels.permissions.AllowAny",)
DEFAULT_PERMISSION_CLASSES = (AllowAny,)


class FastAPIChannel:
    """
    为fastapi-channels全局注册类变量，在使用Channel的时候部分变量没有指定将会使用这个
    """

    broadcast: Optional[Broadcast] = None
    throttle: Optional[Throttle] = None

    _new_broadcast: bool = False
    _new_limiter: bool = False
    # authentication
    query_token_key: Optional[str] = None
    cookie_token_key: Optional[str] = None
    permission_classes: Any = DEFAULT_PERMISSION_CLASSES
    # other
    pagination_class: Any = None
    throttle_classes: Optional[WebSocketRateLimiter] = None

    @classmethod
    async def init(
            cls,
            *,
            debug: bool = False,
            # broadcaster
            url: Optional[str] = None,
            backend: Optional[BroadcastBackend] = None,
            broadcast: Optional[Broadcast] = None,
            # fastapi-limiter
            limiter_url: Optional[str] = None,
            redis: Any = None,
            prefix: str = "fastapi-channel",
            identifier: Optional[Callable] = default_identifier,
            http_callback: Optional[Callable] = http_default_callback,
            ws_callback: Optional[Callable] = ws_default_callback,
            # other config
            permission_classes: Optional[
                Sequence[Union[BasePermission, str, bool, Callable]]
            ] = None,
            throttle_classes: Optional[WebSocketRateLimiter] = None,
            pagination_class: Any = None,
            # authentication
            query_token_key: Optional[str] = None,
            cookie_token_key: Optional[str] = None,
    ):
        cls.debug = debug

        if broadcast:
            cls.broadcast = broadcast
        else:

            cls.broadcast = Broadcast(url=url or limiter_url, backend=backend)
            cls._new_broadcast = True
        cls.permission_classes = permission_classes or cls.permission_classes
        cls.throttle_classes = throttle_classes or cls.throttle_classes
        cls.pagination_class = pagination_class or cls.pagination_class
        cls.throttle=Throttle(
            url=limiter_url or url
        )

        if not FastAPILimiter.redis:
            limiter_redis = redis or await Redis.from_url(limiter_url)
            _fastapi_limiter_init_additional_key = {}
            if identifier:
                _fastapi_limiter_init_additional_key["identifier"] = identifier
            if http_callback:
                _fastapi_limiter_init_additional_key["http_callback"] = http_callback
            await FastAPILimiter.init(
                redis=limiter_redis or url,
                prefix=prefix,
                ws_callback=ws_callback,
                **_fastapi_limiter_init_additional_key,
            )
            cls._new_limiter = True

        cls.query_token_key = query_token_key or DEFAULT_QUERY_TOKEN_KEY
        cls.cookie_token_key = cookie_token_key or DEFAULT_COOKIE_TOKEN_KEY
        await cls.broadcast.connect()

    @classmethod
    async def close(cls):
        if cls._new_broadcast:
            await cls.broadcast.disconnect()
        if cls._new_limiter:
            await FastAPILimiter.close()


def _add_exception_handlers(parent: ParentT):
    from fastapi_channels.exceptions import (
        WebSocketException,
        WebSocketExceptionHandler,
    )
    parent.add_exception_handler(WebSocketException, WebSocketExceptionHandler)  # type:ignore


def add_channel(
        parent: ParentT,
        *,
        add_exception_handlers: bool = True,
        # broadcaster
        url: Optional[str] = None,
        backend: Optional[BroadcastBackend] = None,
        broadcast: Optional[Broadcast] = None,
        # fastapi-limiter
        limiter_url: Optional[str] = None,
        redis=None,
        prefix: str = "fastapi-channel",
        identifier: Optional[Callable] = None,
        http_callback: Optional[Callable] = None,
        ws_callback: Callable = ws_default_callback,
        # other config
        permission_classes: Optional[
            Sequence[Union[BasePermission, str, bool, Callable]]
        ] = None,
        throttle_classes: Optional[WebSocketRateLimiter] = None,
        pagination_class: Any = None,
        # authentication
        query_token_key: Optional[str] = None,
        cookie_token_key: Optional[str] = None,
) -> ParentT:
    # router = parent.router if isinstance(parent, FastAPI) else parent  # type: ignore[attr-defined]
    # debug = parent.debug if isinstance(parent, FastAPI) else False
    if not isinstance(parent, FastAPI):
        raise ValueError("add_channel needs to be applied on FastAPI instances")
    # TODO: 按照fastapi-pagination的设想，这里区分FastAPi还是APIRouter目的在于更新 API 文档 之后我可能会专门实现能够支持BaseChannel和Channel的OpeAPI文档
    # TODO: 但是目前只是实现FastAPIChannel的全局注册
    router = parent.router  # type: ignore[attr-defined]
    debug = parent.debug  # type: ignore[attr-defined]
    _original_lifespan_context = router.lifespan_context

    @asynccontextmanager
    async def lifespan(app: Any) -> AsyncIterator[Any]:
        # 在原有的生命周期的基础上又追加了自己的生命周期 # 合并原来的生命周期
        try:
            await FastAPIChannel.init(
                debug=debug,
                url=url,
                backend=backend,
                broadcast=broadcast,
                limiter_url=limiter_url,
                redis=redis,
                prefix=prefix,
                identifier=identifier,
                http_callback=http_callback,
                ws_callback=ws_callback,
                permission_classes=permission_classes,
                throttle_classes=throttle_classes,
                pagination_class=pagination_class,
                query_token_key=query_token_key,
                cookie_token_key=cookie_token_key,
            )
            async with _original_lifespan_context(app) as maybe_state:
                yield maybe_state
        finally:
            await FastAPIChannel.close()

    router.lifespan_context = lifespan
    if add_exception_handlers:
        _add_exception_handlers(parent)
    return parent
