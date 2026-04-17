import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db

DATE_FORMAT_CHOICES_URL = reverse("users:date-format-choices")


def test_date_format_choices_requires_authentication(drf_client):
    response = drf_client.get(DATE_FORMAT_CHOICES_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_date_format_choices_view(user_drf_client):
    response = user_drf_client.get(DATE_FORMAT_CHOICES_URL)

    assert response.status_code == status.HTTP_200_OK

    choices = response.json()

    assert isinstance(choices, list)
    assert len(choices) > 0

    for choice in choices:
        assert "value" in choice
        assert "label" in choice
        assert isinstance(choice["value"], str)
        assert isinstance(choice["label"], str)
