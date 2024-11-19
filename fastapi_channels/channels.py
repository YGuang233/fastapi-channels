import asyncio
import json
import traceback
import warnings
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
)

import anyio
from fastapi.params import Depends
from fastapi.types import DecoratedCallable
from fastapi_limiter.depends import WebSocketRateLimiter

# from fastapi_channels.throttling.ext._base import WebSocketRateLimiter
# 这个应该是WebSocketRateLimiter类型的指向，这个文件内不应该使用WebSocketRateLimiter的操作
from starlette._exception_handler import _lookup_exception_handler
from starlette._utils import is_async_callable
from starlette.concurrency import run_in_threadpool
from starlette.websockets import WebSocket
from typing_extensions import Annotated, Doc, Literal  # noqa

from fastapi_channels.api import FastAPIChannel
from fastapi_channels.exceptions import (
    ActionIsDeprecated,
    ActionNotExist,
    PermissionDenied,
    WebSocketException,
    WebSocketExceptionHandler,
)
from fastapi_channels.lifespan import ChannelLifespanEvent
from fastapi_channels.metaclssses import ActionConsumerMeta
from fastapi_channels.permission import BasePermission
from fastapi_channels.types import Lifespan


class BaseChannel:
    """
    基础BaseChannel只实现:
        1. 房间构建
        2. 消息处理
        3. 事件：加入房间和退出房间
        4. 请求限速
        5. 基础的用户验证
        6. 错误返回
        7. 聊天记录的保存(*可选)(后续实现)
    """

    # # # - base room settings    - # # #
    # - base room connect settings    - #
    channel: str = "default_channel"

    # - base room Can be instantiated settings    - #
    # room
    max_connection: Optional[int] = None
    # encoding: Optional[str] = None  # May be "text", "bytes", or "json".
    # 默认编码方式，对应直接调用encode和decode的处理方式
    on_join: Optional[Sequence[Callable[[], Any]]] = None
    on_leave: Optional[Sequence[Callable[[], Any]]] = None
    lifespan: Optional[Lifespan] = None
    # limiter
    history_key: str = f"history:{channel}"
    max_history: Optional[int] = None
    limiter_depends: Optional[List] = None
    # recent message
    timedelta: Optional[int] = None
    # permission
    permission_classes: Union[List, Tuple, BasePermission, Callable, bool, None] = (
        FastAPIChannel.permission_classes
    )
    throttle_classes: Optional[WebSocketRateLimiter] = FastAPIChannel.throttle_classes

    def __init__(
        self,
        *,
        channel: Optional[str] = None,
        max_connection: Optional[int] = None,
        history_key: Optional[str] = None,
        max_history: Optional[int] = None,
        limiter_depends: Optional[List] = None,
        permission_classes: Union[
            List, Tuple, BasePermission, Callable, bool, None
        ] = None,
        throttle_classes: Optional[WebSocketRateLimiter] = None,
        on_join: Optional[Sequence[Callable[[], Any]]] = None,
        on_leave: Optional[Sequence[Callable[[], Any]]] = None,
        lifespan: Optional[Lifespan] = None,
    ):
        self._exc_handlers = {}
        assert lifespan is None or (
            on_join is None and on_leave is None
        ), "Use either 'lifespan' or 'on_join'/'on_leave', not both."
        self.permission_classes = permission_classes or self.permission_classes
        self.limiter_depends = limiter_depends or self.limiter_depends
        self.max_history = max_history or self.max_history
        self.history_key = history_key or self.history_key
        self.max_connection = max_connection or self.max_connection
        self.channel = channel or self.channel
        if not isinstance(self.permission_classes, List):
            if isinstance(self.permission_classes, Tuple):
                self.permission_classes = list(self.permission_classes)
            else:
                self.permission_classes = [self.permission_classes]
        self.event_manage = ChannelLifespanEvent(
            on_join=on_join or self.on_join,
            on_leave=on_leave or self.on_leave,
            lifespan=lifespan or self.lifespan,
        )
        self.throttle_classes = throttle_classes or self.throttle_classes

    async def connect(
        self, websocket: WebSocket, channel: Optional[str] = None
    ) -> None:
        channel = channel or self.channel
        await websocket.accept()
        self._exc_handlers, status_handlers = websocket.scope.get(
            "starlette.exception_handlers"
        )
        if self.max_connection is not None and self.max_connection > 0:
            await self.check_connection_count(channel)
        await self.check_permission_classes(websocket)
        await self._lifespan(websocket, channel)

    async def disconnect(self, websocket: WebSocket) -> None:
        await websocket.close()

    async def close(self, websocket: WebSocket) -> None:
        await websocket.close()

    async def broadcast_to_personal(self, websocket: WebSocket, message: Any) -> None:
        """
        @example:
            ```
            class AChannel(Channel):
                @action(name='open')
                async def open_action(self,websocket:Websocket,channel:str):
                    await self.broadcast_to_personal(websocket, 'Hello, Channel!')
            ```
            ```
            channel=Channel()

            @channel.action(name='open')
            async def open_action(self,websocket:Websocket,channel:str):
                await channel.broadcast_to_personal(websocket, 'Hello, Channel!')
            ```
        """
        await websocket.send_text(await self.encode(message))

    async def broadcast_to_channel(self, channel: str, message: Any) -> None:
        """
        @example:
            ```
            class AChannel(Channel):
                @action(name='open')
                async def open_action(self,websocket:Websocket,channel:str,data:dict):
                    await self.broadcast_to_channel(channel, 'Hello, Channel!')
            ```
            ```
            channel=Channel()

            @channel.action(name='open')
            async def open_action(self,websocket:Websocket,channel:str,data:dict):
                await channel.broadcast_to_channel(channel, 'Hello, Channel!')
            ```
        """
        await FastAPIChannel.broadcast.publish(
            channel=channel, message=await self.encode(message)
        )

    @staticmethod
    async def send_error(error_msg: Any, close: bool = False) -> None:
        raise WebSocketException(error_msg=error_msg, close=close)

    async def _handle_exception(self, task, websocket: WebSocket, channel: str):
        try:
            await task
        except Exception as exc:
            handler = None
            if handler is None:
                handler = _lookup_exception_handler(self._exc_handlers, exc)
            if handler is None:
                raise exc
            handler = cast(WebSocketExceptionHandler, handler)
            if is_async_callable(handler):
                await handler(websocket, exc)
            else:
                await run_in_threadpool(handler, websocket, exc)

    async def _handle(self, type: str, message: Optional[str] = None, **kwargs):
        if type == "lifespan.join.complete":
            return await self._connect(
                websocket=kwargs.get("websocket"), channel=kwargs.get("channel")
            )
        if type == "lifespan.join.failed":
            pass
        if type == "lifespan.leave.complete":
            pass
        if type == "lifespan.leave.failed":
            pass

    async def _lifespan(self, websocket: WebSocket, channel: str) -> None:
        """
        Handle fastapi-channels channel lifespan messages, which allows us to manage application
        join and leave events.
        """
        joined = False  # 是否执行join函数
        kwargs = {
            "websocket": websocket,
            "channel": channel,
        }
        # 默认如果是中间部分错误的话，结束不会被运行，除非你捕获了lifespan中的异常并使用finally的语句指定代码
        try:
            async with self.event_manage.lifespan_context(websocket, channel):
                joined = True
                await self._handle(type="lifespan.join.complete", **kwargs)
        except BaseException:
            exc_text = traceback.format_exc()
            if joined:
                await self._handle(
                    type="lifespan.leave.failed", message=exc_text, **kwargs
                )
            else:
                await self._handle(
                    type="lifespan.join.failed", message=exc_text, **kwargs
                )
            raise
        else:
            await self._handle(type="lifespan.leave.complete", **kwargs)

    async def _connect(self, websocket: WebSocket, channel: str) -> None:
        async with anyio.create_task_group() as task_group:
            # run until first is complete
            async def run_chatroom_ws_receiver() -> None:
                try:
                    await self._receiver(websocket=websocket, channel=channel)
                except (
                    RuntimeError
                ):  # 客户端直接断开连接诱发的异常(websocket.accept() first)
                    pass
                task_group.cancel_scope.cancel()

            task_group.start_soon(run_chatroom_ws_receiver)
            await self._sender(websocket=websocket, channel=channel)

    async def _receiver(self, websocket: WebSocket, channel: str):
        """接收信息"""
        async for message in websocket.iter_text():

            async def _task(_message=message):
                if self.throttle_classes is not None:
                    await self.throttle_classes(websocket, channel)
                await self.receiver(websocket, channel, _message)

            await self._handle_exception(
                task=_task(),
                websocket=websocket,
                channel=channel,
            )

    async def receiver(self, websocket: WebSocket, channel: str, message: Any):
        await self.broadcast_to_channel(channel, message)

    async def _sender(self, websocket: WebSocket, channel: str):
        """发送信息"""
        async with FastAPIChannel.broadcast.subscribe(channel=channel) as subscriber:
            async for event in subscriber:
                await websocket.send_text(event.message)

    async def get_permissions(self, action: Optional[str] = None, **kwargs) -> List:
        """
        获取需要验证的权限列表
        Args:
            action: 对应的action
            **kwargs:

        Returns:

        """
        if action:
            # BaseChannel不对action做处理，你应该使用Channel类
            warnings.warn(
                "BaseChannel class does not handle actions,You should use the Channel class.",
                category=Warning,
                stacklevel=1,
            )
        return self.permission_classes

    # async def get_authenticators(self):
    #     """
    #     Instantiates and returns the list of authenticators that this view can use.
    #     雾：不知道这个现在怎么改用
    #     """
    #     return [auth() for auth in self.authentication_classes]
    # async def get_permissions(self):
    #     """
    #     Instantiates and returns the list of permissions that this view requires.
    #     """
    #     return [permission() for permission in self.permission_classes]
    # async def get_throttles(self):
    #     """
    #     Instantiates and returns the list of throttles that this view uses.
    #     雾：不知道这个现在怎么改用
    #     """
    #     return [throttle() for throttle in self.throttle_classes]

    async def check_permission_classes(self, websocket: WebSocket) -> None:
        """只检查permission_classes的权限认证"""
        for permission in await self.get_permissions(action=None):
            if (
                await self._check_permission(
                    websocket=websocket, action=None, permission=permission
                )
                is False
            ):
                raise PermissionDenied(close=True)

    @staticmethod
    async def _check_permission(
        websocket: WebSocket, action: Optional[str], permission: Any, **kwargs
    ) -> bool:
        if permission is None:
            return True
        elif isinstance(permission, type) and issubclass(permission, BasePermission):
            return await permission().has_permission(
                websocket=websocket, action=action, **kwargs
            )
        elif callable(permission):
            if asyncio.iscoroutinefunction(permission):
                return await permission(websocket, action, permission, **kwargs)
            return permission(websocket, action, permission, **kwargs)
        return False

    async def get_connection_count(self, channel: str) -> int:
        """
        获取当前房间连接的人数
        """
        return len(FastAPIChannel.broadcast._subscribers.get(channel, set()))  # type: ignore

    async def check_connection_count(self, channel: str) -> int:
        """
        如果当前人数大于房间设置的上限人数就退出，否则返回当前房间人数
        """
        current_conn_nums = await self.get_connection_count(channel)
        if self.max_connection is None or current_conn_nums < self.max_connection:
            return current_conn_nums
        await self.send_error(
            error_msg="The current number of channel connections is greater than the maximum number of connections",
            close=True,
        )

    @staticmethod
    async def encode_json(data: dict) -> str:
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    async def decode_json(message: str) -> dict:
        return json.loads(message)

    async def encode(self, data: Any):
        return await self.encode_json(data)

    async def decode(self, message: Any) -> dict:
        return await self.decode_json(message)

    def on_event(self, event_type: str) -> DecoratedCallable:
        return self.event_manage.on_event(event_type)

    def add_event_handler(
        self,
        event_type: str,
        func: Callable,
    ) -> None:  # pragma: no cover
        self.event_manage.add_event_handler(event_type, func)


