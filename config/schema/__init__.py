from typing import Callable, Type, TypeVar

from drf_spectacular.utils import extend_schema, extend_schema_view

from .users import VIEWSET_SCHEMAS as USERS_VIEWSET_SCHEMAS

T = TypeVar("T", bound=Type)

VIEWSET_SCHEMAS = {**USERS_VIEWSET_SCHEMAS}

VIEWSET_SCHEMAS_BY_METHOD = {}


def extend_api_schema(view_name: str) -> Callable[[T], T]:
    """Custom decorator that applies extend_schema to viewsets based on the VIEWSET_SCHEMAS mapping."""
    mapping = VIEWSET_SCHEMAS.get(view_name, {})

    def decorator(cls: T) -> T:
        return extend_schema(**mapping)(cls)

    return decorator


def extend_api_schema_by_method(view_name: str) -> Callable[[T], T]:
    """Custom decorator that applies extend_schema_view to viewsets based on the VIEWSET_SCHEMAS_BY_METHOD mapping."""
    mapping = VIEWSET_SCHEMAS_BY_METHOD.get(view_name, {})

    def decorator(cls: T) -> T:
        return extend_schema_view(**mapping)(cls)

    return decorator
