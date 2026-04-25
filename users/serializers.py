from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as DefaultTokenObtainPairSerializer

from .models import User, UserPreferences


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name")
        extra_kwargs = {
            "username": {"required": True},
            "email": {"required": True},
            "password": {"required": True, "write_only": True},
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, password=password)
        user.is_active = False
        user.save()
        return user


class ActivationResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class TokenObtainPairSerializer(DefaultTokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["email"] = user.email
        return token


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password")
        extra_kwargs = {
            "username": {"required": False},
            "email": {"required": False},
            "password": {"required": False, "write_only": True},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class UserSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("uuid", "username", "email", "first_name", "last_name", "is_superuser")


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("uuid", "username", "email", "first_name", "last_name", "is_superuser", "date_joined", "last_login")


class UserPreferencesSerializer(serializers.ModelSerializer):
    date_format = serializers.ChoiceField(choices=UserPreferences.DateFormatChoices)
    date_format_display = serializers.CharField(source="get_date_format_display", read_only=True)
    decimal_format = serializers.ChoiceField(choices=UserPreferences.DecimalFormatChoices)
    decimal_format_display = serializers.CharField(source="get_decimal_format_display", read_only=True)
    time_zone = serializers.CharField()
    time_format = serializers.ChoiceField(choices=UserPreferences.TimeFormatChoices)
    time_format_display = serializers.CharField(source="get_time_format_display", read_only=True)
    fiori_theme = serializers.ChoiceField(choices=UserPreferences.FioriThemeChoices)
    fiori_theme_display = serializers.CharField(source="get_fiori_theme_display", read_only=True)
    show_timezone = serializers.BooleanField()

    class Meta:
        model = UserPreferences
        exclude = ("user",)


class PermissionSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField(read_only=True)
    content_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Permission
        fields = "__all__"

    def get_content_type(self, obj) -> str:
        return str(obj.content_type).title()

    def get_user_count(self, obj) -> int:
        return obj.user_set.count()


class GroupSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]


class GroupSerializer(serializers.ModelSerializer):
    user_count = serializers.IntegerField(read_only=True)
    permission_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Group
        fields = ["id", "name", "user_count", "permission_count"]
