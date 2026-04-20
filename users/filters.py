from django.contrib.auth.models import Group, Permission
from django_filters import rest_framework as filters


class PermissionFilter(filters.FilterSet):
    class Meta:
        model = Permission
        fields = {"name": ["icontains"]}


class GroupFilter(filters.FilterSet):
    class Meta:
        model = Group
        fields = {"name": ["icontains"]}
