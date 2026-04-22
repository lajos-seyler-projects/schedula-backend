from rest_framework import serializers

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

    def get_is_visible(self, obj):
        user = self.context.get("request").user
        user_preference = models.UserFilterPreference.objects.filter(
            user=user, filter_definition=obj
        ).first()
        if user_preference:
            return user_preference.is_visible
        return obj.is_visible_by_default
