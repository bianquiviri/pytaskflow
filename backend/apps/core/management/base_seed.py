"""Shared base for demo-data seeding management commands.

Provides environment safety guards, idempotent execution helpers, and the
--clear destructive workflow. Concrete commands implement ``seed`` and
``clear_demo_data``.
"""

from __future__ import annotations

from abc import abstractmethod

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class BaseSeedCommand(BaseCommand):
    """Base class for TaskFlow demo seeders.

    Subclasses set ``seeder_help`` and implement ``seed()`` / ``clear_demo_data()``.
    ``supports_clear`` toggles the ``--clear`` option for orchestration commands.
    """

    seeder_help = "Seed demo data"
    demo_domain = "taskflow.local"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear", action="store_true", help="Remove only demo records (requires confirmation)."
        )
        # Subclasses add their own count options (--users/--tasks/--count).

    # --- safety guards -------------------------------------------------
    def _guard_environment(self) -> None:
        if getattr(settings, "ENVIRONMENT", "development") == "production":
            raise CommandError(
                "Refusing to seed: demo data generation is forbidden in production. "
                "Run with development settings (DJANGO_SETTINGS_MODULE=config.settings.dev)."
            )

    def _guard_destructive(self) -> None:
        from config.settings.base import env

        if env.str("SEED_CONFIRM_DESTRUCTIVE", default="").lower() != "yes":
            raise CommandError(
                "Refusing destructive cleanup: set SEED_CONFIRM_DESTRUCTIVE=yes to confirm "
                "demo-data removal. Only records marked as demo data are affected."
            )

    # --- hooks ----------------------------------------------------------
    @abstractmethod
    def seed(self, options: dict) -> None: ...

    def clear_demo_data(self) -> None:  # optional hook
        raise CommandError(f"{self.__class__.__name__} does not support --clear.")

    # --- helpers ---------------------------------------------------------
    def info(self, message: str) -> None:
        self.stdout.write(message)

    def warn(self, message: str) -> None:
        self.stdout.write(self.style.WARNING(message))

    def success(self, message: str) -> None:
        self.stdout.write(self.style.SUCCESS(message))

    def handle(self, *args, **options) -> None:
        self._guard_environment()
        if options.get("clear"):
            self._guard_destructive()
            with transaction.atomic():
                self.clear_demo_data()
            self.success("Demo data cleanup complete. Non-demo records were preserved.")
            return
        with transaction.atomic():
            self.seed(options)
