"""Deterministic demo task catalog.

Each entry has a stable ``key`` used as the demo marker for idempotency and
safe cleanup. ``enrich(key)`` derives varied, repeatable field values from the
key hash so generated tasks cover every status/priority and due-date bucket
without random data.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from apps.tasks.models import TaskPriority, TaskStatus

DEMO_TASK_MARKER = "demo-task"

# Base catalog entries: cycled to reach any requested count.
CATALOG: tuple[dict, ...] = (
    {
        "title": "Design database schema for reporting",
        "description": "Define tables and indexes for the reporting module.",
    },
    {
        "title": "Fix flaky login test in CI",
        "description": "Investigate race condition in the auth test suite.",
    },
    {"title": "Write onboarding guide", "description": ""},
    {
        "title": "Upgrade Python runtime to 3.13",
        "description": "Validate dependencies and run the full test suite.",
    },
    {
        "title": "Review Q3 security audit findings",
        "description": "Triage findings and assign owners.",
    },
    {
        "title": "Add pagination to activity feed",
        "description": "Cursor-based pagination for the activity feed endpoint.",
    },
    {"title": "Clean up unused feature flags", "description": ""},
    {
        "title": "Prepare customer demo environment",
        "description": "Reset demo data and verify sample scenarios.",
    },
    {
        "title": "Migrate static assets to CDN",
        "description": "Offload static file serving to the CDN.",
    },
    {
        "title": "Document backup and restore procedure",
        "description": "Step-by-step runbook for database recovery.",
    },
    {
        "title": "Improve empty-state copy on dashboard",
        "description": "Make empty states actionable for new users.",
    },
    {
        "title": "Optimize slow tasks query",
        "description": "Add missing composite indexes and verify with EXPLAIN.",
    },
)

STATUS_CYCLE = (
    TaskStatus.TODO,
    TaskStatus.IN_PROGRESS,
    TaskStatus.DONE,
    TaskStatus.TODO,
    TaskStatus.IN_PROGRESS,
    TaskStatus.DONE,
    TaskStatus.TODO,
    TaskStatus.DONE,
)
PRIORITY_CYCLE = (
    TaskPriority.HIGH,
    TaskPriority.MEDIUM,
    TaskPriority.LOW,
    TaskPriority.MEDIUM,
    TaskPriority.HIGH,
    TaskPriority.LOW,
    TaskPriority.MEDIUM,
    TaskPriority.HIGH,
)

# due-date offset buckets (days relative to today); None = no due date.
DUE_BUCKETS: tuple[int | None, ...] = (-7, -2, 0, 0, 3, 10, None, -30, 1, 5, None, 14)


@dataclass(frozen=True)
class DemoTask:
    key: str
    title: str
    description: str
    status: str
    priority: str
    due_date_offset_days: int | None


def demo_task_key(index: int) -> str:
    """Deterministic marker key: demo-task-<n>."""
    return f"{DEMO_TASK_MARKER}-{index + 1}"


def build_demo_tasks(count: int) -> list[dict]:
    """Return ``count`` deterministic demo task payloads (indices 0..count-1)."""
    return [_entry(i) for i in range(count)]


def demo_task_at(index: int) -> dict:
    """Return the deterministic demo task payload for a single catalog index."""
    return _entry(index)


def _entry(index: int) -> dict:
    base = CATALOG[index % len(CATALOG)]
    seq = index // len(CATALOG)
    suffix = f" #{seq + 1}" if seq else ""
    return {
        "key": demo_task_key(index),
        "title": f"{base['title']}{suffix}",
        "description": base["description"],
        "status": STATUS_CYCLE[index % len(STATUS_CYCLE)],
        "priority": PRIORITY_CYCLE[index % len(PRIORITY_CYCLE)],
        "due_date_offset_days": DUE_BUCKETS[index % len(DUE_BUCKETS)],
    }


def iter_demo_tasks(count: int) -> Iterator[dict]:
    return iter(build_demo_tasks(count))
