import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_health_is_public_and_ok(api_client):
    response = api_client.get(reverse("health"))
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "ok"
