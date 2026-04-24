from django.db import transaction
from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
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
        if getattr(self, "swagger_fake_view", False):
            return models.UserColumnPreference.objects.none()

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


class FilterDefinitionsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = models.FilterDefinition.objects.all()
    serializer_class = serializers.FilterDefinitionSerializer
    filterset_class = filters.FilterDefinitionFilter
    pagination_class = None


class UserFilterPreferencesUpdateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserFilterPreferenceSerializer

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        """
        Bulk create or update user filter preferences for a specific table.

        Request body example:
        {
            "table_id": "users",
            "filter_preferences": [
                {"name": "username", "is_visible": true},
                {"name": "first_naem", "is_visible": false},
                {"name": "is_superuser", "is_visible": true}
            ]
        }
        """
        table_id = request.data.get("table_id")
        filter_preferences = request.data.get("filter_preferences", [])
        errors = {}

        if not table_id:
            errors["table_id"] = ["This field is required."]
        if not filter_preferences:
            errors["filter_preferences"] = ["This field is required."]

        validated_data, missing_filters = self.validate_filter_preferences(
            request.user, table_id, filter_preferences
        )
        if missing_filters:
            filters_text = [
                f"{table_id}:{filter_name}" for table_id, filter_name in missing_filters
            ]
            errors["detail"] = f"Missing filter definitions: {', '.join(filters_text)}"
        if errors:
            return Response(
                errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        models.UserFilterPreference.objects.filter(
            user=request.user, filter_definition__table_id=table_id
        ).delete()
        preferences = [models.UserFilterPreference(**item) for item in validated_data]
        created_preferences = models.UserFilterPreference.objects.bulk_create(
            preferences,
            update_conflicts=True,
            unique_fields=["user", "filter_definition"],
            update_fields=["is_visible"],
        )
        serializer = self.get_serializer(created_preferences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def validate_filter_preferences(self, user, table_id, filter_preferences):
        validated_data = []
        missing_filters = []
        for item in filter_preferences:
            name = item.get("name")
            is_visible = item.get("is_visible", True)
            try:
                filter_definition = models.FilterDefinition.objects.get(
                    table_id=table_id, name=name
                )
                validated_data.append(
                    {
                        "user": user,
                        "filter_definition": filter_definition,
                        "is_visible": is_visible,
                    }
                )
            except models.FilterDefinition.DoesNotExist:
                missing_filters.append((table_id, name))
        return validated_data, missing_filters


class FilterVariantsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.FilterVariantSerializer
    pagination_class = None
    filterset_class = filters.FilterVariantFilter
    lookup_field = "uuid"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return models.FilterVariant.objects.none()

        if self.request.method in SAFE_METHODS:
            return models.FilterVariant.objects.filter(
                Q(created_by=self.request.user) | Q(created_by__isnull=True)
            )
        return models.FilterVariant.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["put"], url_path=r"(?P<table_id>[^/.]+)/default")
    def set_default(self, request, table_id):
        serializer = serializers.UserDefaultFilterVariantSerializer(
            data=request.data, context={"request": request, "table_id": table_id}
        )
        serializer.is_valid(raise_exception=True)
        models.UserDefaultFilterVariant.objects.filter(
            user=request.user, filter_variant__table_id=table_id
        ).delete()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
