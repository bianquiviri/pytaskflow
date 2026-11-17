---
id: TF-Q02
title: "Add concurrency and race-condition tests"
agent: qa
labels: ["agent:qa", "type:test", "priority:medium", "difficulty:hard", "status:ready"]
---

### Context

Nothing tests concurrent behavior: two updates to the same task, a delete racing with an update, duplicate registration submissions, or simultaneous refresh-token rotation. Django's transaction model makes several of these safe today, but nothing proves it — and rotation+blacklist races are a real risk area.

### Objective

Add tests that exercise concurrency hazards deterministically (threads, transactions, or interleaved calls) and document actual behavior of each.

### Acceptance criteria

- [ ] Test: two concurrent PATCHes on the same task both succeed or one fails cleanly (no 500); final state consistent (document last-write-wins semantics).
- [ ] Test: DELETE racing with PATCH — no orphaned/ghost task; response is 204 or 404, never 500.
- [ ] Test: duplicate registration racing (same email twice) — at most one account created, the loser gets a clean 400.
- [ ] Test: same refresh token used twice concurrently — at most one rotation succeeds; the other gets 401; the access token remains valid for the winner.
- [ ] All tests deterministic (no sleeps; use barriers/events for synchronization).

### Technical notes

- Use `transaction.atomic` + `TestCase.captureOnCommitCallbacks` or raw `django.test.TransactionTestCase` with threads where DB-level isolation matters; `--reuse-db` must keep working.
- Postgres is required for realistic behavior; document any test that behaves differently on SQLite (the local fallback is NOT used for these).

### Testing expectations

- New pytest module `tests/api/test_concurrency.py`; report executed commands and results; note any flakiness rather than papering over it.

### Agent ownership

`qa`
