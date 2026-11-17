---
id: TF-F06
title: "Improve responsive behavior for mobile task management"
agent: frontend
labels: ["agent:frontend", "type:refactor", "priority:low", "difficulty:medium", "status:ready"]
---

### Context

The layout is responsive at the grid level, but the task table is desktop-shaped (4 columns with fixed paddings), the task detail meta grid is dense on small screens, and touch targets in the nav are small.

### Objective

Make every primary page fully usable at 360px width: card-style task rows on mobile (instead of a cramped table), stacked detail meta, larger touch targets in navigation and pagination.

### Acceptance criteria

- [ ] At ≤640px the task list renders task rows as cards (title, badges, due date) while keeping the table on larger screens — same data source, no duplicate fetching.
- [ ] Task detail meta stacks to one column at mobile width; description readable without horizontal scroll.
- [ ] Nav and pagination controls meet a minimum 44px touch target.
- [ ] No horizontal page scroll at 360px on login, register, dashboard, list, detail, and form pages.
- [ ] No functional regressions (filters, pagination, actions all work on mobile layout).

### Technical notes

- Prefer CSS-level transformation (hidden columns / card variant per breakpoint) over JS branching to keep one source of truth for task data.
- Reuse `TaskBadge`; extract a `TaskCard` component shared between views if it avoids duplication.

### Testing expectations

- Vitest: `TaskCard` rendering.
- Playwright: viewport-size smoke test (360×800) for the task list rendering the card layout.

### Agent ownership

`frontend`
