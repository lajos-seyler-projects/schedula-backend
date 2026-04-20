from rest_framework import exceptions, permissions


class UserHasPermission(permissions.BasePermission):
    """
    Custom permission class that allows different permissions based on request method.
    The view should define `permission_map`, e.g.:

    permission_map = {
        "GET": "users.view_user",
        "POST": "users.add_user",
        "PUT": "users.change_user",
        "PATCH": "users.change_user",
        "DELETE": "users.delete_user",
    }
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        permission_map = getattr(view, "permission_map", {})

        if request.method not in permission_map:
            raise exceptions.MethodNotAllowed(request.method)

        required_permissions = permission_map.get(request.method)

        if required_permissions is None:
            return True

        if not required_permissions:
            return False

        return request.user.has_perm(required_permissions)
