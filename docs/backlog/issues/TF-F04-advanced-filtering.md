---
id: TF-F04
title: "Implement advanced task filtering in the task list"
agent: frontend
labels: ["agent:frontend", "type:feature", "priority:medium", "difficulty:medium", "status:ready"]
---

### Context

The task list offers single-value status/priority selects, search, and ordering. Users cannot combine filters fluidly or clear them quickly, and filter state is lost when navigating away.

### Objective

Upgrade filtering UX: multi-select status/priority chips, due-date bucket filter (overdue / today / this week / none), filter state synced to the URL query string, and a one-click "clear all" affordance.

### Acceptance criteria

- [ ] Selecting multiple statuses/priorities composes a single API request; UI reflects active filters as removable chips.
- [ ] URL query params (`?status=todo,done&priority=high`) restore filter state on reload and back-navigation.
- [ ] "Clear all" resets to defaults without a full page reload.
- [ ] Requests are debounced for search (existing `useDebouncedRef` reused) and no duplicate in-flight requests race (cancel or ignore superseded).
- [ ] Loading/empty states reflect filter results ("No tasks match these filters" distinct from "No tasks yet").
- [ ] Works with backend multi-value filters when TF-B04 lands; before that, multi-select can degrade to sequential single-value requests client-side (document interim behavior).

### Technical notes

- Centralize filter → query-param mapping in `useTasksStore` or a composable so table and future board views share it.
- Update `docs/architecture/frontend.md` data-flow notes if the store contract changes.

### Testing expectations

- Vitest: filter composition, URL sync, clear-all behavior.
- Playwright: apply filters, reload, assert preserved state and results.

### Agent ownership

`frontend`
