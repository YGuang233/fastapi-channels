from fastapi import FastAPI, WebSocket

from fastapi_channels import add_channel
from fastapi_channels.channels import Channel
from fastapi_channels.decorators import action
from fastapi_channels.throttling import limiter

app = FastAPI()
add_channel(app, add_exception_handlers=True, url="memory://", limiter_url="redis://localhost:6379")


class MyChannel(Channel):
    @limiter(times=2, seconds=60)
    @action()
    async def message(self, websocket: WebSocket, channel: str, data: dict, **kwargs):
        return self.broadcast_to_channel(channel=channel, message=data.get("message"))


my_channel = MyChannel()


@app.websocket("/")
async def ws_endpoint(websocket: WebSocket):
    return await my_channel.connect(websocket)
