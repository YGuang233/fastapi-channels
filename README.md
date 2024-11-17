# FastAPI-Channels

<p align="center">
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge&logo=python&logoColor=white&labelColor=101010" alt="">
  </a>
  <a href="https://fastapi.tiangolo.com">
    <img src="https://img.shields.io/badge/FastAPI-0.111.0-00a393?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=101010" alt="">
  </a>
</p>

## 介绍
[【中文文档】](./README.md) [【English Doc】](./doc/README_EN.md)

&nbsp;&nbsp;本项目主要为FastAPI的WebSocket接口通讯提供快捷方便的扩展库。特色在于少量代码就能实现基本的聊天室的功能,和fastapi的编写风格。
<br>
&nbsp;&nbsp;本项目又集成了优秀的第三方库如:[broadcaster](https://github.com/encode/broadcaster)、[fastapi-limiter](https://github.com/long2ice/fastapi-limiter)。在本项目均保留了自定义使用这些库的位置。
<br>
&nbsp;&nbsp;一般的，用户使用本库仅需考虑如何编写 `action` 来实现传输的目标,和对应的`action`访问的权限类即可

## 案例演示

<img src="https://github.com/user-attachments/assets/593ba9c9-4b23-46bf-8697-bee953372010" alt='WebSockets Demo'>

```python
from typing import Type, Union, Any, Optional

from starlette.requests import Request
from starlette.templating import Jinja2Templates
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from fastapi_channels import add_channel
from fastapi_channels.channels import BaseChannel, Channel
from fastapi_channels.decorators import action
from fastapi_channels.exceptions import PermissionDenied
from fastapi_channels.permission import AllowAny
from fastapi_channels.throttling import limiter
from fastapi_channels.used import PersonChannel, GroupChannel

from path import TemplatePath  # 运行此案例，请将完整的example文件克隆

templates = Jinja2Templates(TemplatePath)
app = FastAPI()
add_channel(app, url="redis://localhost:6379", limiter_url="redis://localhost:6379")

global_channels_details = {}


def add_global_channels_details(
        channel: Union[Type[BaseChannel], BaseChannel], name: str
) -> tuple[BaseChannel, str]:
    # 检查传入的是类还是实例,但是返回的都是实例对象，不做重复的实例化
    if isinstance(channel, type):
        instance = channel()
    else:
        instance = channel

    actions = getattr(instance, "actions", [])
    if BaseChannel in type(instance).__bases__ and type(instance) is not Channel:
        room_type = "base_channel"
    else:
        room_type = "channel"
        assert actions != [], "You should set at least one action"

    global_channels_details[type(instance).__name__] = {
        "action": actions,
        "room": room_type,
        "name": name,
    }
    return instance, name


@app.get("/")
async def homepage(request: Request):
    template = "index.html"
    context = {"request": request, "channels": global_channels_details}
    return templates.TemplateResponse(
        template,
        context,
    )


class ResponseModel(BaseModel):
    action: str
    user: str
    message: Any
    status: str = 'ok'
    errors: Optional[str] = None
    request_id: int = 1

    def create(self) -> str:
        return self.model_dump_json(exclude_none=True)


class BaselChatRoom(BaseChannel): ...


base_chatroom, base_chatroom_name = add_global_channels_details(
    BaselChatRoom, name="chatroom_ws_base"
)


@app.websocket("/base", name=base_chatroom_name)
async def base_chatroom_ws(websocket: WebSocket):
    await base_chatroom.connect(websocket)


class PersonalChatRoom(PersonChannel):
    @staticmethod
    async def encode_json(data: dict) -> str:
        return ResponseModel(**data).create()

    @limiter(times=2, seconds=3000)  # 请求超额 但是不关闭websocket
    @action("count")
    async def get_count(self, websocket: WebSocket, channel: str, data: dict, **kwargs):
        data.update({'message': await self.get_connection_count(channel)})
        await self.broadcast_to_personal(websocket, data)

    @action("message")  # 广播消息
    async def send_message(
            self, websocket: WebSocket, channel: str, data: dict, **kwargs
    ):
        await self.broadcast_to_channel(channel, data)

    @action(deprecated=True)  # action被废弃不关闭websocket
    async def deprecated_action(
            self, websocket: WebSocket, channel: str, data: dict, **kwargs
    ):
        data.update({"message": "发送消息"})
        await self.broadcast_to_personal(websocket, data)

    @action("permission_denied", permission=False)  # 返回权限不足的错误响应
    async def permission_false(
            self, websocket: WebSocket, channel: str, data: dict, **kwargs
    ):
        await self.broadcast_to_channel(channel, data)

    @action(permission=AllowAny)  # 抛出异常不但关闭websocket
    async def error(self, websocket: WebSocket, channel: str, data: dict, **kwargs):
        raise PermissionDenied(close=False)

    @action()  # 客户端通过close的action可以主动关闭websocket连接
    async def close(self, websocket: WebSocket, channel: str, data: dict, **kwargs):
        await websocket.close()


person_chatroom, person_chatroom_name = add_global_channels_details(
    PersonalChatRoom(), name="chatroom_ws_person"
)


@app.websocket("/person", name=person_chatroom_name)
async def person_chatroom_ws(websocket: WebSocket):
    await person_chatroom.connect(websocket, channel="person_channel")


class GroupChatRoom(GroupChannel):
    @staticmethod
    async def encode_json(data: dict) -> str:
        return ResponseModel(**data).create()


group_chatroom = GroupChatRoom()
group_chatroom_name = "chatroom_ws_group"


@app.websocket("/group", name=group_chatroom_name)
async def group_chatroom_ws(websocket: WebSocket):
    await group_chatroom.connect(websocket, channel="group_channel")


async def join_room(
        websocket: WebSocket,
        channel: str,
):
    await group_chatroom.broadcast_to_personal(websocket, "Join successfully")


async def leave_room(
        websocket: WebSocket,
        channel: str,
):
    # await group_chatroom.broadcast_to_personal(websocket, 'leave successfully')
    # error: 👆如果通过action离开房间会输出这个，但是客户端直接关闭会诱发websocket没有进行连接
    # 所以这一步只能`broadcast_to_channel`或者后续处理,而不是`broadcast_to_personal`
    await group_chatroom.broadcast_to_channel(channel, "leave successfully")


# 以函数的形式注册加入房间和退出房间的操作是可以进行广播到频道中,像fastapi那样
group_chatroom.add_event_handler("join", join_room)
group_chatroom.add_event_handler("leave", leave_room)


# 而以类的形式通过异步上下文管理器来实现频道的周期却是不行的
# import contextlib
# @contextlib.asynccontextmanager
# async def lifespan(self, websocket: WebSocket, channel: str, ):
#     # await person_chatroom.broadcast_to_channel(channel, 'Join successfully')
#     # yield
#     # await person_chatroom.broadcast_to_channel(channel, 'leave successfully')
#     await PersonalChatRoom.broadcast_to_channel(channel, 'Join successfully')
#     yield
#     await person_chatroom.broadcast_to_channel(channel, 'leave successfully')
# person_chatroom = PersonalChatRoom(lifespan=lifespan)
# 因为这里的channel是在实例化后的`connect`中被传入的`，因为我将一些lifespan的操作放到了channel,有着极大的耦合，后续将解决这个问题


@limiter(seconds=3, times=1)
@group_chatroom.action("message")  # 消息发送解析和#装饰器异常
async def send_message(websocket: WebSocket, channel: str, data: dict, **kwargs):
    await group_chatroom.broadcast_to_channel(channel, data)


@group_chatroom.action("error_true")  # 触发异常，主机关闭连接
async def send_error_and_close(
        websocket: WebSocket, channel: str, data: dict, **kwargs
):
    raise PermissionDenied(close=True)


@group_chatroom.action("error_false")  # 消息发送解析和异常
async def send_error(websocket: WebSocket, channel: str, data: dict, **kwargs):
    raise PermissionDenied(close=False)


@group_chatroom.action()  # 客户端发通过`action`请求主机关闭连接
async def close(websocket: WebSocket, channel: str, data: dict, **kwargs):
    await websocket.close()


_, _ = add_global_channels_details(group_chatroom, group_chatroom_name)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000)

