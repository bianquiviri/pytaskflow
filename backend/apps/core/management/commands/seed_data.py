"""Master demo seeder: orchestrates seed_users and seed_tasks."""

from django.core.management import call_command

from apps.core.management.base_seed import BaseSeedCommand


class Command(BaseSeedCommand):
    seeder_help = "Seed the full demo dataset (users + tasks). Idempotent; development only."

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--users", type=int, default=5, help="Target number of demo users.")
        parser.add_argument("--tasks", type=int, default=40, help="Target number of demo tasks.")

    def seed(self, options: dict) -> None:
        self.info("Seeding demo users…")
        call_command("seed_users", count=options.get("users") or 5)
        self.info("Seeding demo tasks…")
        call_command("seed_tasks", count=options.get("tasks") or 40)
        self.success("Demo dataset ready.")

    def clear_demo_data(self) -> None:
        self.info("Removing demo tasks…")
        call_command("seed_tasks", clear=True)
        self.info("Removing demo users…")
        call_command("seed_users", clear=True)
