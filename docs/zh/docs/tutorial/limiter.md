---
comments: true
---

# 限流器

限流器主要分为几种：全局限流器、房间限流器、装饰器限流器

优先级是层次递进的：全局限流器<房间限流器<绑定Action的限流器

全局限流和房间限流是整个`BaseChannel`类都支持的。[加入房间后]("加入房间前需要经过几项检验，会经过一次房间权限or全局权限的检验")限流器的优先级是高于权限验证的，这样可以避免多次验证，却没有拿到数据的时间损耗。

```python hl_lines="10-11"
from fastapi import FastAPI, WebSocket
from fastapi_channels import add_channel
from fastapi_channels.channels import BaseChannel
from fastapi_limiter.depends import WebSocketRateLimiter

app = FastAPI()
add_channel(app, url="redis://localhost:6379", limiter_url="redis://localhost:6379",
            throttle_classes=WebSocketRateLimiter(times=2, seconds=60))
c = BaseChannel()


@app.websocket('/')
async def home_page(websocket: WebSocket):
    await c.connect(websocket, 'limiter')
```

```python hl_lines="10 12"
from fastapi import FastAPI, WebSocket
from fastapi_channels import add_channel
from fastapi_channels.channels import BaseChannel
from fastapi_limiter.depends import WebSocketRateLimiter

app = FastAPI()
add_channel(app, url="redis://localhost:6379", limiter_url="redis://localhost:6379")
c = BaseChannel(throttle_classes=WebSocketRateLimiter(times=2, seconds=60))


@app.websocket('/')
async def home_page(websocket: WebSocket):
    await c.connect(websocket, 'limiter')
```

装饰器限流器是在使用`Channel`类的基础上进行设置的，它需要识别对应的`action`标识，所以你不能在任意的函数上去添加这个装饰器

```python
from fastapi import FastAPI, WebSocket
from fastapi_channels.channels import Channel
from fastapi_channels.throttling import limiter

c = Channel()


@limiter(times=2, seconds=60)
@c.action()
async def message(websocket: WebSocket, channel: str, data: dict, **kwargs):
    await c.broadcast_to_channel(channel, 'hello')


app = FastAPI()


@app.websocket('/')
async def home_page(websocket: WebSocket):
    await c.connect(websocket, 'limiter')
```