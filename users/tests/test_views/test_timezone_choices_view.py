import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db

TIMEZONE_CHOICES_URL = reverse("users:timezone-choices")


def test_timezone_choices_requires_authentication(drf_client):
    response = drf_client.get(TIMEZONE_CHOICES_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_timezone_choices_view(user_drf_client):
    response = user_drf_client.get(TIMEZONE_CHOICES_URL)

    assert response.status_code == status.HTTP_200_OK

    grouped_choices = response.json()

    assert isinstance(grouped_choices, dict)
    assert len(grouped_choices.keys()) > 0
    assert "Europe" in grouped_choices.keys()
    assert isinstance(grouped_choices["Europe"], list)
    assert len(grouped_choices["Europe"]) > 0

    for choice in grouped_choices["Europe"]:
        assert "value" in choice
        assert "offset" in choice
        assert isinstance(choice["value"], str)
        assert isinstance(choice["offset"], str)
