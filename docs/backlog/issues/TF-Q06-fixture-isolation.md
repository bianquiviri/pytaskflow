---
id: TF-Q06
title: "Improve test fixtures and test-data isolation"
agent: qa
labels: ["agent:qa", "type:refactor", "priority:medium", "difficulty:easy", "status:ready"]
---

### Context

Tests mix factories (`tests/factories/`) with direct model creation and a few magic strings. Seeder tests depend on the demo email domain, which is correct, but other tests hardcode emails like `ada@example.test` — creating coupling and the risk of colliding with demo data in shared test DBs.

### Objective

Standardize test data: all user creation through factories with a namespace distinct from demo data (`*.example.test` vs `*.taskflow.local`), shared fixtures extracted to `conftest.py`, and a documented isolation rule.

### Acceptance criteria

- [ ] A lint-style test or simple grep-based check fails if production code or tests use the `taskflow.local` domain outside seeder tests — proving demo data can never leak into general tests.
- [ ] `conftest.py` fixtures (`user`, `auth_client`, `other_user`, `other_user_task`, `task`) are used consistently; direct `UserFactory()` calls in api tests replaced by fixtures where equivalent.
- [ ] No test depends on execution order or module-level state (run suite with `-p no:randomly` semantics documented if ordering plugins added later).
- [ ] Document the factory/fixture conventions in `docs/development/testing.md`.

### Technical notes

- Keep it boring: no new dependencies; the grep check can be a pytest test reading `tests/` and `apps/` sources.

### Testing expectations

- Full suite green; new isolation guard test included; report commands executed.

### Agent ownership

`qa`
