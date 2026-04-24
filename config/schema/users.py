from . import parameters
from .types import ViewSetSchemasType

VIEWSET_SCHEMAS: ViewSetSchemasType = {
    "UserActivateView": {
        "parameters": [parameters.user_uuid_param, parameters.user_token_param]
    },
    "UserGroupsViewSet": {"parameters": [parameters.user_uuid_param]},
    "GroupUsersViewSet": {"parameters": [parameters.group_name_param]},
}
