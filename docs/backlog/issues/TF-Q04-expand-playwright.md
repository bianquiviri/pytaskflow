---
id: TF-Q04
title: "Expand Playwright user workflow coverage"
agent: qa
labels: ["agent:qa", "type:test", "priority:medium", "difficulty:medium", "status:ready"]
---

### Context

E2E covers register, login, one CRUD flow, and route protection. Missing: filter/search interactions, pagination, session persistence across reloads, expired-token recovery, and error states (e.g., backend briefly unavailable).

### Objective

Add Playwright scenarios for the remaining user-visible flows, using seeded demo data patterns rather than UI-created fixtures where faster.

### Acceptance criteria

- [ ] Scenario: filter by status/priority and search — results update and empty state shows when nothing matches.
- [ ] Scenario: pagination — create 25+ tasks via API (fast path), verify page 2 works and page indicators are correct.
- [ ] Scenario: reload the page after login — session persists; logout clears it (verified by reload hitting /login).
- [ ] Scenario: 401 recovery — expire/revoke the access token via API, trigger an authenticated action, observe transparent refresh or a clean redirect to login (document which).
- [ ] Every scenario is independent, cleans up or uses unique accounts, and runs green locally with the documented command.

### Technical notes

- Use `request` context fixture for API setup/teardown; keep UI steps minimal.
- Respect `E2E_BASE_URL`/`E2E_API_URL` env overrides from `playwright.config.ts`.

### Testing expectations

- New spec files under `frontend/tests/e2e/`; executed against the compose stack with output reported.

### Agent ownership

`qa`
