import pytest
from django.contrib.auth.models import Permission
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.factories import UserFactory
from users.models import User


def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


@pytest.fixture
def user(db):  # noqa: ARG001
    """Creates a user"""
    return UserFactory.create(is_active=True)


@pytest.fixture
def superuser(db):
    """Creates a superuser"""
    return UserFactory.create(is_superuser=True, is_active=True)


@pytest.fixture
def drf_client():
    """DRF API test client that not authenticated with a user"""
    return APIClient()


@pytest.fixture
def user_drf_client(user):
    """DRF API test client that is authenticated with a user"""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def auth_drf_client(db):
    def make_client(*permissions, user=None):
        if user is None:
            user = UserFactory(is_active=True)

        if permissions:
            perms = Permission.objects.annotate(
                full_perm=Concat(F("content_type__app_label"), Value("."), F("codename"))
            ).filter(full_perm__in=permissions)

            user.user_permissions.add(*perms)

        user = get_object_or_404(User, pk=user.pk)

        client = APIClient()
        tokens = get_tokens(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        return client, user

    return make_client
