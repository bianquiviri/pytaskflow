---
id: TF-F05
title: "Keyboard navigation and accessibility improvements"
agent: frontend
labels: ["agent:frontend", "type:feature", "priority:medium", "difficulty:medium", "status:ready"]
---

### Context

Core forms use semantic labels, but there is no systematic keyboard flow: no skip link, no visible focus styles beyond browser defaults, modals trap no focus, and table rows are only reachable by tabbing through every link.

### Objective

Bring the app to a consistent accessibility baseline: skip-to-content link, visible focus rings, focus trap + Escape handling in `BaseModal`, ARIA roles on the task table, and keyboard shortcuts for primary actions (e.g., `n` → new task on the list page).

### Acceptance criteria

- [ ] Skip-to-content link appears on first Tab press and jumps to `main`.
- [ ] `BaseModal` traps focus while open, restores focus to the trigger on close, and closes on Escape.
- [ ] Task table has proper `<caption>`/`scope` semantics and row actions reachable by keyboard in a logical order.
- [ ] Status/priority badges expose accessible names (not color-only).
- [ ] Documented keyboard shortcuts don't collide with browser defaults and are listed in a help affordance or README note.
- [ ] No form control relies on placeholder as its only label.

### Technical notes

- Avoid adding large a11y libraries; implement the focus trap manually in `BaseModal` (small, testable).
- Audit with keyboard only + browser dev tools; document findings in the issue while working.

### Testing expectations

- Vitest: modal focus trap and Escape behavior.
- Playwright: tab order smoke on login and task list pages.

### Agent ownership

`frontend`
