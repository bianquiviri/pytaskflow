"""Security-focused authentication tests (TF-Q01).

Proves the auth endpoints resist common misuse patterns: malformed tokens,
token type confusion, hash exposure, user enumeration, oversized inputs, and
cross-user logout. No production code is modified here; observed behavior that
differs from an ideal is documented in the test itself.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db

REGISTER = "auth-register"
LOGIN = "auth-login"
REFRESH = "auth-refresh"
LOGOUT = "auth-logout"
ME = "auth-me"

PASSWORD = "S3cure-passw0rd!"
SENSITIVE_KEY_PARTS = ("password", "hash", "salt")

User = get_user_model()


def _login_response(api_client, user, password=PASSWORD):
    """Log `user` in through the API and return the raw response."""
    user.set_password(password)
    user.save()
    return api_client.post(reverse(LOGIN), {"email": user.email, "password": password})


def _assert_no_hash_exposure(response, user):
    """Full-body scan: no sensitive key names, no actual hash value."""
    body = response.json()

    def walk(node, path=""):
        if isinstance(node, dict):
            for key, value in node.items():
                lowered = str(key).lower()
                assert not any(part in lowered for part in SENSITIVE_KEY_PARTS), (
                    f"sensitive key {path}{key!r} in response body"
                )
                walk(value, f"{path}{key}.")
        elif isinstance(node, list):
            for index, item in enumerate(node):
                walk(item, f"{path}[{index}]")

    walk(body)
    assert user.password not in response.content.decode()


@pytest.mark.parametrize(
    "authorization",
    [
        "Bearer garbage",
        "Bearer a.b.c",  # three parts, invalid payload/signature
        "Bearer .",  # malformed separator
        "Bearer",  # keyword without token
        "Basic dXNlcjpwYXNz",  # wrong scheme
        "Token abc.def.ghi",  # wrong scheme keyword
        "",  # no header value
        "Bearer " + "x" * 5000,  # oversized junk
    ],
)
def test_malformed_authorization_headers_return_401_not_500(api_client, authorization):
    response = api_client.get(reverse(ME), HTTP_AUTHORIZATION=authorization)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_access_token_is_rejected_at_refresh_endpoint(api_client, user):
    tokens = _login_response(api_client, user).json()
    response = api_client.post(reverse(REFRESH), {"refresh": tokens["access"]})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token_is_rejected_as_access_token(api_client, user):
    tokens = _login_response(api_client, user).json()
    response = api_client.get(reverse(ME), HTTP_AUTHORIZATION=f"Bearer {tokens['refresh']}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_register_response_never_exposes_password_hash(api_client):
    email = "hash-scan@example.test"
    response = api_client.post(
        reverse(REGISTER),
        {
            "email": email,
            "password": PASSWORD,
            "first_name": "Ada",
            "last_name": "Lovelace",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    _assert_no_hash_exposure(response, User.objects.get(email=email))


def test_login_and_me_responses_never_expose_password_hash(api_client, user):
    login_response = _login_response(api_client, user)
    assert login_response.status_code == status.HTTP_200_OK
    _assert_no_hash_exposure(login_response, user)

    tokens = login_response.json()
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    me_response = api_client.get(reverse(ME))
    assert me_response.status_code == status.HTTP_200_OK
    _assert_no_hash_exposure(me_response, user)


def test_login_error_does_not_reveal_whether_email_exists(api_client, user):
    """Unknown email and wrong password must yield one identical generic error."""
    unknown_email = api_client.post(
        reverse(LOGIN), {"email": "ghost@example.test", "password": "Whatever-12345"}
    )
    wrong_password = api_client.post(
        reverse(LOGIN), {"email": user.email, "password": "definitely-not-it"}
    )

    assert unknown_email.status_code == status.HTTP_401_UNAUTHORIZED
    assert wrong_password.status_code == status.HTTP_401_UNAUTHORIZED
    assert unknown_email.json() == wrong_password.json()  # single generic message

    detail = str(unknown_email.json())
    assert user.email not in detail
    assert "ghost" not in detail


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("email", f"{'a' * 310}@example.test"),  # 323 chars > EmailField's 254
        ("first_name", "A" * 1000),  # > CharField(max_length=150)
        ("last_name", "B" * 1000),
    ],
)
def test_register_rejects_extremely_long_inputs_cleanly(api_client, field, value):
    payload = {
        "email": "normal@example.test",
        "password": PASSWORD,
        "first_name": "Ada",
        "last_name": "Lovelace",
        field: value,
    }
    response = api_client.post(reverse(REGISTER), payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST  # clean 4xx, never 500
    assert response.json()  # structured validation error


def test_logout_with_another_users_refresh_token_blacklists_it(api_client, user, other_user):
    """Observed behavior (documented per TF-Q01): no ownership check.

    An authenticated user can submit someone else's refresh token to
    `/auth/logout/`; the call succeeds (204) and the victim's token ends up
    blacklisted (a later refresh with it is rejected with 401). The endpoint
    does not compare the token's subject against the request user.
    """
    victim_tokens = _login_response(api_client, user).json()
    # _login_response persists the password explicitly (UserFactory skips the
    # post-generation save, so its set_password call never reaches the DB).
    attacker = _login_response(api_client, other_user).json()

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {attacker['access']}")
    logout = api_client.post(reverse(LOGOUT), {"refresh": victim_tokens["refresh"]})
    assert logout.status_code == status.HTTP_204_NO_CONTENT

    # The victim's refresh token is no longer usable.
    reuse = api_client.post(reverse(REFRESH), {"refresh": victim_tokens["refresh"]})
    assert reuse.status_code == status.HTTP_401_UNAUTHORIZED
