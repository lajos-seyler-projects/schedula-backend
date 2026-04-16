from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import (
    TokenBlacklistView as DefaultTokenBlacklistView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView as DefaultTokenObtainPairView,
)
from rest_framework_simplejwt.views import TokenRefreshView as DefaultTokenRefreshView

from common.serializers import ChoiceSerializer
from config.schema import extend_api_schema

from . import serializers
from .models import User, UserPreferences
from .utils import build_timezone_response, send_registration_email


class RegisterView(viewsets.generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = serializers.UserRegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        send_registration_email(user)


@extend_api_schema("UserActivateView")
class UserActivateView(generics.GenericAPIView):
    serializer_class = serializers.ActivationResponseSerializer
    permission_classes = [AllowAny]

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


class TokenObtainPairView(DefaultTokenObtainPairView):
    serializer_class = serializers.TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data.pop("refresh", None)
        response.set_cookie(
            key="refresh",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="None",
        )
        return response


class TokenRefreshView(DefaultTokenRefreshView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh", None)
        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenBlacklistView(DefaultTokenBlacklistView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh", None)
        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        response.delete_cookie("refresh")
        return response


class CurrentUserRetrieveUpdateViewSet(
    mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """User retrieve and update viewsets for the current user"""

    serializer_class = serializers.UserMeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the current request user"""
        return self.request.user


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = "uuid"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.UserDetailsSerializer
        return serializers.UserSlimSerializer


class BaseChoicesAPIView(APIView):
    choices_class = None
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = [{"value": c.value, "label": c.label} for c in self.choices_class]
        serializer = ChoiceSerializer(data, many=True)
        return Response(serializer.data)


class DateFormatChoicesAPIView(BaseChoicesAPIView):
    choices_class = UserPreferences.DateFormatChoices


class DecimalFormatChoicesAPIView(BaseChoicesAPIView):
    choices_class = UserPreferences.DecimalFormatChoices


class TimezoneChoicesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(build_timezone_response())


class TimeFormatChoicesAPIView(BaseChoicesAPIView):
    choices_class = UserPreferences.TimeFormatChoices


class FioriThemeChoicesAPIView(BaseChoicesAPIView):
    choices_class = UserPreferences.FioriThemeChoices


class UserPreferencesViewSet(viewsets.GenericViewSet):
    serializer_class = serializers.UserPreferencesSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get", "patch"])
    def preferences(self, request):
        obj, _ = UserPreferences.objects.get_or_create(user=request.user)

        if request.method == "GET":
            serializer = self.get_serializer(obj)
            return Response(serializer.data)

        serializer = self.get_serializer(
            obj, data={**request.data, "user": request.user.pk}, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
