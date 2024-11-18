# FastAPI-Channels

<p align="center">
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge&logo=python&logoColor=white&labelColor=101010" alt="">
  </a>
  <a href="https://fastapi.tiangolo.com">
    <img src="https://img.shields.io/badge/FastAPI-0.111.0-00a393?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=101010" alt="">
  </a>
</p>

## Introduction
[【中文文档】](../README.md) [【English Doc】](./README_EN.md)

&nbsp;&nbsp;This project mainly provides a fast and convenient extension library for the Web Socket interface communication of Fast API. The feature lies in the ability to implement basic chat room functions with a small amount of code, and the writing style of FastAPI.
<br>
&nbsp;&nbsp;This project has also integrated excellent third-party libraries such as [broadcaster](https://github.com/encode/broadcaster) and [FastAPI limiter](https://github.com/long2ice/fastapi-limiter), and has reserved custom locations for using these libraries in this project.
<br>
&nbsp;&nbsp;Generally, users only need to consider how to write 'actions' to achieve the transmission goals and the corresponding permission classes for accessing' actions' when using this library

## Examples

<img src="https://github.com/user-attachments/assets/593ba9c9-4b23-46bf-8697-bee953372010" alt='WebSockets Demo'>

```python
# -*- coding: utf-8 -*-
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

from path import TemplatePath  # To run this case, please clone the complete example file

templates = Jinja2Templates(TemplatePath)
app = FastAPI()
add_channel(app, url="redis://localhost:6379", limiter_url="redis://localhost:6379")

global_channels_details = {}


def add_global_channels_details(
        channel: Union[Type[BaseChannel], BaseChannel], name: str
) -> tuple[BaseChannel, str]:
    # Check whether the input is a class or an instance,
    # but return instance objects without repeating instantiation
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

    @limiter(times=2, seconds=3000)  # Request exceeded, but it will not close websocket
    @action("count")
    async def get_count(self, websocket: WebSocket, channel: str, data: dict, **kwargs):
        data.update({'message': await self.get_connection_count(channel)})
        await self.broadcast_to_personal(websocket, data)

    @action("message")  # broadcast message
    async def send_message(
            self, websocket: WebSocket, channel: str, data: dict, **kwargs
    ):
        await self.broadcast_to_channel(channel, data)

    @action(
        deprecated=True
    )  # The action is discarded and returns a discarded message. It will not close the websocket
    async def deprecated_action(
            self, websocket: WebSocket, channel: str, data: dict, **kwargs
    ):
        data.update({"message": "send message"})
        await self.broadcast_to_personal(websocket, data)

    @action(
        "permission_denied", permission=False
    )  # return error response with insufficient permissions
    async def permission_false(
            self, websocket: WebSocket, channel: str, data: dict, **kwargs
    ):
        await self.broadcast_to_channel(channel, data)

    @action(
        permission=AllowAny
    )  # raise an exception not only closes websocket
    async def error(self, websocket: WebSocket, channel: str, data: dict, **kwargs):
        raise PermissionDenied(close=False)

    @action()  # The client can actively close the websocket connection through the close action
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
    # error: 👆 If you leave the room through an `action`, it will output this,
    # but if the client closes it directly, it will trigger the websocket to not connect,
    # so this step can only be 'broadcast_to_channel' or processed later,
    # rather than 'broadcast_to_personal'`
    await group_chatroom.broadcast_to_channel(channel, "leave successfully")


# The operation of registering and joining rooms and exiting rooms in 
# the form of functions can be broadcasted to channels, similar to FastAPI
group_chatroom.add_event_handler("join", join_room)
group_chatroom.add_event_handler("leave", leave_room)


# However, implementing channel cycles through asynchronous context managers in the form of classes is not feasible
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
# Because the channel here is passed in the 'connect' after instantiation, 
# I have placed some lifespan operations in the channel, which has a great coupling. 
# I will solve this problem in the future

@limiter(times=1, seconds=3)
@group_chatroom.action("message")  # 消息发送解析和#装饰器异常
async def send_message(websocket: WebSocket, channel: str, data: dict, **kwargs):
    await group_chatroom.broadcast_to_channel(channel, data)


@group_chatroom.action("error_true")  # Trigger exception, host close connection
async def send_error_and_close(
        websocket: WebSocket, channel: str, data: dict, **kwargs
):
    raise PermissionDenied(close=True)


@group_chatroom.action("error_false")  # Trigger exception, host no close connection
async def send_error(websocket: WebSocket, channel: str, data: dict, **kwargs):
    raise PermissionDenied(close=False)


@group_chatroom.action()  # The client sends an 'action' request to the host to close the connection
async def close(websocket: WebSocket, channel: str, data: dict, **kwargs):
    await websocket.close()


_, _ = add_global_channels_details(group_chatroom, group_chatroom_name)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000)

```
The HTML template for the front end [is available here](https://github.com/YGuang233/fastapi-channels/blob/master/example/templates/index.html), and is adapted from [Pieter Noordhuis's PUB/SUB demo](https://gist.github.com/pietern/348262) and [Tom Christie's Broadcaster demo](https://github.com/encode/broadcaster/blob/master/example/templates/index.html).

Please clone the entire example file to run this case

<a href="https://fc.bxzdyg.com/zh/tutorial/">Tutorial - User Guide</a> There are more complete examples with more features included.


## Goal and Achieve

- [x] Permission authentication
    - [x] Basic global and channel permission authentication
    - [x] Permission verification for accessing 'action'
    - [ ] Basic user authentication scheme
- [x] Customize exceptions and global capture, and throw exceptions to control connection status
- [ ] Additional logging
- [ ] Paginator
- [x] Current limiter
    - [x] fastapi-limiter
- [ ] Compatible with support for multiple request types
    - [ ] Text
    - [x] JSON
    - [ ] Binary
- [x] Channel Events
    - [x] Channel lifecycle event(lifespan、on_event)
- [ ] Customizable data transmission structure
    - [ ] Request Body
    - [ ] Response body
    - [ ] Paginator
- [ ] Persistent
    - [ ] Storage of historical records
    - [ ] Reading of historical records
- [ ] back-stage management
    - [ ] API interface control
    - [ ] Timed management
- [ ] i18n
- [ ] Test environment setup
- [ ] Complete doc
- [ ] FastAPI writing stylization (dependency injection...)

## Installation

So now it's up to you to use fastapi-channels
```shell
pip install fastapi-channels
```
