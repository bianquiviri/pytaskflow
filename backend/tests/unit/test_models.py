import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone

from apps.tasks.models import Task, TaskPriority, TaskStatus
from tests.factories.tasks import TaskFactory
from tests.factories.users import UserFactory

User = get_user_model()
pytestmark = pytest.mark.django_db


class TestUserModel:
    def test_create_user_with_email(self):
        user = User.objects.create_user(email="Ada@example.ORG", password="strong-pass-123")
        # normalize_email lowercases the domain part.
        assert user.email == "Ada@example.org"
        assert user.check_password("strong-pass-123")
        assert user.is_active and not user.is_staff

    def test_email_is_unique_login_field(self):
        User.objects.create_user(email="dup@example.test", password="x")
        with pytest.raises(IntegrityError):
            User.objects.create_user(email="dup@example.test", password="y")

    def test_create_user_requires_email(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email="", password="x")

    def test_create_superuser_flags(self):
        user = User.objects.create_superuser(email="root@example.test", password="x")
        assert user.is_staff and user.is_superuser

    def test_timestamps(self):
        user = UserFactory()
        assert user.created_at is not None
        assert user.updated_at is not None


class TestTaskModel:
    def test_defaults(self):
        task = TaskFactory(title="Only title")
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.MEDIUM
        assert task.due_date is None
        assert task.id is not None
        assert task.created_at is not None

    def test_status_and_priority_choices(self):
        task = TaskFactory(status=TaskStatus.IN_PROGRESS, priority=TaskPriority.HIGH)
        task.refresh_from_db()
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.HIGH

    def test_ordering_most_recent_first(self):
        first = TaskFactory()
        second = TaskFactory()
        assert list(Task.objects.all()) == [second, first]

    def test_owner_deletion_cascades(self):
        user = UserFactory()
        TaskFactory(owner=user)
        user.delete()
        assert Task.objects.count() == 0

    def test_uuid_primary_key_not_sequential(self):
        t1, t2 = TaskFactory(), TaskFactory()
        assert t1.id != t2.id

    def test_due_date_accepts_past_and_future(self):
        past = TaskFactory(due_date=timezone.now() - timezone.timedelta(days=1))
        future = TaskFactory(due_date=timezone.now() + timezone.timedelta(days=30))
        assert past.due_date < future.due_date
