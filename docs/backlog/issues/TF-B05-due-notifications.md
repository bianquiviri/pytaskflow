---
id: TF-B05
title: "Implement due-date notifications infrastructure"
agent: backend
labels: ["agent:backend", "type:feature", "priority:low", "difficulty:hard", "status:ready"]
---

### Context

Tasks with approaching due dates are only visible on the dashboard. There is no infrastructure to notify owners about upcoming or overdue work, and the project intentionally has no background worker yet.

### Objective

Build the minimal, extensible notification infrastructure: a management command `notify_due_tasks` that finds tasks due within a configurable window (and overdue tasks) per owner and emits a notification record (DB model + command output), designed so a scheduler (cron/Celery beat) can call it later.

### Acceptance criteria

- [ ] `Notification` (or equivalent) model stores recipient, task reference, kind (upcoming/overdue), created_at, and read flag.
- [ ] `python manage.py notify_due_tasks --window-hours 24` creates one notification per (task, kind) and is idempotent: running twice does not duplicate notifications for the same task within the same period.
- [ ] Overdue tasks (past due date, not done) produce overdue notifications; tasks due within the window produce upcoming notifications; done tasks are skipped.
- [ ] The command respects production guard rails: it is safe to run in any environment but never seeds demo data.
- [ ] `docs/development/commands.md` documents the command and scheduling guidance.

### Technical notes

- No Celery in this issue: a plain management command callable by external cron is the agreed scope; document the extension path in `docs/architecture/decisions/`.
- Email delivery is explicitly out of scope (no credentials available).

### Testing expectations

- pytest coverage: upcoming/overdue/done classification, window boundaries (due exactly at window edge), idempotency, isolation (notifications reference only the correct owners' tasks).

### Agent ownership

`backend`
