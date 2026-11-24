"""Auth throttle tests (TF-B06).

Throttling is disabled for the whole suite by `config.settings.test`
(`DEFAULT_THROTTLE_CLASSES = ()`), so regular tests never hit rate limits and
need no per-test overrides. The tests below opt *in* via `throttling_at(...)`.

DRF 3.18 snapshots its throttle configuration into class attributes at import
time, so `override_settings(REST_FRAMEWORK=...)` alone does NOT change throttle
behavior — both snapshots must be patched:

- `APIView.throttle_classes` (from `DEFAULT_THROTTLE_CLASSES`);
- `SimpleRateThrottle.THROTTLE_RATES` (from `DEFAULT_THROTTLE_RATES`).

`ScopedRateThrottle` counts requests per ident in the cache and the cache is
cleared per test, so the (N+1)-th call trips an `N/min` rate instantly — no
wall-clock sleeps.
"""

import importlib
import os
import uuid
from contextlib import contextmanager
from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle, SimpleRateThrottle
from rest_framework.views import APIView

pytestmark = pytest.mark.django_db

LOGIN_PAYLOAD = {"email": "nobody@nowhere.test", "password": "wrong-password-1"}
REGISTER_PAYLOAD = {
    "email": f"throttle-{uuid.uuid4().hex[:10]}@example.test",
    "password": "Throttle-Pass-1",
    "first_name": "Throttle",
    "last_name": "Test",
}


@contextmanager
def throttling_at(rates: dict[str, str]):
    """Enable scoped throttling with explicit per-scope rates for the block."""
    with patch.object(APIView, "throttle_classes", (ScopedRateThrottle,)):
        with patch.object(SimpleRateThrottle, "THROTTLE_RATES", rates):
            yield


@pytest.fixture(autouse=True)
def _clean_throttle_cache():
    cache.clear()
    yield
    cache.clear()


def _assert_throttled(response):
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert int(response.headers["Retry-After"]) >= 1
    assert "throttled" in response.json()["detail"].lower()


def test_login_returns_429_after_rate_exceeded(api_client):
    url = reverse("auth-login")
    with throttling_at({"login": "2/min", "auth": "10/min"}):
        for _ in range(2):  # within the limit: throttles do not engage yet
            response = api_client.post(url, LOGIN_PAYLOAD, format="json")
            assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS
        _assert_throttled(api_client.post(url, LOGIN_PAYLOAD, format="json"))


def test_register_returns_429_after_rate_exceeded(api_client):
    url = reverse("auth-register")
    with throttling_at({"login": "5/min", "auth": "1/min"}):
        response = api_client.post(url, REGISTER_PAYLOAD, format="json")
        assert response.status_code == status.HTTP_201_CREATED  # first call is allowed
        _assert_throttled(api_client.post(url, REGISTER_PAYLOAD, format="json"))


def test_unscoped_endpoints_are_not_affected(api_client):
    """Health (no throttle_scope) must stay 200 while auth scopes are capped."""
    url = reverse("health")
    with throttling_at({"login": "1/min", "auth": "1/min"}):
        for _ in range(5):
            response = api_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == {"status": "ok"}


def test_throttle_rates_are_sourced_from_env():
    """AUTH_THROTTLE_RATE / LOGIN_THROTTLE_RATE flow into DEFAULT_THROTTLE_RATES."""
    from config.settings import base as base_settings

    keys = ("AUTH_THROTTLE_RATE", "LOGIN_THROTTLE_RATE")
    saved = {key: os.environ.get(key) for key in keys}
    try:
        os.environ["AUTH_THROTTLE_RATE"] = "7/min"
        os.environ["LOGIN_THROTTLE_RATE"] = "3/min"
        importlib.reload(base_settings)
        rates = base_settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]
        assert rates == {"auth": "7/min", "login": "3/min"}
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        importlib.reload(base_settings)
        # restored state: whatever the process env says, or the documented defaults
        rates = base_settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]
        assert rates["auth"] == os.environ.get("AUTH_THROTTLE_RATE", "10/min")
        assert rates["login"] == os.environ.get("LOGIN_THROTTLE_RATE", "5/min")
