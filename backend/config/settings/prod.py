"""Production settings: strict, no debug, secrets required."""

import sys

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

_secret = env("SECRET_KEY", default="")
if not _secret or "dev-only" in _secret or "insecure" in _secret:
    raise RuntimeError("SECRET_KEY must be set to a strong production value.")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
if not ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS must be configured in production.")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)

# Guard: demo seeding must never run with production settings.
if "seed" in sys.argv and "manage.py" in sys.argv[0]:
    raise RuntimeError(
        "Demo seeders are forbidden with production settings. "
        "Use config.settings.dev (development environment only)."
    )

_log_level = "WARNING"
LOGGING = {**LOGGING, "root": {**LOGGING["root"], "level": _log_level}}  # noqa: F405
