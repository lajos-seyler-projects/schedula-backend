from django.shortcuts import get_object_or_404
from rest_framework import status, views, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import User
from .serializers import UserRegistrationSerializer
from .utils import send_registration_email


class RegisterView(viewsets.generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        send_registration_email(user)


class UserActivateView(views.APIView):
    def get(self, *args, uuid, token):
        user = get_object_or_404(User, uuid=uuid)

        if not user.activate(token):
            return Response(
                {"message": "Invalid or expired activation token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "User activated successfully."}, status=status.HTTP_200_OK
        )
