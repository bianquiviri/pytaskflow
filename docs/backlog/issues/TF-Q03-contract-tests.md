---
id: TF-Q03
title: "Add API contract tests against the OpenAPI schema"
agent: qa
labels: ["agent:qa", "type:test", "priority:medium", "difficulty:medium", "status:ready"]
---

### Context

`docs/api/conventions.md` and the drf-spectacular schema describe the API, but nothing validates that responses conform. Frontend work depends on field names and error shapes staying stable; a silent rename breaks the SPA.

### Objective

Create contract tests that fetch the generated OpenAPI schema and assert that key endpoints implement the documented contract (paths, auth requirement, response codes, field presence), so breaking changes fail CI.

### Acceptance criteria

- [ ] Schema loads via drf-spectacular in tests (no network dependency on a running server).
- [ ] Contract checks for `/auth/login/`, `/auth/register/`, `/tasks/`, `/tasks/{id}/`: required request fields, response fields (`id`, `title`, `status`, `priority`, `due_date`, timestamps), and documented status codes.
- [ ] Error-shape contract: validation errors are field-keyed objects; 401 is `{"detail": ...}`.
- [ ] Schema generation produces zero warnings (asserts on drf-spectacular's warning output) so new endpoints can't degrade docs silently.
- [ ] Frontend `src/types/` mirrors the checked fields — add a note comparing both when field drift is detected.

### Technical notes

- Render the schema with `drf_spectacular.generators.SchemaGenerator` in pytest; validate responses with a minimal hand-rolled checker or `openapi-core` if the extra dependency is justified (decide and document).

### Testing expectations

- New pytest module `tests/api/test_contract.py`; runs in the default suite; no server process needed.

### Agent ownership

`qa`
