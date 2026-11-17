---
id: TF-B04
title: "Improve task API filtering and validation"
agent: backend
labels: ["agent:backend", "type:refactor", "priority:medium", "difficulty:medium", "status:ready"]
---

### Context

The list endpoint exposes `filterset_fields = ["status", "priority"]` (exact match) and DRF search/ordering. There are no date-range filters, no multi-value filters, and invalid enum values in query params are silently ignored by django-filter, making client bugs hard to diagnose.

### Objective

Harden list filtering: multi-value `status`/`priority` (`?status=todo,done`), `due_before`/`due_after` datetime filters, and explicit validation errors for unknown or invalid filter values.

### Acceptance criteria

- [ ] `?status=todo,done` returns the union of tasks in both statuses; same for priority.
- [ ] `due_before` / `due_after` accept ISO 8601 datetimes; invalid values return 400 with a clear message, not an empty result.
- [ ] Unknown query params do not break the request (documented behavior).
- [ ] Combined filters compose correctly (`?status=todo&priority=high&due_before=...`).
- [ ] Existing single-value filters and ordering keep working (no breaking change for the current frontend).
- [ ] Filtering logic lives in a `django_filters.FilterSet` in `apps/tasks` (not inline viewset code).

### Technical notes

- Use `django_filters.CharFilter` with a custom method for comma-separated multi-values; validate against `TaskStatus.values`.
- Keep `docs/api/conventions.md` updated with the new parameters.

### Testing expectations

- pytest coverage for each new filter, invalid datetime → 400, multi-value unions, and composition; existing filter tests keep passing.

### Agent ownership

`backend`
