"""Task business logic. Views/serializers delegate non-trivial operations here."""

from __future__ import annotations

from django.db.models import Count, Q, QuerySet

from apps.tasks.models import Task, TaskPriority, TaskStatus


def tasks_for_owner(
    owner_id, *, status: str | None = None, priority: str | None = None
) -> QuerySet[Task]:
    """Base queryset for a single owner, optionally filtered by enum fields."""
    qs = Task.objects.filter(owner_id=owner_id)
    if status:
        if status not in TaskStatus.values:
            raise ValueError(f"Invalid status filter: {status}")
        qs = qs.filter(status=status)
    if priority:
        if priority not in TaskPriority.values:
            raise ValueError(f"Invalid priority filter: {priority}")
        qs = qs.filter(priority=priority)
    return qs


def dashboard_metrics(owner_id) -> dict:
    """Aggregated counts for the frontend dashboard. Single DB round trip."""
    rows = Task.objects.filter(owner_id=owner_id).aggregate(
        total=Count("id"),
        todo=Count("id", filter=Q(status=TaskStatus.TODO)),
        in_progress=Count("id", filter=Q(status=TaskStatus.IN_PROGRESS)),
        done=Count("id", filter=Q(status=TaskStatus.DONE)),
        high_priority=Count("id", filter=Q(priority=TaskPriority.HIGH)),
    )
    return {
        "total": rows["total"],
        "todo": rows["todo"],
        "in_progress": rows["in_progress"],
        "done": rows["done"],
        "high_priority": rows["high_priority"],
    }
