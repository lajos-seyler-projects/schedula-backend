import pytest

from users.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_email_is_unique():
    user = UserFactory()

    with pytest.raises(Exception):
        UserFactory(email=user.email)


def test_username_is_unique():
    user = UserFactory()

    with pytest.raises(Exception):
        UserFactory(username=user.username)
