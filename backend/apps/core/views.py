"""Liveness and readiness endpoints."""

import threading

import django.db
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

READY_TIMEOUT_SECONDS = 2.0


def _database_ready(timeout: float = READY_TIMEOUT_SECONDS) -> bool:
    """Run `SELECT 1` with a hard timeout; never raise.

    The probe runs in a worker thread so a hung database cannot stall the
    request beyond `timeout` (Django has no per-query timeout).
    """
    outcome = {"ready": False}

    def probe() -> None:
        try:
            with django.db.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                outcome["ready"] = cursor.fetchone() is not None
        except Exception:  # noqa: BLE001 — readiness must never raise
            outcome["ready"] = False
        finally:
            try:
                django.db.connection.close()  # drop this thread's connection
            except Exception:  # noqa: BLE001
                pass

    worker = threading.Thread(target=probe, daemon=True, name="ready-probe")
    worker.start()
    worker.join(timeout)
    return outcome["ready"]


class HealthView(APIView):
    """Liveness probe: the process serves requests. No dependency checks."""

    permission_classes = [AllowAny]
    authentication_classes: list = []

    @extend_schema(
        operation_id="health_check",
        tags=["health"],
        responses={
            200: {
                "type": "object",
                "properties": {"status": {"type": "string"}},
            }
        },
    )
    def get(self, request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class ReadyView(APIView):
    """Readiness probe: verifies dependencies before receiving traffic."""

    permission_classes = [AllowAny]
    authentication_classes: list = []

    @extend_schema(
        operation_id="ready_check",
        tags=["health"],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "ready": {"type": "boolean"},
                    "checks": {"type": "object"},
                },
            },
            503: {
                "type": "object",
                "properties": {
                    "ready": {"type": "boolean"},
                    "checks": {"type": "object"},
                },
            },
        },
    )
    def get(self, request):
        checks = {"database": _database_ready()}
        ready = all(checks.values())
        body = {"ready": ready, "checks": checks}
        code = status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(body, status=code)
