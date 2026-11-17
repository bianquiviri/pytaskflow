---
id: TF-F01
title: "Add drag-and-drop task organization on the task list"
agent: frontend
labels: ["agent:frontend", "type:feature", "priority:medium", "difficulty:hard", "status:ready"]
---

### Context

The task list is a static table sorted by explicit filters/ordering. Users reorganize work visually (move between status columns) but must edit each task individually.

### Objective

Add drag-and-drop reordering/grouping of tasks by status on a board-style view of the existing task list, persisting each move through the API.

### Acceptance criteria

- [ ] A board view (columns To do / In progress / Done) is reachable from the task list without replacing the table view (toggle persisted in the store).
- [ ] Dragging a card to another column issues `PATCH /tasks/{id}/ {"status": ...}` and reflects optimistic UI state, with rollback + error banner if the request fails.
- [ ] Only the authenticated user's tasks appear; pagination interacts sanely (e.g., board works with up to the page size; document behavior beyond it).
- [ ] Keyboard-accessible alternative exists (move between columns via buttons/menu) so DnD is not the only way to change status.
- [ ] Loading, empty, and error states are handled; no layout regression on mobile.

### Technical notes

- Do not add a heavyweight DnD dependency unless justified; evaluate native HTML5 drag events first and document the decision.
- Reuse `useTasksStore` and `src/api/tasks.ts`; no direct Axios calls in components.

### Testing expectations

- Vitest: board rendering, optimistic update + rollback on API failure.
- Playwright: change status via the keyboard alternative; drag simulation where feasible in headless Chromium.

### Agent ownership

`frontend`
