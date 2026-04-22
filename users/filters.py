from django.contrib.auth.models import Group, Permission
from django_filters import rest_framework as filters

from .models import User


class GroupFilter(filters.FilterSet):
    class Meta:
        model = Group
        fields = {"name": ["icontains"]}


class PermissionFilter(filters.FilterSet):
    class Meta:
        model = Permission
        fields = {"name": ["icontains"]}


class UserFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = {
            "username": ["icontains"],
            "email": ["icontains"],
            "first_name": ["icontains"],
            "last_name": ["icontains"],
            "is_superuser": ["exact"],
        }
