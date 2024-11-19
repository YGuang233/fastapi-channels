# 如果你想自己手动注册fastapi_channel
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi_channels import FastAPIChannel
from fastapi_channels.exceptions import WebSocketException, WebSocketExceptionHandler


@asynccontextmanager
async def lifespan(_: FastAPI):
    await FastAPIChannel.init(
        url="redis://localhost:6379", limiter_url="redis://localhost:6379"
    )
    yield
    await FastAPIChannel.close()


app = FastAPI(lifespan=lifespan)

app.add_exception_handler(WebSocketException, WebSocketExceptionHandler)  # type:ignore
