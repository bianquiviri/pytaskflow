"""Health and readiness endpoint."""

import django.db
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """Liveness probe; also verifies database connectivity."""

    permission_classes = [AllowAny]
    authentication_classes: list = []

    @extend_schema(
        operation_id="health_check",
        tags=["health"],
        responses={
            200: {
                "type": "object",
                "properties": {"status": {"type": "string"}, "database": {"type": "string"}},
            }
        },
    )
    def get(self, request):
        try:
            with django.db.connection.cursor():
                database = "ok"
        except Exception:  # noqa: BLE001 — health must never raise
            database = "unavailable"
        return Response({"status": "ok", "database": database}, status=status.HTTP_200_OK)
