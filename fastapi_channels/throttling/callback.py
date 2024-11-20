from math import ceil

from fastapi_limiter import default_identifier, http_default_callback
from starlette.websockets import WebSocket

from fastapi_channels.exceptions import RateLimitExceeded

__all__ = [
    "ws_default_callback",
    "ws_action_default_callback",
    "http_default_callback",
    "default_identifier",
]


async def ws_default_callback(ws: WebSocket, pexpire: int) -> None:
    """
    default callback when too many requests
    :param ws:
    :param pexpire: The remaining milliseconds
    :return:
    """
    expire = ceil(pexpire / 1000)
    raise RateLimitExceeded(
        error_msg=f"Too Many Requests. Retry after {expire} seconds."
    )


async def ws_action_default_callback(ws: WebSocket, pexpire: int) -> None:
    """
    default callback when too many requests
    :param ws:
    :param pexpire: The remaining milliseconds
    :return:
    """
    expire = ceil(pexpire / 1000)
    raise RateLimitExceeded(
        error_msg=f"Too Many Requests. Retry after {expire} seconds.", close=False
    )
