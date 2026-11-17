import pytest
from rest_framework.test import APIClient

from tests.factories.tasks import TaskFactory
from tests.factories.users import UserFactory


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def other_user(db):
    return UserFactory()


@pytest.fixture
def auth_client(api_client, user) -> APIClient:
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def task(user, db):
    return TaskFactory(owner=user)


@pytest.fixture
def other_user_task(other_user, db):
    return TaskFactory(owner=other_user)
