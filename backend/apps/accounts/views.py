"""Auth endpoints: register, login, refresh, logout, me."""

from django.contrib.auth import logout as django_logout
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    RefreshSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(APIView):
    """Create a user account and return initial tokens."""

    permission_classes = [AllowAny]
    authentication_classes: list = []
    throttle_scope = "auth"

    @extend_schema(
        operation_id="auth_register",
        tags=["auth"],
        request=RegisterSerializer,
        responses={201: UserSerializer},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """Email/password login returning access + refresh tokens.

    Throttled through the global ``ScopedRateThrottle`` default via
    ``throttle_scope`` (so test settings can disable it wholesale).
    """

    serializer_class = LoginSerializer
    throttle_scope = "login"  # dedicated, stricter scope (LOGIN_THROTTLE_RATE)

    @extend_schema(operation_id="auth_login", tags=["auth"], responses={200: LoginSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RefreshView(TokenRefreshView):
    """Rotate the refresh token and return a new access token."""

    throttle_scope = "auth"

    @extend_schema(
        operation_id="auth_refresh",
        tags=["auth"],
        request=RefreshSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {"access": {"type": "string"}, "refresh": {"type": "string"}},
            }
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """Blacklist the provided refresh token (idempotent client-side)."""

    permission_classes = [IsAuthenticated]
    throttle_scope = "auth"

    @extend_schema(
        operation_id="auth_logout", tags=["auth"], request=LogoutSerializer, responses={204: None}
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except TokenError:
            # Already invalid/blacklisted: treat as success (idempotent logout).
            pass
        django_logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    """Return the authenticated user's profile."""

    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="auth_me", tags=["auth"], responses={200: UserSerializer})
    def get(self, request):
        return Response(UserSerializer(request.user).data)
