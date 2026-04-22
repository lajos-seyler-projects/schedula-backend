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
