from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import serializers
from .utils import get_preferences_for_table


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
