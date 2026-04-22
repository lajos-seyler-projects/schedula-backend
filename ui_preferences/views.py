from django.db import transaction
from rest_framework import mixins, status, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import filters, models, serializers
from .default_column_preferences import DEFAULT_COLUMN_PREFERENCES
from .utils import get_invalid_column_keys, get_preferences_for_table


class DefaultColumnPreferencesView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.DefaultColumnPreferenceSerializer

    def get(self, request):
        table_id_param = request.query_params.get("table_id")

        if not table_id_param:
            return Response(
                {"table_id": ["This query parameter is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        preferences = get_preferences_for_table(table_id=table_id_param)

        if not preferences:
            return Response(
                {
                    "detail": f"No column preferences found for table '{table_id_param}'."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(preferences, many=True)
        return Response(serializer.data)


class UserColumnPreferencesViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserColumnPreferenceSerializer
    filterset_class = filters.UserColumnPreferenceFilter
    pagination_class = None

    def get_queryset(self):
        return models.UserColumnPreference.objects.filter(user=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Bulk create or update user column preferences for a specific table.

        Request body example:
        {
            "table_id": "users",
            "column_preferences": [
                {"key": "username", "is_visible": true, "label": "Username"},
                {"key": "first_name", "is_visible": true, "label": "First Name"},
                {"key": "last_name", "is_visible": false, "label": "Last Name"},
            ]
        }
        """
        table_id = request.data.get("table_id")
        column_preferences = request.data.get("column_preferences")
        errors = {}

        if not table_id:
            errors["table_id"] = ["This field is required."]
        if not column_preferences:
            errors["column_preferences"] = ["This field is required."]

        invalid_column_keys = get_invalid_column_keys(table_id, column_preferences)

        if invalid_column_keys:
            errors["detail"] = (
                f"Invalid column preferences: {', '.join(invalid_column_keys)}"
            )

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        for i, item in enumerate(column_preferences):
            item["order"] = i
            item["table_id"] = table_id
            item["user"] = request.user.id

        serializer = self.get_serializer(data=column_preferences, many=True)
        serializer.is_valid(raise_exception=True)

        self._inject_expressions(serializer.validated_data)

        preferences = [
            models.UserColumnPreference(**item) for item in serializer.validated_data
        ]
        created_preferences = models.UserColumnPreference.objects.bulk_create(
            preferences,
            update_conflicts=True,
            unique_fields=["user", "table_id", "key"],
            update_fields=["is_visible", "label", "order"],
        )

        serializer = self.get_serializer(created_preferences, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _inject_expressions(self, validated_data):
        for item in validated_data:
            table_id = item["table_id"]
            key = item["key"]
            for col in DEFAULT_COLUMN_PREFERENCES.get(table_id, {}):
                if col["key"] == key:
                    item["expression"] = col["expression"]
                    break
