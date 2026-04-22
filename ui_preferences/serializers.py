from rest_framework import serializers


class DefaultColumnPreferenceSerializer(serializers.Serializer):
    table_id = serializers.CharField()
    key = serializers.CharField()
    expression = serializers.JSONField()
    label = serializers.CharField()
    is_visible = serializers.BooleanField()
