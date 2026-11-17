import pytest

from apps.tasks.models import TaskPriority, TaskStatus
from apps.tasks.services import dashboard_metrics, tasks_for_owner
from tests.factories.tasks import TaskFactory
from tests.factories.users import UserFactory

pytestmark = pytest.mark.django_db


class TestTasksForOwner:
    def test_scopes_to_owner_only(self):
        user = UserFactory()
        other = UserFactory()
        TaskFactory(owner=user)
        TaskFactory(owner=other)
        qs = tasks_for_owner(user.id)
        assert qs.count() == 1
        assert qs.first().owner_id == user.id

    def test_status_filter(self):
        user = UserFactory()
        TaskFactory(owner=user, status=TaskStatus.DONE)
        TaskFactory(owner=user, status=TaskStatus.TODO)
        assert tasks_for_owner(user.id, status=TaskStatus.DONE).count() == 1

    def test_priority_filter(self):
        user = UserFactory()
        TaskFactory(owner=user, priority=TaskPriority.HIGH)
        TaskFactory(owner=user, priority=TaskPriority.LOW)
        assert tasks_for_owner(user.id, priority=TaskPriority.HIGH).count() == 1

    def test_invalid_filter_raises(self):
        user = UserFactory()
        with pytest.raises(ValueError):
            tasks_for_owner(user.id, status="bogus")
        with pytest.raises(ValueError):
            tasks_for_owner(user.id, priority="urgent")


class TestDashboardMetrics:
    def test_counts_by_bucket(self):
        user = UserFactory()
        other = UserFactory()
        TaskFactory.create_batch(3, owner=user, status=TaskStatus.TODO, priority=TaskPriority.LOW)
        TaskFactory(owner=user, status=TaskStatus.IN_PROGRESS, priority=TaskPriority.HIGH)
        TaskFactory.create_batch(2, owner=user, status=TaskStatus.DONE, priority=TaskPriority.HIGH)
        TaskFactory(owner=other, status=TaskStatus.DONE, priority=TaskPriority.HIGH)  # foreign
        metrics = dashboard_metrics(user.id)
        assert metrics == {"total": 6, "todo": 3, "in_progress": 1, "done": 2, "high_priority": 3}

    def test_empty_owner(self):
        user = UserFactory()
        assert dashboard_metrics(user.id)["total"] == 0
