from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as DefaultTokenObtainPairSerializer,
)

from .models import User, UserPreferences


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        )
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
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        )
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
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_superuser",
        )


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_superuser",
            "date_joined",
            "last_login",
        )


class UserPreferencesSerializer(serializers.ModelSerializer):
    date_format = serializers.ChoiceField(choices=UserPreferences.DateFormatChoices)
    date_format_display = serializers.CharField(
        source="get_date_format_display",
        read_only=True,
    )
    decimal_format = serializers.ChoiceField(
        choices=UserPreferences.DecimalFormatChoices
    )
    decimal_format_display = serializers.CharField(
        source="get_decimal_format_display",
        read_only=True,
    )
    time_zone = serializers.CharField()
    time_format = serializers.ChoiceField(choices=UserPreferences.TimeFormatChoices)
    time_format_display = serializers.CharField(
        source="get_time_format_display",
        read_only=True,
    )
    fiori_theme = serializers.ChoiceField(choices=UserPreferences.FioriThemeChoices)
    fiori_theme_display = serializers.CharField(
        source="get_fiori_theme_display",
        read_only=True,
    )
    show_timezone = serializers.BooleanField()

    class Meta:
        model = UserPreferences
        exclude = ("user",)
