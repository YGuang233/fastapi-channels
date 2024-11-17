from functools import wraps
from typing import Callable, Optional

from .base import Throttle
from .callback import ws_action_default_callback
from .ext._base import WebSocketRateLimiter as _WebSocketRateLimiter

# from .depends import RateLimiter, WebSocketRateLimiter  # noqa:E402

# 用于缓存 WebSocketRateLimiter 实例
_limiter_cache = {}


def limiter(
        times: int = 1,
        milliseconds: int = 0,
        seconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        identifier: Optional[Callable] = None,
        callback: Callable = ws_action_default_callback,
        _limiter: _WebSocketRateLimiter = None,
):
    def decorator(func):
        if not hasattr(func, "action"):
            raise AttributeError(
                "The function is missing the 'action' attribute."
                " Ensure that the @action decorator is applied before @limiter."
            )

        action_name, _ = func.action

        # 创建一个唯一的键，包含所有参数
        cache_key = (
            action_name,
            times,
            milliseconds,
            seconds,
            minutes,
            hours,
            identifier,
        )
        # 如果没有传入 _limiter，则使用缓存
        # if not _limiter:
        #     from .depends import WebSocketRateLimiter
        #     if cache_key not in _limiter_cache:
        #         _limiter_cache[cache_key] = WebSocketRateLimiter()(
        #             times=times,
        #             milliseconds=milliseconds,
        #             seconds=seconds,
        #             minutes=minutes,
        #             hours=hours,
        #             callback=callback,
        #             identifier=identifier,
        #         )
        #     ratelimit = _limiter_cache[cache_key]
        # else:
        #     ratelimit = _limiter

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not _limiter:
                from .depends import WebSocketRateLimiter
                if cache_key not in _limiter_cache:
                    _limiter_cache[cache_key] = WebSocketRateLimiter()(
                        times=times,
                        milliseconds=milliseconds,
                        seconds=seconds,
                        minutes=minutes,
                        hours=hours,
                        callback=callback,
                        identifier=identifier,
                    )
                ratelimit = _limiter_cache[cache_key]
            else:
                ratelimit = _limiter
            _channel = kwargs.get("channel", None)
            _context_key = [action_name]
            if _channel:
                _context_key.insert(0, _channel)
            context_key = ":".join(_context_key)

            await ratelimit(ws=kwargs.get("websocket"), context_key=context_key)
            return await func(*args, **kwargs)

        func.call = wrapper
        return wrapper

    return decorator
