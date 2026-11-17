---
id: TF-Q05
title: "Add performance regression tests for the tasks API"
agent: qa
labels: ["agent:qa", "type:test", "priority:low", "difficulty:hard", "status:ready"]
---

### Context

No performance assertions exist. The list endpoint supports pagination and filters, but nothing guards against N+1 queries or unindexed ordering — the seeded 500-task dataset exists precisely to catch this, and it is unused by tests.

### Objective

Add lightweight performance-regression tests: query-count assertions and latency sanity checks for the tasks list with a meaningful dataset (500 tasks via the seeder's catalog, deterministic).

### Acceptance criteria

- [ ] Test: list endpoint executes a bounded number of queries (assert with Django's `assertNumQueries` or CaptureQueriesContext) for a page of 20 with filters applied — catches select_related regressions.
- [ ] Test: dashboard metrics aggregation stays a single query regardless of task count.
- [ ] Test: 500-task seeded dataset lists within an acceptable time budget on CI hardware (generous bound, e.g., < 1s per page) — mark and document so flakiness can be triaged.
- [ ] Test: seeder runtime for `--tasks 500` completes within a documented budget (guards against accidental per-task query explosions).
- [ ] Perf tests are skippable (`pytest -m perf`) so default runs stay fast; register the marker.

### Technical notes

- Use the deterministic demo catalog (`apps/tasks/seed/demo_tasks.py`) for data generation inside tests — not the production seeder command — or call it with the production-guard documented for test settings.
- CI numbers are noisy: prefer query-count assertions over wall-clock where possible.

### Testing expectations

- New pytest module `tests/perf/` with the `perf` marker; run documented and reported.

### Agent ownership

`qa`
