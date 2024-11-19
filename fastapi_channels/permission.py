from typing import Any

from fastapi import WebSocket


class OperationHolderMixin:
    def __and__(self, other):
        return OperandHolder(AND, self, other)

    def __or__(self, other):
        return OperandHolder(OR, self, other)

    def __rand__(self, other):
        return OperandHolder(AND, other, self)

    def __ror__(self, other):
        return OperandHolder(OR, other, self)

    def __invert__(self):
        return SingleOperandHolder(NOT, self)


class SingleOperandHolder(OperationHolderMixin):
    def __init__(self, operator_class, op1_class):
        self.operator_class = operator_class
        self.op1_class = op1_class

    def __call__(self, *args, **kwargs):
        op1 = self.op1_class(*args, **kwargs)
        return self.operator_class(op1)


class OperandHolder(OperationHolderMixin):
    def __init__(self, operator_class, op1_class, op2_class):
        self.operator_class = operator_class
        self.op1_class = op1_class
        self.op2_class = op2_class

    def __call__(self, *args, **kwargs):
        op1 = self.op1_class(*args, **kwargs)
        op2 = self.op2_class(*args, **kwargs)
        return self.operator_class(op1, op2)


class AND:
    def __init__(self, op1: "BasePermission", op2: "BasePermission"):
        self.op1 = op1
        self.op2 = op2

    def has_permission(self, websocket: WebSocket, action: str, **kwargs):
        return self.op1.has_permission(
            websocket, action, **kwargs
        ) and self.op2.has_permission(websocket, action, **kwargs)


class OR:
    def __init__(self, op1: "BasePermission", op2: "BasePermission"):
        self.op1 = op1
        self.op2 = op2

    def has_permission(self, websocket: WebSocket, action: str, **kwargs):
        return self.op1.has_permission(
            websocket, action, **kwargs
        ) or self.op2.has_permission(websocket, action, **kwargs)


class NOT:
    def __init__(self, op1: "BasePermission"):
        self.op1 = op1

    def has_permission(self, websocket: WebSocket, action: str, **kwargs):
        return not self.op1.has_permission(websocket, action, **kwargs)


class BasePermissionMetaclass(OperationHolderMixin, type):
    """
    元类以支持逻辑组合
    """

    pass


class BasePermission(metaclass=BasePermissionMetaclass):
    """Base permission class

    Notes:
        You should extend this class and override the `has_permission` method to create your own permission class.

    Methods:
        async has_permission ( websocket, action, **kwargs)
    """

    async def has_permission(self, websocket: WebSocket, action: str, **kwargs) -> bool:
        """
        Called on every websocket message sent before the corresponding action handler is called.
        """
        pass

    async def can_connect(self, websocket: WebSocket, message: Any = None) -> bool:
        """
        Called during connection to validate if a given client can establish a websocket connection.

        By default, this returns True and permits all connections to be made.
        """
        return True


class AllowAny(BasePermission):
    """Allow any permission class"""

    async def has_permission(self, websocket: WebSocket, action: str, **kwargs) -> bool:
        return True
