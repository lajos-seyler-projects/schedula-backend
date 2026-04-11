from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import User
from .serializers import UserRegistrationSerializer


class RegisterView(viewsets.generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
