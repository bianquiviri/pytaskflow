"""Rate limiting helpers for authentication endpoints."""

from rest_framework.throttling import ScopedRateThrottle


class AuthThrottleMixin:
    """Apply the scoped ``auth`` throttle rate to an auth view."""

    throttle_scope = "auth"

    def get_throttles(self):
        return [ScopedRateThrottle()]
