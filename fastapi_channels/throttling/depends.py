# from fastapi_channels import FastAPIChannel
#
# RateLimiter = FastAPIChannel.throttle.ratelimiter()
# WebSocketRateLimiter = FastAPIChannel.throttle.websocket_ratelimiter()
# 实际上这样子写的话,下面的指引路径还更短
from functools import lru_cache


# RateLimiter = Throttle.ratelimiter()
# WebSocketRateLimiter = Throttle.websocket_ratelimiter()

@lru_cache()
def RateLimiter():
    from . import Throttle

    return Throttle.ratelimiter()


@lru_cache()
def WebSocketRateLimiter():
    from . import Throttle

    return Throttle.ratelimiter()
