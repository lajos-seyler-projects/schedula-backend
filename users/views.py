from django.contrib.auth.models import Group, Permission
from django.db.models import Count
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenBlacklistView as DefaultTokenBlacklistView
from rest_framework_simplejwt.views import TokenObtainPairView as DefaultTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView as DefaultTokenRefreshView

from common.permissions import UserHasPermission
from common.serializers import ChoiceSerializer
from config.schema import extend_api_schema

from . import filters, serializers
from .models import User, UserPreferences
from .utils import build_timezone_response, get_filtered_permissions_by_exclusions, send_registration_email


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
            return Response({"message": "Invalid or expired activation token."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "User activated successfully."}, status=status.HTTP_200_OK)


class TokenObtainPairView(DefaultTokenObtainPairView):
    serializer_class = serializers.TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data.pop("refresh", None)
        response.set_cookie(key="refresh", value=refresh_token, httponly=True, secure=True, samesite="None")
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


class CurrentUserRetrieveUpdateViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """User retrieve and update viewsets for the current user"""

    serializer_class = serializers.UserMeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the current request user"""
        return self.request.user


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    filterset_class = filters.UserFilter
    lookup_field = "uuid"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.UserDetailsSerializer
        return serializers.UserSlimSerializer


class BaseChoicesAPIView(APIView):
    choices_class = None
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=ChoiceSerializer(many=True))
    def get(self, request):
        data = [{"value": c.value, "label": c.label} for c in self.choices_class]
        serializer = ChoiceSerializer(data, many=True)
        return Response(serializer.data)


class DateFormatChoicesAPIView(BaseChoicesAPIView):
    choices_class = UserPreferences.DateFormatChoices


class DecimalFormatChoicesAPIView(BaseChoicesAPIView):
    choices_class = UserPreferences.DecimalFormatChoices


@extend_schema(exclude=True)
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

        serializer = self.get_serializer(obj, data={**request.data, "user": request.user.pk}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PermissionsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.PermissionSerializer
    filterset_class = filters.PermissionFilter

    def get_queryset(self):
        return get_filtered_permissions_by_exclusions().order_by("content_type__app_label", "content_type", "codename")


class GroupsViewSet(viewsets.ModelViewSet):
    lookup_field = "name"
    filterset_class = filters.GroupFilter

    def get_queryset(self):
        if self.request.query_params.get("slim") == "true":
            return Group.objects.order_by("name")

        return Group.objects.annotate(
            user_count=Count("user", distinct=True), permission_count=Count("permissions", distinct=True)
        ).order_by("name")

    def get_serializer_class(self):
        if self.request.query_params.get("slim") == "true":
            return serializers.GroupSlimSerializer
        return serializers.GroupSerializer


@extend_api_schema("UserGroupsViewSet")
class UserGroupsViewSet(viewsets.ModelViewSet):
    permission_classes = [UserHasPermission]
    permission_map = {"GET": None, "POST": "users.manage_user_groups", "DELETE": "users.manage_user_groups"}
    serializer_class = serializers.GroupSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Group.objects.none()

        uuid = self.kwargs.get("uuid")
        user = get_object_or_404(User, uuid=uuid)
        return user.groups.annotate(
            user_count=Count("user", distinct=True), permission_count=Count("permissions", distinct=True)
        ).order_by("name")

    def get_groups(self, request):
        group_ids = request.data.get("groups", [])
        return Group.objects.filter(id__in=group_ids)

    def create(self, request, uuid=None):
        if not request.data.get("groups"):
            return Response({"groups": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, uuid=uuid)
        groups = self.get_groups(request)
        user.groups.add(*groups)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["delete"], detail=False)
    def delete(self, request, uuid=None):
        if not request.data.get("groups"):
            return Response({"groups": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, uuid=uuid)
        groups = self.get_groups(request)
        user.groups.remove(*groups)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_api_schema("GroupUsersViewSet")
class GroupUsersViewSet(viewsets.ModelViewSet):
    permission_classes = [UserHasPermission]
    permission_map = {"GET": None, "POST": "users.manage_user_groups", "DELETE": "users.manage_user_groups"}
    serializer_class = serializers.UserSlimSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return User.objects.none()

        name = self.kwargs.get("name")
        group = get_object_or_404(Group, name=name)
        return group.user_set.all()

    def get_users(self, request):
        user_uuids = request.data.get("users", [])
        return User.objects.filter(uuid__in=user_uuids)

    def create(self, request, name=None):
        if not request.data.get("users"):
            return Response({"users": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        group = get_object_or_404(Group, name=name)
        users = self.get_users(request)
        group.user_set.add(*users)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["delete"], detail=False)
    def delete(self, request, name=None):
        if not request.data.get("users"):
            return Response({"users": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        group = get_object_or_404(Group, name=name)
        users = self.get_users(request)
        group.user_set.remove(*users)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_api_schema("GroupPermissionsViewSet")
class GroupPermissionsViewSet(viewsets.ModelViewSet):
    permission_classes = [UserHasPermission]
    permission_map = {"GET": None, "POST": "users.manage_group_permissions", "DELETE": "users.manage_group_permissions"}
    serializer_class = serializers.PermissionSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Permission.objects.none()

        name = self.kwargs.get("name")
        group = get_object_or_404(Group, name=name)
        return group.permissions.all()

    def get_permission_objects(self, request):
        permissions = request.data.get("permissions", [])
        return Permission.objects.filter(id__in=permissions)

    def create(self, request, name=None):
        if not request.data.get("permissions"):
            return Response({"permissions": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        group = get_object_or_404(Group, name=name)
        permissions = self.get_permission_objects(request)
        group.permissions.add(*permissions)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["delete"], detail=False)
    def delete(self, request, name=None):
        if not request.data.get("permissions"):
            return Response({"permissions": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        group = get_object_or_404(Group, name=name)
        permissions = self.get_permission_objects(request)
        group.permissions.remove(*permissions)
        return Response(status=status.HTTP_204_NO_CONTENT)
