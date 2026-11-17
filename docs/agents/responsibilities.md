# Agent responsibilities

Definitions live in `.opencode/agents/` (OpenCode native format). Summary of boundaries:

## backend (`.opencode/agents/backend.md`)

Django, DRF, models/migrations, auth, permissions, services, seeders, backend tests, OpenAPI docs. Must not touch frontend code unless an issue explicitly requires it; must protect production data when running seeders; must run the tests it claims to pass.

## frontend (`.opencode/agents/frontend.md`)

Vue 3, TypeScript, components, Pinia, router, API integration, accessibility, frontend tests. Consults API contracts, never backend internals; adds/updates tests for its changes; preserves existing UI behavior unless an issue changes it.

## qa (`.opencode/agents/qa.md`)

Test strategy, unit/integration/E2E tests, regression, bug reproduction, coverage analysis, seeder testing, data-isolation validation. Does not modify production code to make tests pass (unless assigned); does not delete failing tests without documented cause; verifies demo cleanup cannot touch unrelated data.

## sre (`.opencode/agents/sre.md`)

Docker/Compose, CI/CD (GitHub Actions), env configuration, logging, health checks, deployment docs, reliability. Never commits secrets; keeps dev setup reproducible; ensures production cannot run destructive demo operations; avoids reading app internals unless needed for operational integration.

## Shared rules (all agents)

1. Read `AGENTS.md` first; keep context minimal.
2. One session per issue; finish with a concise handoff.
3. Add or update tests for every change.
4. Do not implement other agents' areas or backlog items outside the assigned issue.
5. Concise communication: summaries over reports.
6. Escalate conflicts (overlapping files, contract changes) in the issue instead of silently breaking others.
