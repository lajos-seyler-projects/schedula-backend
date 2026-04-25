USERS_DEFAULT_COLUMN_PREFERENCES = {
    # username, email, first_name, last_name, is_superuser
    "users": [
        {
            "name": "username",
            "is_visible": True,
            "key": "username",
            "expression": {"type": "field", "path": "username"},
            "label": "Username",
        },
        {
            "name": "email",
            "is_visible": True,
            "key": "email",
            "expression": {"type": "field", "path": "email"},
            "label": "Email",
        },
        {
            "name": "first_name",
            "is_visible": True,
            "key": "first_name",
            "expression": {"type": "field", "path": "first_name"},
            "label": "First Name",
        },
        {
            "name": "last_name",
            "is_visible": True,
            "key": "last_name",
            "expression": {"type": "field", "path": "last_name"},
            "label": "Last Name",
        },
        {
            "name": "is_active",
            "is_visible": True,
            "key": "is_active",
            "expression": {"type": "field", "path": "is_active"},
            "label": "Is Active",
        },
        {
            "name": "is_superuser",
            "is_visible": True,
            "key": "is_superuser",
            "expression": {"type": "field", "path": "is_superuser"},
            "label": "Is Superuser",
        },
    ]
}
