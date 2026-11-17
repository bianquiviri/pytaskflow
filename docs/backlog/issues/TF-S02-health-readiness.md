---
id: TF-S02
title: "Add production-ready health and readiness checks"
agent: sre
labels: ["agent:sre", "type:infrastructure", "priority:high", "difficulty:easy", "status:ready"]
---

### Context

`GET /api/v1/health/` returns a static `{"status": "ok", "database": "ok"}` — it is a liveness probe, but it never fails when the database is down (the exception is swallowed), and there is no separate readiness semantics for load balancers.

### Objective

Split liveness and readiness: `/api/v1/health/` stays cheap and static (process is up), while `/api/v1/ready/` verifies database connectivity (and future dependencies) and returns 503 with a structured body when a dependency fails.

### Acceptance criteria

- [ ] `/api/v1/health/` — no DB call, always 200 when the process serves requests, suitable for container liveness.
- [ ] `/api/v1/ready/` — checks DB (`SELECT 1`) and returns 200 `{"ready": true}` or 503 `{"ready": false, "checks": {"database": false}}`; responds quickly (hard timeout ~2s on checks).
- [ ] Both endpoints are public (no auth) and excluded from request logging noise (see TF-S01, not a hard dependency).
- [ ] Compose healthchecks updated: backend container readiness uses `/api/v1/ready/`; CI E2E waits on it.
- [ ] Documented in `docs/operations/deployment.md` with load-balancer guidance.

### Technical notes

- Keep exception handling broad but bounded (timeout via a short query); never leak exception details in the 503 body.

### Testing expectations

- pytest: ready → 200 with DB; ready → 503 when DB unreachable (mock the connection); health stays 200 with DB down.

### Agent ownership

`sre`
