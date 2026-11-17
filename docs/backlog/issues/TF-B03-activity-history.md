---
id: TF-B03
title: "Add task activity history tracking"
agent: backend
labels: ["agent:backend", "type:feature", "priority:medium", "difficulty:hard", "status:ready"]
---

### Context

Task state changes (status, priority, edits) are invisible: the API exposes only `created_at`/`updated_at`. Dashboards and future timelines need an auditable change log.

### Objective

Add a `TaskEvent` model recording create/update/delete events per task with the changed fields, and expose `GET /api/v1/tasks/{id}/events/` for the owner.

### Acceptance criteria

- [ ] `TaskEvent` rows are created on task create, update (including partial updates and bulk endpoints if present), and delete/restore, with `event_type`, `changed_fields` (JSON), and timestamps.
- [ ] Events are recorded even when tasks are updated through services (not just the viewset).
- [ ] Only the task owner can list events; foreign tasks return 404.
- [ ] Events are ordered chronologically and paginated.
- [ ] Event creation failure never breaks the main task write (log and continue, or use a transaction that rolls back together — document the chosen guarantee).

### Technical notes

- Capture changes with `Model.diff` via `tracker`-style serializer diffing in the service layer; avoid signals where explicit service calls suffice, since bulk operations bypass `save()`.
- Store `changed_fields` as a JSONField with old→new values for scalar fields only (skip `updated_at`).
- UUID pk, FK to Task with `on_delete=CASCADE` (or preserve history on soft delete — decide and document in an ADR).

### Testing expectations

- pytest coverage: event created on create/update/restore; field diff correctness; owner-only access; pagination; events not created for no-op PATCH requests.

### Agent ownership

`backend`