class Channel(BaseChannel, metaclass=ActionConsumerMeta):
    """
    Channel在 BaseChannel 的基础上又实现:
        1. 通过action装饰器解析处理用户发送的数据包,同时可以在原有的权限基础上进行权限认证
        2. 通过limiter装饰器(需要先注册action装饰器),可对单个类型的action进行限流
    """

    def __init__(
        self,
        *,
        channel: Optional[str] = None,
        max_connection: Optional[int] = None,
        history_key: Optional[str] = None,
        max_history: Optional[int] = None,
        limiter_depends: Optional[List] = None,
        permission_classes: Optional[List] = None,
        throttle_classes: Optional[WebSocketRateLimiter] = None,
        on_join: Optional[Sequence[Callable[[], Any]]] = None,
        on_leave: Optional[Sequence[Callable[[], Any]]] = None,
        lifespan: Optional[Lifespan] = None,
    ):
        super().__init__(
            channel=channel,
            max_connection=max_connection,
            history_key=history_key,
            max_history=max_history,
            limiter_depends=limiter_depends,
            permission_classes=permission_classes,
            throttle_classes=throttle_classes,
            on_join=on_join,
            on_leave=on_leave,
            lifespan=lifespan,
        )

        if not hasattr(self, "_actions"):
            self._actions: Dict[str, tuple] = {}

    async def receiver(self, websocket: WebSocket, channel: str, message: Any):
        data: dict = await self.decode(message)
        return (
            await self.handle_action(
                action=data.get("action", None),
                request_id=int(data.get("request_id", 1)),
                data=data,
                websocket=websocket,
                channel=channel,
            ),
        )

    @property
    def actions(self) -> List[str]:
        return list(self._actions.keys())

    async def handle_action(
        self,
        websocket: WebSocket,
        channel: str,
        action: str,
        request_id: int,
        data: dict,
        **kwargs,
    ) -> None:
        if action not in self.actions:
            raise ActionNotExist(request_id=request_id, close=False)
        await self.check_permissions(websocket=websocket, action=action, **kwargs)
        action_func_or_str, _ = self._actions[action]
        if isinstance(action_func_or_str, str):
            await getattr(self, action_func_or_str)(
                websocket=websocket, channel=channel, data=data
            )
        else:
            await action_func_or_str.call(
                websocket=websocket, channel=channel, data=data
            )

    def action(
        self,
        name: Optional[str] = None,
        *,
        permission: Optional[Any] = None,
        detached: bool = False,
        deprecated: bool = False,
        dependencies: Annotated[
            Optional[Sequence[Depends]],
            Doc(
                """
                    A list of dependencies (using `Depends()`) to be used for this Action.

                    Read more about it in the
                    [FastAPI docs for Action](https://fc.bxzdyg.cn/learn/action).
                """
            ),
        ] = None,  # TODO: 以后改成我自己的文档地址，这里先不动
    ) -> DecoratedCallable:
        if detached:
            raise NotImplementedError(
                "Sorry, the detached function has not been implemented yet and is currently only used for placeholder"
            )

        def decorator(func):
            _name = name if name else func.__name__
            func.action = (_name, func.__doc__)
            perm_desc = "Allow Anyone"
            if isinstance(permission, type) and issubclass(permission, BasePermission):
                perm_desc = permission.__doc__ or permission.has_permission.__doc__
            elif callable(permission):
                perm_desc = permission.__doc__
            elif isinstance(permission, bool):
                if not permission:
                    perm_desc = "Not Allow Anyone"
            func.permission = (permission, perm_desc)

            @wraps(func)
            async def wrapper(*args, **kwargs):
                if deprecated:
                    raise ActionIsDeprecated(
                        error_msg=f"The function '{_name}' is deprecated."
                    )
                return await func(*args, **kwargs)

            wrapper.action = func.action
            wrapper.call = wrapper
            self._actions[_name] = (wrapper, permission)
            return wrapper

        return decorator

    async def get_permissions(self, action: Optional[str] = None, **kwargs) -> List:
        """
        获取需要验证的权限列表
        Args:
            action: 对应的action
            **kwargs:

        Returns:

        """
        _, perm_call = self._actions.get(action, (None, None))
        if perm_call is not None:
            if not isinstance(perm_call, List):
                if isinstance(perm_call, Tuple):
                    perm_call = list(perm_call)
                else:
                    perm_call = [perm_call]
            return self.permission_classes + perm_call
        return self.permission_classes

    async def check_permissions(
        self, websocket: WebSocket, action: str = None, **kwargs
    ) -> None:
        """检查permission_classes的权限认证和对应action的权限认证"""
        for permission in await self.get_permissions(action=action):
            if (
                await self._check_permission(
                    websocket=websocket, action=action, permission=permission, **kwargs
                )
                is False
            ):
                raise PermissionDenied(close=False)
