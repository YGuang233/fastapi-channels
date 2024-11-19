from typing import Type, Union, Any, Optional

from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from starlette.requests import Request
from starlette.templating import Jinja2Templates

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
# add_channel(app, url="redis://localhost:6379", limiter_url="redis://localhost:6379")
add_channel(app, add_exception_handlers=True, url="redis://:r1e3d1i4s520@192.168.129.128:6379/14",
            # limiter_url="redis://:r1e3d1i4s520@192.168.129.128:6379/14")
            limiter_url="memory://")

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

    @limiter(times=5, minutes=1)  # 请求超额 但是不关闭websocket
    @limiter(times=7, minutes=2)  # 存在冲突，如果多次请求存在一个范围比较大和一个比较小的时间那么将会小的超时了，再请求还是会影响大的 # 一个解决办法就是把时间跨度短的放在上面，跨度大的放下面.这样被小的计数了，也不会影响大的
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
    data = {
        "user": "notice",
        "message": "Join successfully",
        "action": "join room"
    }  # 因为修改列encode 如果不以对应的样式来处理会诱发pydantic的解析错误
    await group_chatroom.broadcast_to_personal(websocket, data)


async def leave_room(
        websocket: WebSocket,
        channel: str,
):
    # await group_chatroom.broadcast_to_personal(websocket, 'leave successfully')
    # error: 👆如果通过action离开房间会输出这个，但是客户端直接关闭会诱发websocket没有进行连接
    # 所以这一步只能`broadcast_to_channel`或者后续处理,而不是`broadcast_to_personal`
    data = {
        "user": "notice",
        "message": "leave successfully",
        "action": "leave room"
    }
    await group_chatroom.broadcast_to_channel(channel, data)


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


@limiter(times=1, seconds=3)
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
