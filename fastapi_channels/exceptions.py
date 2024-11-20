import json
from typing import Any, Dict, Optional, Union

from fastapi import WebSocket
from fastapi.exceptions import WebSocketException as FastAPIWebSocketException
from typing_extensions import Annotated, Doc  # noqa
from websockets.frames import CloseCode  # noqa


class WebSocketException(FastAPIWebSocketException):
    code = CloseCode.NORMAL_CLOSURE
    status = "bad"
    reason = "disconnect error"

    def __init__(
        self,
        code: Annotated[
            Optional[int],
            Doc(
                """
                A closing code from the
                [valid codes defined in the specification](https://datatracker.ietf.org/doc/html/rfc6455#section-7.4.1).
                """
            ),
        ] = None,
        reason: Annotated[
            Optional[str],
            Doc(
                """
                The reason to close the WebSocketType connection.

                It is UTF-8-encoded data. The interpretation of the reason is up to the
                application, it is not specified by the WebSocketType specification.

                It could contain text that could be human-readable or interpretable
                by the client code, etc.
                """
            ),
        ] = None,
        *,  # 后面都是我自己加的
        close: Annotated[
            Optional[bool],
            Doc(
                """
                Close determines whether the exception raise will close the current connection.
                When 'close' is True, the parameters of 'reason' and 'code' will only be used
                """
            ),
        ] = True,  # close决定抛出的这个异常关不关闭当前的连接。 close为True时`reason`和`code`的参数才会被用上
        status: Annotated[
            Union[str, int, None],
            Doc(
                """
                The response status sent to the frontend for the websocket connection.
                It can be data of type int or str, of course, you can define the status according to
                your preferences or project needs. If you do not fill in the status, the default 'bad' will be used`
                """
            ),
        ] = None,  # 为websocket连接向前端发送的响应状态。可以为 int或str类型的数据，当然你可以根据自己的喜好或者项目的需求来定义status不填入则采用默认的`bad`
        error_msg: Annotated[
            Optional[Any],
            Doc(
                """
                Error messages will be added to the response packet.
                If 'error msg' is not filled in and only 'reason' is specified, then 'reason'
                will be used as the value of 'error msg'
                """
            ),
        ] = None,  # 错误信息，将添加在响应的数据包中。如果没有填入`error_msg`只指定了`reason`,那么`reason`将作为`error_msg`的值
        data: Annotated[
            Any,
            Doc(""" Can be used to store additional information """),
        ] = None,  # 可用来存储额外的信息
        request_id: Annotated[
            Optional[int],
            Doc(
                """ The sequential identifier of the requested multiple data segments """
            ),
        ] = None,  # 请求的多段数据的顺序标识符
        **kwargs: Annotated[
            Optional[Dict[str, Any]],
            Doc(
                """ Additional parameters will be added to the outermost layer of the data response body """
            ),
        ],  # 额外参数,将在在数据响应体的最外层添加上去
    ) -> None:  # code必须传入
        _code = code or self.code
        _reason = reason or self.reason
        super().__init__(code=_code, reason=_reason)
        self.close = close
        self.error_msg = error_msg or _reason
        self.data = data
        self.request_id = request_id
        self.status = status or self.status
        self.kwargs = kwargs


class PermissionDenied(WebSocketException):
    """权限不足"""

    code = CloseCode.PROTOCOL_ERROR
    reason = "Permission Denied"


class RateLimitExceeded(WebSocketException):
    """请求上限"""

    code = CloseCode.PROTOCOL_ERROR
    reason = "Too Many Request"


class ActionNotExist(WebSocketException):
    """action不存在"""

    code = CloseCode.UNSUPPORTED_DATA
    reason = "Action Not Exist"


class ActionIsDeprecated(WebSocketException):
    """action被废弃"""

    code = CloseCode.GOING_AWAY
    reason = "Action is deprecated"


class NotFound(WebSocketException):
    """找不到"""

    code = CloseCode.UNSUPPORTED_DATA
    reason = "Not Found"


class MethodNotAllowed(WebSocketException):
    """方法不被运行"""

    code = CloseCode.UNSUPPORTED_DATA
    reason = "Method Not Allowed"


class ParseError(WebSocketException):
    """请求数据解析错误"""

    code = CloseCode.INVALID_DATA
    reason = "Parse Error"


async def WebSocketExceptionHandler(websocket: WebSocket, exc: WebSocketException):
    errors_res = {
        "type": "response",
        "status": exc.status,  # 文字或者 int
        "request_id": exc.request_id,  # 前端传入的标识键值
        "data": exc.data,  # 前端传入的标识键值
        "errors": exc.error_msg,  # 前端传入的标识键值
        **exc.kwargs,
    }
    await websocket.send_text(json.dumps(errors_res, ensure_ascii=False))
    if exc.close:
        await websocket.close(code=exc.code, reason=exc.reason)
