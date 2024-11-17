from fastapi_channels import FastAPIChannel

RateLimiter = FastAPIChannel.throttle.ratelimiter
WebSocketRateLimiter = FastAPIChannel.throttle.websocket_ratelimiter
