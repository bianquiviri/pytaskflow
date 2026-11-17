---
id: TF-F02
title: "Improve dashboard visualizations"
agent: frontend
labels: ["agent:frontend", "type:feature", "priority:low", "difficulty:medium", "status:ready"]
---

### Context

The dashboard shows five numeric cards fed by real API data. There is no trend, no breakdown by priority, and no due-date awareness beyond "upcoming due dates" being absent entirely — the metric list promised in the UI design (upcoming due dates) is missing from the card grid.

### Objective

Enrich the dashboard: an "upcoming / overdue" panel listing the next tasks by due date (real data from the tasks list API), a priority breakdown bar, and skeleton/empty/error states kept consistent.

### Acceptance criteria

- [ ] New "Upcoming & overdue" section lists up to 5 tasks ordered by `due_date` (overdue first, then soonest) using real API data, linking to task detail pages.
- [ ] Priority breakdown renders proportions of low/medium/high from real data; no hardcoded numbers.
- [ ] Empty states are friendly and actionable; loading shows skeletons; API failure shows the error banner with a retry action.
- [ ] Metrics remain derived from the API (no second backend change required; reuse `fetchDashboardMetrics` + a `listTasks` ordering query).
- [ ] Mobile layout stacks correctly at `sm:` breakpoint.

### Technical notes

- Reuse `Badge`, `BaseCard`; extract a `DashboardMetricCard` component if it reduces duplication.
- Keep API access inside stores/composables; pages compose components only.

### Testing expectations

- Vitest: component rendering with mocked API data (tasks present, empty list, API failure).
- Playwright: dashboard shows sections after login with seeded demo data available.

### Agent ownership

`frontend`
