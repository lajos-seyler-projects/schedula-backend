USERS_FILTER_DEFINITIONS = {
    "users": [
        {
            "name": "username",
            "label": "Username",
            "query_parameter": "username__icontains",
            "required": True,
            "is_visible_by_default": True,
        },
        {
            "name": "email",
            "label": "Email",
            "query_parameter": "email__icontains",
            "required": False,
            "is_visible_by_default": True,
        },
        {
            "name": "first_name",
            "label": "First Name",
            "query_parameter": "first_name__icontains",
            "required": False,
            "is_visible_by_default": True,
        },
        {
            "name": "last_name",
            "label": "Last Name",
            "query_parameter": "last_name__icontains",
            "required": False,
            "is_visible_by_default": True,
        },
        {
            "name": "is_active",
            "label": "Is Active",
            "query_parameter": "is_active",
            "required": "False",
            "is_visible_by_default": True,
        },
        {
            "name": "is_superuser",
            "label": "Is Superuser",
            "query_parameter": "is_superuser",
            "required": False,
            "is_visible_by_default": True,
        },
    ]
}
