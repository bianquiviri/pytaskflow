"""Seeder behavior, idempotency, cleanup safety, and environment guards."""

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.tasks.models import Task, TaskPriority, TaskStatus
from apps.tasks.seed.demo_tasks import build_demo_tasks
from tests.factories.tasks import TaskFactory
from tests.factories.users import UserFactory

User = get_user_model()
pytestmark = pytest.mark.django_db


class TestSeedUsers:
    def test_creates_requested_count(self):
        call_command("seed_users", count=7)
        assert User.objects.filter(email__iendswith="@taskflow.local").count() == 7

    def test_default_count(self):
        call_command("seed_users")
        assert User.objects.filter(email__iendswith="@taskflow.local").count() == 5

    def test_idempotent_no_duplicates(self):
        call_command("seed_users", count=5)
        call_command("seed_users", count=5)
        assert User.objects.filter(email__iendswith="@taskflow.local").count() == 5

    def test_increasing_count_adds_only_missing(self):
        call_command("seed_users", count=3)
        call_command("seed_users", count=6)
        assert User.objects.filter(email__iendswith="@taskflow.local").count() == 6

    def test_passwords_hashed_and_usable(self):
        call_command("seed_users", count=2)
        user = User.objects.get(email="demo1@taskflow.local")
        assert not user.password.startswith("demo-password")
        assert user.check_password("demo-password-123")

    def test_realistic_profile_fields(self):
        call_command("seed_users", count=3)
        for user in User.objects.filter(email__iendswith="@taskflow.local"):
            assert user.first_name and user.last_name


class TestSeedTasks:
    def test_requires_demo_users(self):
        call_command("seed_tasks", count=5)
        assert Task.objects.count() == 0

    def test_creates_requested_count(self):
        call_command("seed_users", count=3)
        call_command("seed_tasks", count=30)
        assert Task.objects.count() == 30

    def test_idempotent_no_duplicates(self):
        call_command("seed_users", count=3)
        call_command("seed_tasks", count=20)
        call_command("seed_tasks", count=20)
        assert Task.objects.count() == 20

    def test_variety_of_statuses_and_priorities(self):
        call_command("seed_users", count=3)
        call_command("seed_tasks", count=24)
        statuses = set(Task.objects.values_list("status", flat=True))
        priorities = set(Task.objects.values_list("priority", flat=True))
        assert statuses == {TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.DONE}
        assert priorities == {TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH}

    def test_due_date_buckets_covered(self):
        call_command("seed_users", count=3)
        call_command("seed_tasks", count=24)
        now = Task.objects.first().created_at
        assert Task.objects.filter(due_date__lt=now).exists()  # past
        assert Task.objects.filter(due_date__isnull=True).exists()  # none
        assert Task.objects.filter(due_date__gt=now).exists()  # upcoming

    def test_tasks_with_and_without_description(self):
        call_command("seed_users", count=2)
        call_command("seed_tasks", count=12)
        assert Task.objects.filter(description="").exists()
        assert Task.objects.exclude(description="").exists()

    def test_all_tasks_owned_by_demo_users(self):
        call_command("seed_users", count=4)
        call_command("seed_tasks", count=50)
        owner_domains = {
            owner.email.split("@")[1] for owner in User.objects.filter(tasks__isnull=False)
        }
        assert owner_domains == {"taskflow.local"}


class TestSeedDataOrchestration:
    def test_runs_both_seeders(self):
        call_command("seed_data", users=3, tasks=15)
        assert User.objects.filter(email__iendswith="@taskflow.local").count() == 3
        assert Task.objects.count() == 15

    def test_idempotent(self):
        call_command("seed_data", users=3, tasks=15)
        call_command("seed_data", users=3, tasks=15)
        assert User.objects.filter(email__iendswith="@taskflow.local").count() == 3
        assert Task.objects.count() == 15

    def test_failure_message_is_explicit(self, settings):
        from django.test import override_settings

        with override_settings(ENVIRONMENT="production"):
            with pytest.raises(CommandError, match="forbidden in production"):
                call_command("seed_data", clear=True)


class TestCleanupSafety:
    def test_clear_removes_only_demo_data(self):
        call_command("seed_data", users=2, tasks=10)
        real_user = UserFactory(email="real.user@company.com")
        real_task = TaskFactory(owner=real_user, title="Real project work")
        demo_user = User.objects.get(email="demo1@taskflow.local")

        import os

        os.environ["SEED_CONFIRM_DESTRUCTIVE"] = "yes"
        try:
            call_command("seed_data", clear=True)
        finally:
            del os.environ["SEED_CONFIRM_DESTRUCTIVE"]

        assert not User.objects.filter(email__iendswith="@taskflow.local").exists()
        assert Task.objects.filter(owner=demo_user).count() == 0
        assert User.objects.filter(id=real_user.id).exists()
        assert Task.objects.filter(id=real_task.id).exists()

    def test_clear_requires_confirmation(self):
        call_command("seed_data", users=1, tasks=5)
        import os

        os.environ.pop("SEED_CONFIRM_DESTRUCTIVE", None)
        with pytest.raises(CommandError):
            call_command("seed_data", clear=True)
        assert User.objects.filter(email__iendswith="@taskflow.local").exists()

    def test_clear_does_not_delete_same_titled_tasks_of_real_users(self):
        call_command("seed_users", count=2)
        real_user = UserFactory(email="real@company.com")
        demo_title = build_demo_tasks(4)[1]["title"]
        TaskFactory(owner=real_user, title=demo_title)
        call_command("seed_tasks", count=4)

        import os

        os.environ["SEED_CONFIRM_DESTRUCTIVE"] = "yes"
        try:
            call_command("seed_tasks", clear=True)
        finally:
            del os.environ["SEED_CONFIRM_DESTRUCTIVE"]

        assert Task.objects.filter(owner=real_user).count() == 1


class TestProductionProtection:
    def test_seeding_refused_in_production(self, settings):
        from django.test import override_settings

        with override_settings(ENVIRONMENT="production"):
            with pytest.raises(CommandError, match="forbidden in production"):
                call_command("seed_users")
