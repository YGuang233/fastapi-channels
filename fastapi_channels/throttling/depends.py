# from fastapi_channels import FastAPIChannel
#
# RateLimiter = FastAPIChannel.throttle.ratelimiter()
# WebSocketRateLimiter = FastAPIChannel.throttle.websocket_ratelimiter()
# 实际上这样子写的话,下面的指引路径还更短
from fastapi_channels import FastAPIChannel
from fastapi_channels.throttling.base import _create_backend

# RateLimiter = Throttle.ratelimiter()
# WebSocketRateLimiter = Throttle.websocket_ratelimiter()
ThrottleBackend = _create_backend(FastAPIChannel.limiter_url)
RateLimiter = ThrottleBackend.ratelimiter
WebSocketRateLimiter = ThrottleBackend.websocket_ratelimiter
# from functools import lru_cache
# @lru_cache()
# def RateLimiter():
#     from . import Throttle
#
#     return Throttle.ratelimiter()
#
#
# @lru_cache()
# def WebSocketRateLimiter():
#     from . import Throttle
#
#     return Throttle.ratelimiter()
