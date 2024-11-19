from fastapi_channels import FastAPIChannel
from fastapi_channels.throttling.base import _create_backend

ThrottleBackend = _create_backend(FastAPIChannel.limiter_url)
RateLimiter = ThrottleBackend.ratelimiter
WebSocketRateLimiter = ThrottleBackend.websocket_ratelimiter
