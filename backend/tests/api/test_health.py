import django.db
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class _DeadConnection:
    """Stand-in for a database that refuses connections."""

    def cursor(self):
        raise ConnectionError("database unreachable")

    def close(self):
        pass


def test_health_is_public_and_ok(api_client):
    response = api_client.get(reverse("health"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_stays_200_when_db_is_down(api_client, monkeypatch):
    monkeypatch.setattr(django.db, "connection", _DeadConnection())
    response = api_client.get(reverse("health"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_200_when_db_is_up(api_client):
    response = api_client.get(reverse("ready"))
    assert response.status_code == 200
    assert response.json() == {"ready": True, "checks": {"database": True}}


def test_ready_returns_503_when_db_is_unreachable(api_client, monkeypatch):
    monkeypatch.setattr(django.db, "connection", _DeadConnection())
    response = api_client.get(reverse("ready"))
    assert response.status_code == 503
    assert response.json() == {"ready": False, "checks": {"database": False}}