```
前端的HTML模板[可在此处获得](https://github.com/YGuang233/fastapi-channels/blob/master/example/templates/index.html)，改编自[Pieter Noordhuis的PUB/SUB演示](https://gist.github.com/pietern/348262)和[Tom Christie的Broadcaster演示](https://github.com/encode/broadcaster/blob/master/example/templates/index.html)

运行此案例请将整个example文件进行clone

<a href="https://fc.bxzdyg.com/zh/tutorial/">教程 - 用户指南</a> 中有包含更多特性的更完整示例。

## 目标和实现

- [x] 权限认证
    - [x] 基础全局、频道权限认证
    - [x] 访问`action`的权限验证
    - [ ] 基础的用户验证的方案
- [x] 自定义异常和全局捕获,并且抛出异常可控连接状态
- [ ] 额外的日志记录
- [ ] 分页器
- [x] 限流器
    - [x] fastapi-limiter
- [ ] 兼容多种请求类型的支持
    - [ ] Text
    - [x] JSON
    - [ ] Binary
- [x] 频道事件
    - [x] 频道生命周期事件(lifespan、on_event)
- [ ] 可自定义数据传输的结构
    - [ ] 请求体
    - [ ] 响应体
    - [ ] 分页器
- [ ] 持久化
    - [ ] 历史记录的存储
    - [ ] 历史记录的读取
- [ ] 后台管理
    - [ ] Api接口控制
    - [ ] 定时管理
- [ ] 国际化
- [ ] 测试环境搭建
- [ ] 完善的doc
- [ ] fastapi编写风格化(依赖项注入...)

## 安装

那么接下来就由你来使用fastapi-channels了
```shell
pip install fastapi-channels
```

## 许可协议

该项目遵循 MIT 许可协议。
