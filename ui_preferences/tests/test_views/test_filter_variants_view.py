import pytest
from django.urls import reverse
from rest_framework import status

from ui_preferences.factories import FilterVariantFactory
from ui_preferences.models import FilterVariant, UserDefaultFilterVariant
from users.factories import UserFactory

pytestmark = pytest.mark.django_db

FILTER_VARIANTS_URL = reverse("ui_preferences:filter-variants-list")


def get_filter_variants_default_url(table_id):
    return f"{FILTER_VARIANTS_URL}{table_id}/default/"


def test_filter_variants_GET_missing_table_id_param(user_drf_client):
    response = user_drf_client.get(FILTER_VARIANTS_URL)
    assert response.status_code == 400


def test_filter_variants_GET_filtered_by_table_id(auth_drf_client):
    client, user = auth_drf_client()
    fv1 = FilterVariantFactory(created_by=user, table_id="target", name="Variant 1")
    fv2 = FilterVariantFactory(created_by=user, table_id="target", name="Variant 2")
    FilterVariantFactory(created_by=user, table_id="other_view", name="Other Variant")
    response = client.get(f"{FILTER_VARIANTS_URL}?table_id=target")
    assert response.status_code == status.HTTP_200_OK
    names = [item["name"] for item in response.json()]
    assert set(names) == {fv1.name, fv2.name}


def test_filter_variants_GET_does_not_return_other_users_variants(auth_drf_client):
    client, user = auth_drf_client()
    other_user = UserFactory()
    fv1 = FilterVariantFactory(created_by=user, table_id="target", name="Variant 1")
    FilterVariantFactory(created_by=other_user, table_id="target", name="Variant 2")
    response = client.get(f"{FILTER_VARIANTS_URL}?table_id=target")
    assert response.status_code == status.HTTP_200_OK
    names = [item["name"] for item in response.json()]
    assert set(names) == {fv1.name}


def test_filter_variants_GET_returns_global_variants(auth_drf_client):
    client, user = auth_drf_client()
    fv1 = FilterVariantFactory(created_by=None, table_id="target", name="Variant 1")
    fv2 = FilterVariantFactory(created_by=user, table_id="target", name="Variant 2")
    response = client.get(f"{FILTER_VARIANTS_URL}?table_id=target")
    assert response.status_code == status.HTTP_200_OK
    names = [item["name"] for item in response.json()]
    assert set(names) == {fv1.name, fv2.name}


def test_filter_variants_POST(auth_drf_client):
    client, user = auth_drf_client()
    request_data = {
        "table_id": "target",
        "name": "New Variant",
        "filters": {"foo": "bar"},
        "exclude_filters": {},
        "is_public": False,
        "execute_on_selection": False,
    }
    response = client.post(FILTER_VARIANTS_URL, data=request_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    created_variant = FilterVariant.objects.filter(created_by=user, table_id="target", name="New Variant")
    assert created_variant.exists()
    assert created_variant[0].filters["foo"] == "bar"
    assert created_variant[0].is_public is False
    assert created_variant[0].execute_on_selection is False


def test_filter_variants_default_PUT(auth_drf_client):
    client, user = auth_drf_client()
    fv = FilterVariantFactory(created_by=user, table_id="target", name="Variant 1")
    url = get_filter_variants_default_url("target")
    response = client.put(url, data={"filter_variant_id": fv.uuid}, format="json")
    assert response.status_code == status.HTTP_200_OK
    created_default_variant = UserDefaultFilterVariant.objects.filter(user=user, filter_variant__table_id="target")
    assert created_default_variant.exists()


def test_filter_variants_default_PUT_does_not_allow_other_users_variant(auth_drf_client):
    client, user = auth_drf_client()
    other_user = UserFactory()
    fv = FilterVariantFactory(created_by=other_user)
    url = get_filter_variants_default_url(fv.table_id)
    response = client.put(url, data={"filter_variant_id": fv.uuid}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "filter_variant_id" in data
    assert data["filter_variant_id"] == ["You do not have permission to use this filter variant."]
