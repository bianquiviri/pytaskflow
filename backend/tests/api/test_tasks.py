import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.tasks.models import Task, TaskPriority, TaskStatus
from tests.factories.tasks import TaskFactory

pytestmark = pytest.mark.django_db

LIST = "task-list"
DETAIL = "task-detail"


def payload(**overrides):
    return {
        "title": "Write report",
        "description": "Q3 summary",
        "status": "todo",
        "priority": "high",
        **overrides,
    }


class TestAuthentication:
    def test_anonymous_cannot_list(self, api_client):
        response = api_client.get(reverse(LIST))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_anonymous_cannot_create(self, api_client):
        response = api_client.post(reverse(LIST), payload())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCreate:
    def test_create_task(self, auth_client, user):
        response = auth_client.post(reverse(LIST), payload())
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["title"] == "Write report"
        assert body["status"] == "todo"
        assert body["priority"] == "high"
        assert Task.objects.get(id=body["id"]).owner_id == user.id

    def test_create_without_title(self, auth_client):
        response = auth_client.post(reverse(LIST), {"title": "   "})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_invalid_status(self, auth_client):
        response = auth_client.post(reverse(LIST), payload(status="archived"))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "status" in response.json()

    def test_create_invalid_priority(self, auth_client):
        response = auth_client.post(reverse(LIST), payload(priority="urgent"))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "priority" in response.json()


class TestOwnershipIsolation:
    def test_list_contains_only_own_tasks(self, auth_client, user, other_user):
        TaskFactory.create_batch(3, owner=user)
        TaskFactory.create_batch(2, owner=other_user)
        response = auth_client.get(reverse(LIST))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 3

    def test_cannot_retrieve_foreign_task(self, auth_client, other_user_task):
        response = auth_client.get(reverse(DETAIL, args=[other_user_task.id]))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cannot_update_foreign_task(self, auth_client, other_user_task):
        response = auth_client.patch(
            reverse(DETAIL, args=[other_user_task.id]), {"title": "hacked"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        other_user_task.refresh_from_db()
        assert other_user_task.title != "hacked"

    def test_cannot_delete_foreign_task(self, auth_client, other_user_task):
        response = auth_client.delete(reverse(DETAIL, args=[other_user_task.id]))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Task.objects.filter(id=other_user_task.id).exists()


class TestRetrieveUpdateDelete:
    def test_retrieve(self, auth_client, task):
        response = auth_client.get(reverse(DETAIL, args=[task.id]))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == task.title

    def test_update_put(self, auth_client, task):
        response = auth_client.put(
            reverse(DETAIL, args=[task.id]), payload(title="Rewritten", status="done")
        )
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.title == "Rewritten" and task.status == TaskStatus.DONE

    def test_partial_update_patch(self, auth_client, task):
        original_title = task.title
        response = auth_client.patch(reverse(DETAIL, args=[task.id]), {"status": "in_progress"})
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.title == original_title  # unchanged

    def test_delete(self, auth_client, task):
        response = auth_client.delete(reverse(DETAIL, args=[task.id]))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task.id).exists()

    def test_invalid_uuid_returns_404(self, auth_client):
        response = auth_client.get(reverse(DETAIL, args=["not-a-uuid"]))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unknown_task_returns_404(self, auth_client):
        response = auth_client.get(reverse(DETAIL, args=["00000000-0000-0000-0000-000000000000"]))
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestListFilters:
    def test_filter_by_status(self, auth_client, user):
        TaskFactory(owner=user, status=TaskStatus.TODO)
        TaskFactory(owner=user, status=TaskStatus.DONE)
        response = auth_client.get(reverse(LIST), {"status": "done"})
        assert response.json()["count"] == 1
        assert response.json()["results"][0]["status"] == "done"

    def test_filter_by_priority(self, auth_client, user):
        TaskFactory(owner=user, priority=TaskPriority.HIGH)
        TaskFactory(owner=user, priority=TaskPriority.LOW)
        response = auth_client.get(reverse(LIST), {"priority": "high"})
        assert response.json()["count"] == 1
        assert response.json()["results"][0]["priority"] == "high"

    def test_search_matches_title(self, auth_client, user):
        TaskFactory(owner=user, title="Prepare quarterly review")
        TaskFactory(owner=user, title="Buy coffee")
        response = auth_client.get(reverse(LIST), {"search": "quarterly"})
        assert response.json()["count"] == 1

    def test_search_matches_description(self, auth_client, user):
        TaskFactory(owner=user, title="Alpha", description="Contains unicorn keyword")
        TaskFactory(owner=user, title="Beta", description="nothing")
        response = auth_client.get(reverse(LIST), {"search": "unicorn"})
        assert response.json()["count"] == 1

    def test_ordering_by_due_date(self, auth_client, user):
        now = timezone.now()
        late = TaskFactory(owner=user, due_date=now + timezone.timedelta(days=5))
        soon = TaskFactory(owner=user, due_date=now + timezone.timedelta(days=1))
        response = auth_client.get(reverse(LIST), {"ordering": "due_date"})
        ids = [r["id"] for r in response.json()["results"]]
        assert ids.index(str(soon.id)) < ids.index(str(late.id))

    def test_ordering_descending_created_at_default(self, auth_client, user):
        TaskFactory(owner=user)
        TaskFactory(owner=user)
        response = auth_client.get(reverse(LIST))
        results = response.json()["results"]
        assert results[0]["created_at"] >= results[1]["created_at"]


class TestPagination:
    def test_default_page_size(self, auth_client, user):
        TaskFactory.create_batch(25, owner=user)
        response = auth_client.get(reverse(LIST))
        body = response.json()
        assert body["count"] == 25
        assert len(body["results"]) == 20

    def test_page_size_param(self, auth_client, user):
        TaskFactory.create_batch(15, owner=user)
        response = auth_client.get(reverse(LIST), {"page_size": 10})
        assert len(response.json()["results"]) == 10

    def test_second_page(self, auth_client, user):
        TaskFactory.create_batch(25, owner=user)
        response = auth_client.get(reverse(LIST), {"page": 2})
        body = response.json()
        assert len(body["results"]) == 5
        assert body["previous"] is not None
