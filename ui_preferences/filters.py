from django_filters import rest_framework as filters

from .models import FilterDefinition, UserColumnPreference


class UserColumnPreferenceFilter(filters.FilterSet):
    table_id = filters.CharFilter(required=True)

    class Meta:
        model = UserColumnPreference
        fields = {"table_id": ["exact"]}


class FilterDefinitionFilter(filters.FilterSet):
    table_id = filters.CharFilter(required=True)

    class Meta:
        model = FilterDefinition
        fields = {"table_id": ["exact"]}
