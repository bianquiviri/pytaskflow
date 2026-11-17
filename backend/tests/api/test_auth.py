import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db

REGISTER = "auth-register"
LOGIN = "auth-login"
REFRESH = "auth-refresh"
LOGOUT = "auth-logout"
ME = "auth-me"


def register(api_client, **overrides):
    payload = {
        "email": "ada@example.test",
        "password": "S3cure-passw0rd!",
        "first_name": "Ada",
        "last_name": "Lovelace",
        **overrides,
    }
    return api_client.post(reverse(REGISTER), payload)


class TestRegistration:
    def test_register_returns_tokens_and_user(self, api_client):
        response = register(api_client)
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["user"]["email"] == "ada@example.test"
        assert body["user"]["first_name"] == "Ada"
        assert "access" in body and "refresh" in body
        assert "password" not in body["user"]

    def test_register_rejects_weak_password(self, api_client):
        response = register(api_client, password="12345678")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.json()

    def test_register_rejects_duplicate_email(self, api_client, user):
        response = register(api_client, email=user.email)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_requires_email(self, api_client):
        response = register(api_client, email="")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestLogin:
    def test_login_returns_tokens_and_user(self, api_client, user):
        user.set_password("S3cure-passw0rd!")
        user.save()
        response = api_client.post(
            reverse(LOGIN), {"email": user.email, "password": "S3cure-passw0rd!"}
        )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert "access" in body and "refresh" in body
        assert body["user"]["email"] == user.email

    def test_login_wrong_password(self, api_client, user):
        user.set_password("S3cure-passw0rd!")
        user.save()
        response = api_client.post(reverse(LOGIN), {"email": user.email, "password": "wrong"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRefreshAndMe:
    def _tokens(self, api_client, user):
        user.set_password("S3cure-passw0rd!")
        user.save()
        return api_client.post(
            reverse(LOGIN), {"email": user.email, "password": "S3cure-passw0rd!"}
        ).json()

    def test_refresh_returns_new_access(self, api_client, user):
        tokens = self._tokens(api_client, user)
        response = api_client.post(reverse(REFRESH), {"refresh": tokens["refresh"]})
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.json()

    def test_refresh_rejects_blacklisted_token_after_rotation(self, api_client, user):
        tokens = self._tokens(api_client, user)
        first = api_client.post(reverse(REFRESH), {"refresh": tokens["refresh"]}).json()
        second = api_client.post(reverse(REFRESH), {"refresh": tokens["refresh"]})
        assert second.status_code == status.HTTP_401_UNAUTHORIZED
        assert "access" in first

    def test_me_requires_authentication(self, api_client):
        response = api_client.get(reverse(ME))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_returns_profile(self, auth_client, user):
        response = auth_client.get(reverse(ME))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == user.email
        assert "password" not in response.json()

    def test_access_token_grants_task_access(self, api_client, user):
        tokens = self._tokens(api_client, user)
        response = api_client.get("/api/v1/tasks/", HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        assert response.status_code == status.HTTP_200_OK


class TestLogout:
    def test_logout_blacklists_refresh(self, api_client, user):
        user.set_password("S3cure-passw0rd!")
        user.save()
        tokens = api_client.post(
            reverse(LOGIN), {"email": user.email, "password": "S3cure-passw0rd!"}
        ).json()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        response = api_client.post(reverse(LOGOUT), {"refresh": tokens["refresh"]})
        assert response.status_code == status.HTTP_204_NO_CONTENT
        reuse = api_client.post(reverse(REFRESH), {"refresh": tokens["refresh"]})
        assert reuse.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_requires_auth(self, api_client):
        response = api_client.post(reverse(LOGOUT), {"refresh": "x"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
