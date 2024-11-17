from contextlib import asynccontextmanager
from typing import AsyncIterator

from broadcaster import Broadcast
from fastapi import FastAPI, WebSocket
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis

from fastapi_channels import add_channel
from fastapi_channels.channels import BaseChannel


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator:
    await FastAPILimiter.init(redis=await Redis.from_url("redis://localhost:6379"))
    yield
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan)

add_channel(app, add_exception_handlers=True, broadcast=Broadcast(url="memory://"),
            limiter_url="redis://localhost:6379")
c = BaseChannel()


@app.websocket("/")
async def ws_endpoint(websocket: WebSocket):
    return await c.connect(websocket, "default_channel")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
