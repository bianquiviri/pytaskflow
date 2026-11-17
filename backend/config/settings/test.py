"""Test settings: isolated database, fast password hashing.

Database connection is environment-driven (DB_* variables) so tests can run
against any PostgreSQL instance; defaults match the compose development stack.
"""

import os

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test_" + env("DB_NAME", default="taskflow"),
        "USER": env("DB_USER", default="taskflow"),
        "PASSWORD": env("DB_PASSWORD", default="taskflow-dev-password"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env.int("DB_PORT", default=5432),
        "TEST": {"DEPENDENCIES": []},
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Loosen throttling for tests unless a test explicitly exercises it.
REST_FRAMEWORK = {**REST_FRAMEWORK, "DEFAULT_THROTTLE_CLASSES": ()}  # noqa: F405

# Seeders must never run with production settings; tests use ENVIRONMENT=development.
os.environ.setdefault("SEED_CONFIRM_DESTRUCTIVE", "yes")
