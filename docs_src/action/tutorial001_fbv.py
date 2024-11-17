from fastapi import FastAPI, WebSocket

from fastapi_channels import add_channel
from fastapi_channels.channels import Channel
from fastapi_channels.throttling import limiter

app = FastAPI()
add_channel(app, add_exception_handlers=True, url="memory://", limiter_url="redis://localhost:6379")

my_channel = Channel()


@limiter(seconds=60, times=2)
@my_channel.action()
async def message(websocket: WebSocket, channel: str, data: dict, **kwargs):
    return my_channel.broadcast_to_channel(channel=channel, message=data.get("message"))


@app.websocket("/")
async def ws_endpoint(websocket: WebSocket):
    return await my_channel.connect(websocket)
