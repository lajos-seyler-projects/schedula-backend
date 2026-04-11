from rest_framework import viewsets
from rest_framework.permissions import AllowAny

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
