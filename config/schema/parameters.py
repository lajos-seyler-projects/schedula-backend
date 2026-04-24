from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

user_uuid_param = OpenApiParameter(
    name="uuid",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.PATH,
    description="UUID of the User.",
)
user_token_param = OpenApiParameter(
    name="token",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.PATH,
    description="Activation token of the User.",
)
group_name_param = OpenApiParameter(
    name="name",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.PATH,
    description="Name of the group.",
)
