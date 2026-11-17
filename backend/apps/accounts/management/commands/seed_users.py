"""Seed demo users: demo1..demoN @taskflow.local with hashed demo passwords."""

import os

from apps.accounts.models import User
from apps.core.management.base_seed import BaseSeedCommand

DEMO_EMAIL_DOMAIN = "taskflow.local"

DEMO_NAMES = [
    ("Ana", "Torres"),
    ("Bruno", "Salas"),
    ("Carla", "Nunez"),
    ("Diego", "Prado"),
    ("Elena", "Vidal"),
    ("Fabio", "Rojas"),
    ("Gina", "Marquez"),
    ("Hugo", "Lima"),
    ("Iris", "Campos"),
    ("Julia", "Reyes"),
    ("Kevin", "Ortega"),
    ("Laura", "Ponce"),
    ("Marco", "Fuentes"),
    ("Nadia", "Sosa"),
    ("Oscar", "Vega"),
    ("Paula", "Cruz"),
    ("Raul", "Miranda"),
    ("Sofia", "Aguilar"),
    ("Tomas", "Navarro"),
    ("Vera", "Castillo"),
]


def demo_user_emails(count: int) -> list[str]:
    """Stable demo email convention: demo<n>@taskflow.local, n starts at 1."""
    return [f"demo{n}@{DEMO_EMAIL_DOMAIN}" for n in range(1, count + 1)]


class Command(BaseSeedCommand):
    seeder_help = "Seed demo users (idempotent; development only)."

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Target number of demo users (existing demo users count toward it).",
        )

    def _demo_password(self) -> str:
        return os.environ.get("SEED_DEMO_PASSWORD", "demo-password-123")

    def seed(self, options: dict) -> None:
        count = max(1, options.get("count") or 5)
        password = self._demo_password()
        created = 0
        existing = 0
        for n, email in enumerate(demo_user_emails(count), start=1):
            name = DEMO_NAMES[(n - 1) % len(DEMO_NAMES)]
            user, was_created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": name[0],
                    "last_name": name[1],
                    "is_active": True,
                },
            )
            if was_created:
                user.set_password(password)  # hashed with Django's mechanisms
                user.save(update_fields=["password"])
                created += 1
            else:
                existing += 1
        self.success(f"Demo users: {created} created, {existing} already present (target {count}).")
        self.warn(
            "Demo password comes from SEED_DEMO_PASSWORD (default 'demo-password-123') — "
            "never reuse these credentials outside development."
        )

    def clear_demo_data(self) -> None:
        qs = User.objects.filter(email__iendswith=f"@{DEMO_EMAIL_DOMAIN}")
        count = qs.count()
        # Never delete superusers or staff accounts even if they match the domain.
        protected = qs.filter(is_staff=True).count()
        qs.filter(is_staff=False).delete()
        self.info(
            f"Removed {count - protected} demo users ({protected} protected staff accounts left untouched)."
        )
