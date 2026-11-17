"""Seed demo tasks owned by demo users. Idempotent via deterministic titles."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts.management.commands.seed_users import DEMO_EMAIL_DOMAIN
from apps.core.management.base_seed import BaseSeedCommand
from apps.tasks.models import Task
from apps.tasks.seed.demo_tasks import build_demo_tasks, demo_task_at

# Upper bound for the cleanup title set (matches any realistic seed count).
_CATALOG_SIZE_LIMIT = 10_000


class Command(BaseSeedCommand):
    seeder_help = "Seed demo tasks for demo users (idempotent; development only)."

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--count",
            type=int,
            default=40,
            help="Target number of demo tasks (existing demo tasks count toward it).",
        )

    def seed(self, options: dict) -> None:
        User = get_user_model()
        owners = list(
            User.objects.filter(email__iendswith=f"@{DEMO_EMAIL_DOMAIN}").order_by("email")
        )
        if not owners:
            self.warn(
                "No demo users found. Run `python manage.py seed_users` first (or use seed_data)."
            )
            return

        count = max(1, options.get("count") or 40)
        # Continue the deterministic catalog sequence after the existing demo
        # tasks so the total equals `count` and repeated runs create nothing.
        existing_total = Task.objects.filter(owner__in=owners).count()
        start_index = existing_total

        now = timezone.now()
        created = 0
        for index in range(start_index, count):
            entry = demo_task_at(index)
            owner = owners[index % len(owners)]
            due_date = None
            if entry["due_date_offset_days"] is not None:
                due_date = now + timedelta(days=entry["due_date_offset_days"])
            Task.objects.create(
                title=entry["title"],
                description=entry["description"],
                status=entry["status"],
                priority=entry["priority"],
                due_date=due_date,
                owner=owner,
            )
            created += 1
        self.success(
            f"Demo tasks: {created} created, {existing_total} already present (target {count})."
        )

    def clear_demo_data(self) -> None:
        """Remove only tasks owned by demo users whose title belongs to the demo catalog."""
        User = get_user_model()
        demo_owner_ids = list(
            User.objects.filter(email__iendswith=f"@{DEMO_EMAIL_DOMAIN}").values_list(
                "id", flat=True
            )
        )
        catalog_titles = {entry["title"] for entry in build_demo_tasks(_CATALOG_SIZE_LIMIT)}
        qs = Task.objects.filter(owner_id__in=demo_owner_ids, title__in=catalog_titles)
        count = qs.count()
        qs.delete()
        self.info(
            f"Removed {count} demo tasks owned by demo users. Other users' tasks were preserved."
        )
