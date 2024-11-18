from functools import wraps
from typing import Callable, Optional

from .callback import ws_action_default_callback

# 用于缓存 WebSocketRateLimiter 实例
_limiter_cache = {}


def limiter(
    times: int = 1,
    milliseconds: int = 0,
    seconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    identifier: Optional[Callable] = None,
    ws_callback: Optional[Callable] = None,
):
    if ws_callback is None:
        ws_callback = ws_action_default_callback

    def decorator(func):
        if not hasattr(func, "action"):
            raise AttributeError(
                "The function is missing the 'action' attribute."
                " Ensure that the @action decorator is applied before @limiter."
            )

        action_name, _ = func.action
        if not hasattr(func, "_rate_limits"):
            func._rate_limits = []

        @wraps(func)
        async def wrapper(*args, **kwargs):
            from .depends import WebSocketRateLimiter

            # 创建一个唯一的键，包含所有参数
            cache_key = (
                action_name,
                times,
                milliseconds,
                seconds,
                minutes,
                hours,
                identifier,
                ws_callback,
            )

            # 检查并更新_rate_limits列表
            try:
                index = func._rate_limits.index(cache_key) + 1
            except ValueError:
                func._rate_limits.append(cache_key)
                index = len(func._rate_limits)

            # 缓存限流器
            if cache_key not in _limiter_cache:
                _limiter_cache[cache_key] = WebSocketRateLimiter(
                    times=times,
                    milliseconds=milliseconds,
                    seconds=seconds,
                    minutes=minutes,
                    hours=hours,
                    callback=ws_callback,
                    identifier=identifier,
                )

            ratelimit = _limiter_cache[cache_key]
            _channel = kwargs.get("channel", None)
            _context_key = [_channel, action_name, str(index)]
            context_key = ":".join(_context_key)
            await ratelimit(ws=kwargs.get("websocket"), context_key=context_key)
            return await func(*args, **kwargs)

        # 绑定包装器
        func.call = wrapper
        return wrapper

    return decorator
