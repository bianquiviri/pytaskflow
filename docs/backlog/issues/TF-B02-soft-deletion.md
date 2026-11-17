---
id: TF-B02
title: "Implement task soft deletion and restoration"
agent: backend
labels: ["agent:backend", "type:feature", "priority:high", "difficulty:medium", "status:ready"]
---

### Context

Task deletion is hard-delete today: `DELETE /api/v1/tasks/{id}/` removes the row permanently. Users cannot recover accidentally deleted tasks, and there is no audit trail of deletion.

### Objective

Introduce soft deletion: `deleted_at` timestamp column. `DELETE` sets `deleted_at` instead of removing the row; add `POST /api/v1/tasks/{id}/restore/` and a listing filter (`?deleted=true`) for the authenticated owner.

### Acceptance criteria

- [ ] `Task` model gains nullable `deleted_at`; default viewsets exclude deleted tasks from list/retrieve.
- [ ] `DELETE` returns 204 and the row still exists in the database with `deleted_at` set.
- [ ] `restore` action clears `deleted_at`; restoring a non-deleted task returns 400 or is idempotent (document the choice).
- [ ] Deleted tasks remain invisible to other users; cross-user access to a deleted task returns 404.
- [ ] Dashboard metrics (`apps/tasks/services.py::dashboard_metrics`) exclude deleted tasks.
- [ ] Existing indexes updated if needed; migrations are generated and applied cleanly.
- [ ] OpenAPI schema updated without warnings.

### Technical notes

- Prefer a manager/default queryset approach (e.g., `Task.objects.active()`) rather than scattered `filter(deleted_at__isnull=True)` calls.
- Keep `IsTaskOwner` semantics: ownership checks still apply to soft-deleted rows.
- Do not implement trash UI — that is a frontend follow-up issue.

### Testing expectations

- pytest coverage: delete → soft-deleted, excluded from list; restore returns it; isolation (foreign deleted task → 404); metrics exclude deleted; seeder and factories unaffected.

### Agent ownership

`backend`
