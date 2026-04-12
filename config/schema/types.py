from typing import TypedDict

from drf_spectacular.utils import OpenApiParameter


class ViewSetSchemaEntry(TypedDict, total=False):
    parameters: list[OpenApiParameter]


ViewSetSchemasType = dict[str, ViewSetSchemaEntry]
