from rest_framework import serializers

from users.models import User
from users.serializers import UserSlimSerializer

from . import models


class DefaultColumnPreferenceSerializer(serializers.Serializer):
    table_id = serializers.CharField()
    key = serializers.CharField()
    expression = serializers.JSONField()
    label = serializers.CharField()
    is_visible = serializers.BooleanField()


class UserColumnPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserColumnPreference
        fields = "__all__"


class FilterDefinitionSerializer(serializers.ModelSerializer):
    is_visible = serializers.SerializerMethodField()

    class Meta:
        model = models.FilterDefinition
        fields = ["id", "name", "label", "query_parameter", "required", "is_visible"]

    def get_is_visible(self, obj) -> bool:
        user = self.context.get("request").user
        user_preference = models.UserFilterPreference.objects.filter(
            user=user, filter_definition=obj
        ).first()
        if user_preference:
            return user_preference.is_visible
        return obj.is_visible_by_default


class UserFilterPreferenceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )

    class Meta:
        model = models.UserFilterPreference
        fields = "__all__"


class FilterVariantSerializer(serializers.ModelSerializer):
    is_default = serializers.SerializerMethodField()

    class Meta:
        model = models.FilterVariant
        fields = [
            "uuid",
            "table_id",
            "name",
            "slug",
            "filters",
            "exclude_filters",
            "is_default",
            "execute_on_selection",
            "is_public",
            "created_by",
        ]
        read_only_fields = ["uuid", "slug", "is_default", "created_by"]

    def get_is_default(self, obj) -> bool:
        user = self.context.get("request").user
        return models.UserDefaultFilterVariant.objects.filter(
            user=user, filter_variant=obj
        ).exists()


class UserDefaultFilterVariantSerializer(serializers.ModelSerializer):
    user = UserSlimSerializer(required=False, read_only=True)
    filter_variant = FilterVariantSerializer(read_only=True)
    filter_variant_id = serializers.PrimaryKeyRelatedField(
        queryset=models.FilterVariant.objects.all(),
        source="filter_variant",
        write_only=True,
        required=True,
    )

    class Meta:
        model = models.UserDefaultFilterVariant
        fields = ["id", "user", "filter_variant", "filter_variant_id"]

    def validate_filter_variant_id(self, value):
        table_id = self.context.get("table_id")
        user = self.context.get("request").user

        if not value:
            raise serializers.ValidationError("Filter variant is required.")
        if value.table_id != table_id:
            raise serializers.ValidationError(
                "Filter variant does not match the table id in the URL."
            )
        if value.created_by != user and value.created_by is not None:
            raise serializers.ValidationError(
                "You do not have permission to use this filter variant."
            )
        return value

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
