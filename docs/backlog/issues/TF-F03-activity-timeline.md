---
id: TF-F03
title: "Add task activity timeline to task detail page"
agent: frontend
labels: ["agent:frontend", "type:feature", "priority:medium", "difficulty:medium", "status:blocked"]
---

### Context

Task detail shows static fields. Backend issue TF-B03 adds a `GET /tasks/{id}/events/` activity feed; the frontend needs to render it once that endpoint exists.

### Objective

Render a chronological activity timeline on the task detail page from the events API (created, status changed, priority changed, edited, restored, deleted), with pagination ("load more").

### Acceptance criteria

- [ ] Timeline lists events newest-first with event icon/label and relative timestamps; falls back to a friendly "No activity yet" empty state.
- [ ] Handles API absence gracefully while TF-B03 is not merged (feature-flagged or 404 → hidden section, no crash) so this can merge before or after backend work.
- [ ] Pagination via "Load more" wired to the paginated events response.
- [ ] All data from `src/api/` clients; loading and error states included.
- [ ] Cross-user protection respected (foreign task → 404 page state as today).

### Technical notes

- Depends on TF-B03 response shape; agree the contract in the issue comments before implementing.
- Add a typed `TaskEvent` interface in `src/types/` mirroring the API contract.

### Testing expectations

- Vitest: timeline rendering from mocked events, empty state, error state.
- Playwright: (after backend merge) edit a task and see the timeline update.

### Agent ownership

`frontend`
