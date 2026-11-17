---
id: TF-B01
title: "Add task bulk status updates endpoint"
agent: backend
labels: ["agent:backend", "type:feature", "priority:medium", "difficulty:medium", "status:ready"]
---

### Context

The tasks API supports single-task updates only. Users managing large batches (e.g., closing several completed items) must issue one request per task, which is slow and produces N round trips and N serializer validations.

### Objective

Add `PATCH /api/v1/tasks/bulk-status/` accepting `{"ids": [<uuid>, ...], "status": <TaskStatus>}` that updates all listed tasks owned by the requesting user and returns the affected task payloads.

### Acceptance criteria

- [ ] Only tasks owned by the requesting user are updated; foreign or missing IDs are reported in the response (e.g., `{updated: [...], not_found: [...]}`), never silently skipped or 500.
- [ ] Invalid status values return 400 with the standard error shape.
- [ ] The endpoint requires authentication; anonymous requests return 401.
- [ ] Response includes per-task `updated_at` timestamps proving the update applied.
- [ ] OpenAPI schema documents the new operation without warnings from `python manage.py spectacular`.
- [ ] Empty `ids` list returns 400.

### Technical notes

- Implement the business rule in `apps/tasks/services.py` (e.g., `bulk_update_status(owner_id, ids, status)`); keep the viewset thin.
- Enforce ownership inside the service query (`filter(owner_id=owner_id, id__in=ids)`), not via per-object permission checks.
- Use a single `queryset.update()` plus re-fetch for the response payload to avoid N+1 writes.
- Register the custom route on the existing `TaskViewSet` router (`drf` `@action(detail=False, methods=["patch"])`).

### Testing expectations

- pytest coverage: happy path (2 tasks updated), partial ownership (1 foreign id → reported, not updated), invalid status → 400, empty ids → 400, unauthenticated → 401.
- Update `docs/api/conventions.md` with the new endpoint row.

### Agent ownership

`backend` (see `.opencode/agents/backend.md`)
