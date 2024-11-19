import functools
import inspect
import warnings
from contextlib import asynccontextmanager, contextmanager
from typing import (
    Annotated,
    Any,
    AsyncContextManager,
    AsyncIterator,
    Callable,
    Generator,
    Mapping,
    Optional,
    Sequence,
)

from fastapi.types import DecoratedCallable
from starlette._utils import is_async_callable
from starlette.routing import _AsyncLiftContextManager
from starlette.websockets import WebSocket
from typing_extensions import Doc, deprecated  # noqa

from fastapi_channels.types import Lifespan


def _wrap_gen_lifespan_context(
    lifespan_context: Callable[[Any, Any], Generator[Any, Any, Any]],
) -> Callable[[Any], AsyncContextManager[Any]]:
    """同步上下文管理器转异步上下文管理器"""
    cmgr = contextmanager(lifespan_context)

    @functools.wraps(cmgr)
    def wrapper(websocket: Any, channel: Any) -> _AsyncLiftContextManager[Any]:
        return _AsyncLiftContextManager(cmgr(websocket, channel))

    return wrapper


def _merge_lifespan_context(
    original_context: Lifespan[Any, Any], nested_context: Lifespan[Any, Any]
) -> Lifespan[Any, Any]:
    """合并生命周期函数"""

    @asynccontextmanager
    async def merged_lifespan(
        websocket: WebSocket, channel: str
    ) -> AsyncIterator[Optional[Mapping[str, Any]]]:
        async with original_context(websocket, channel) as maybe_original_state:
            async with nested_context(websocket, channel) as maybe_nested_state:
                if maybe_nested_state is None and maybe_original_state is None:
                    yield None  # old ASGI compatibility
                else:
                    yield {**(maybe_nested_state or {}), **(maybe_original_state or {})}

    return merged_lifespan  # type: ignore[return-value]


class ChannelLifespanEvent:
    def __init__(
        self,
        on_join: Sequence[Callable[[WebSocket, str], Any]] | None = None,
        on_leave: Sequence[Callable[[WebSocket, str], Any]] | None = None,
        lifespan: Lifespan[Any, Any] | None = None,
    ):
        self.on_join = [] if on_join is None else list(on_join)
        self.on_leave = [] if on_leave is None else list(on_leave)
        if on_join or on_leave:
            if lifespan:
                warnings.warn(
                    "The `lifespan` parameter cannot be used with `on_join` or "
                    "`on_leave`. Both `on_join` and `on_leave` will be ignored.",
                    category=Warning,
                    stacklevel=4,
                )
        if lifespan is None:
            self.lifespan_context = self._default_lifespan
        elif inspect.isasyncgenfunction(lifespan):
            warnings.warn(
                "async generator function lifespans are deprecated, "
                "use an @contextlib.asynccontextmanager function instead",
                category=DeprecationWarning,
                stacklevel=4,
            )
            self.lifespan_context = asynccontextmanager(
                lifespan,  # type: ignore
            )
        elif inspect.isgeneratorfunction(lifespan):
            warnings.warn(
                "generator function lifespans are deprecated, "
                "use an @contextlib.asynccontextmanager function instead",
                category=DeprecationWarning,
                stacklevel=4,
            )
            self.lifespan_context = _wrap_gen_lifespan_context(
                lifespan,  # type: ignore
            )
        else:
            self.lifespan_context = lifespan

    def add_event_handler(
        self,
        event_type: str,
        func: Callable,
    ) -> None:  # pragma: no cover
        assert event_type in ("join", "leave")
        if event_type == "join":
            self.on_join.append(func)
        else:
            self.on_leave.append(func)

    async def join(self, websocket: WebSocket, channel: str) -> None:
        """
        Run any `.on_join` event handlers.
        """
        for handler in self.on_join:
            if is_async_callable(handler):
                await handler(websocket, channel)
            else:
                handler(websocket, channel)

    async def leave(self, websocket: WebSocket, channel: str) -> None:
        """
        Run any `.on_leave` event handlers.
        """
        for handler in self.on_leave:
            if is_async_callable(handler):
                await handler(websocket, channel)
            else:
                handler(websocket, channel)

    def on_event(
        self,
        event_type: Annotated[
            str,
            Doc(
                """
                The type of event. `join` or `leave`.
                """
            ),
        ],
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            self.add_event_handler(event_type, func)
            return func

        return decorator

    @asynccontextmanager
    async def _default_lifespan(self, websocket: WebSocket, channel: str):
        await self.join(websocket, channel)
        yield
        await self.leave(websocket, channel)

    # async def lifespan(self, websocket: WebSocket, channel: str) -> None:
    #     """
    #     Handle fastapi-channels channel lifespan messages, which allows us to manage application
    #     join and leave events.
    #     """
    #     print(websocket, channel)
    #     joined = False  # 是否执行join函数
    #     kwargs = {
    #         'websocket': websocket,
    #         'channel': channel,
    #     }
    #     # 默认如果是中间部分错误的话，结束不会被运行，除非你捕获了lifespan中的异常并使用finally的语句指定代码
    #     try:
    #         async with self.lifespan_context(websocket, channel):
    #             joined = True
    #             await self._handle(type="lifespan.join.complete", **kwargs)
    #     except BaseException:
    #         exc_text = traceback.format_exc()
    #         if joined:
    #             await self._handle(type="lifespan.leave.failed", message=exc_text, **kwargs)
    #         else:
    #             await self._handle(type="lifespan.join.failed", message=exc_text, **kwargs)
    #         raise
    #     else:
    #         await self._handle(type="lifespan.leave.complete", **kwargs)
