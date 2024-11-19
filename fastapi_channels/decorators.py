from enum import Enum
from functools import wraps
from typing import Annotated, Any, Callable, Dict, List, Optional, Sequence, Type, Union

from fastapi import Response, params
from fastapi.datastructures import Default
from fastapi.params import Depends  # noqa
from fastapi.routing import APIRoute
from fastapi.types import DecoratedCallable, IncEx
from fastapi.utils import generate_unique_id
from starlette.responses import JSONResponse
from starlette.routing import BaseRoute
from typing_extensions import Doc  # noqa

from fastapi_channels.exceptions import ActionIsDeprecated
from fastapi_channels.permission import BasePermission


def action(
    name: Optional[str] = None,  # 类似 path
    *,
    permission: Optional[Any] = None,
    detached: bool = False,
    response_model: Annotated[
        Any,
        Doc(
            """
                """
        ),
    ] = Default(None),
    status_code: Annotated[
        Optional[int],
        Doc(
            """
                """
        ),
    ] = None,
    tags: Annotated[
        Optional[List[Union[str, Enum]]],
        Doc(
            """
                """
        ),
    ] = None,
    dependencies: Annotated[
        Optional[Sequence[params.Depends]],
        Doc(
            """
                """
        ),
    ] = None,
    summary: Annotated[
        Optional[str],
        Doc(
            """
                """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
                """
        ),
    ] = None,
    response_description: Annotated[
        str,
        Doc(
            """
                """
        ),
    ] = "Successful Response",
    responses: Annotated[
        Optional[Dict[Union[int, str], Dict[str, Any]]],
        Doc(
            """
                """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
                """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
                """
        ),
    ] = None,
    response_model_include: Annotated[
        Optional[IncEx],
        Doc(
            """
                """
        ),
    ] = None,
    response_model_exclude: Annotated[
        Optional[IncEx],
        Doc(
            """
                """
        ),
    ] = None,
    response_model_by_alias: Annotated[
        bool,
        Doc(
            """
                """
        ),
    ] = True,
    response_model_exclude_unset: Annotated[
        bool,
        Doc(
            """
                """
        ),
    ] = False,
    response_model_exclude_defaults: Annotated[
        bool,
        Doc(
            """
                """
        ),
    ] = False,
    response_model_exclude_none: Annotated[
        bool,
        Doc(
            """
                """
        ),
    ] = False,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
                """
        ),
    ] = True,
    response_class: Annotated[
        Type[Response],
        Doc(
            """
                """
        ),
    ] = Default(JSONResponse),
    # name: Annotated[
    #     Optional[str],
    #     Doc(
    #         """
    #         """
    #     ),
    # ] = None,# 这个name是可以用作jinja url_for{}的
    callbacks: Annotated[
        Optional[List[BaseRoute]],
        Doc(
            """
                """
        ),
    ] = None,
    openapi_extra: Annotated[
        Optional[Dict[str, Any]],
        Doc(
            """
                """
        ),
    ] = None,
    generate_unique_id_function: Annotated[
        Callable[[APIRoute], str],
        Doc(
            """
                """
        ),
    ] = Default(generate_unique_id),
) -> DecoratedCallable:
    if detached:
        raise NotImplementedError(
            "Sorry, the detached function has not been implemented yet and is currently only used for placeholder"
        )

    def decorator(func):
        _name = name if name else func.__name__
        func.action = (_name, func.__doc__)
        perm_desc = "Allow Anyone"
        if isinstance(permission, type) and issubclass(permission, BasePermission):
            perm_desc = permission.__doc__ or permission.has_permission.__doc__
        elif callable(permission):
            perm_desc = permission.__doc__
        elif isinstance(permission, bool):
            if not permission:
                perm_desc = "Not Allow Anyone"
        func.permission = (permission, perm_desc)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if deprecated:
                raise ActionIsDeprecated(
                    error_msg=f"The action '{_name}' is deprecated.", close=False
                )
            return await func(*args, **kwargs)

        # func.call = wrapper
        return wrapper

    return decorator
