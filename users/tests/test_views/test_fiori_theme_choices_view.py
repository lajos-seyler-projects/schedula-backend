import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db

FIORI_THEME_CHOICES_URL = reverse("users:fiori-theme-choices")


def test_fiori_theme_choices_requires_authentication(drf_client):
    response = drf_client.get(FIORI_THEME_CHOICES_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_fiori_theme_choices_view(user_drf_client):
    response = user_drf_client.get(FIORI_THEME_CHOICES_URL)

    assert response.status_code == status.HTTP_200_OK

    choices = response.json()

    assert isinstance(choices, list)
    assert len(choices) > 0

    for choice in choices:
        assert "value" in choice
        assert "label" in choice
        assert isinstance(choice["value"], str)
        assert isinstance(choice["label"], str)
