from fastapi import FastAPI, WebSocket

from fastapi_channels import add_channel
from fastapi_channels.channels import BaseChannel

app = FastAPI()
add_channel(app, add_exception_handlers=True, url="memory://", limiter_url="redis://localhost:6379")


class MyChannel(BaseChannel):
    channel = "chat_room"


my_channel = BaseChannel()


@app.websocket("/")
async def ws_endpoint(websocket: WebSocket):
    return await my_channel.connect(websocket, channel="chat_room")
