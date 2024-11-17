---
comments: true
---

# 权限验证


```python hl_lines="12"
from fastapi import FastAPI, WebSocket
from fastapi_channels import add_channel
from fastapi_channels.channels import BaseChannel
from fastapi_channels.permission import BasePermission, AllowAny

app = FastAPI()
add_channel(
    app,
    add_exception_handlers=True,
    url="memory://",
    limiter_url="redis://localhost:6379"
)


class NotAllowAny(BasePermission):

    async def has_permission(self, websocket: WebSocket, action: str, **kwargs) -> bool:
        return False


my_channel1 = BaseChannel(max_connection=2,permission_classes=[AllowAny])
my_channel2 = BaseChannel(max_connection=2,permission_classes=[NotAllowAny])


@app.websocket('/any')
async def ws_endpoint(websocket: WebSocket):
    return await my_channel1.connect(websocket)
@app.websocket('/no_any')
async def ws_endpoint(websocket: WebSocket):
    return await my_channel2.connect(websocket)

```
