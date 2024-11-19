from typing import Any

from fastapi import FastAPI, WebSocket

from fastapi_channels import add_channel
from fastapi_channels.channels import BaseChannel

app = FastAPI()
add_channel(app, add_exception_handlers=True, url="memory://", limiter_url="redis://localhost:6379")


class MyChannel(BaseChannel):
    async def receiver(self, websocket: WebSocket, channel: str, message: Any):
        if isinstance(message, str):
            match message:
                case "message":
                    await self.broadcast_to_channel(channel, message)
                case "close":
                    await self.close(websocket)
