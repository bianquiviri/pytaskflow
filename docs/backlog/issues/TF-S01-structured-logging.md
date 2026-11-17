---
id: TF-S01
title: "Add structured JSON application logging"
agent: sre
labels: ["agent:sre", "type:infrastructure", "priority:medium", "difficulty:easy", "status:ready"]
---

### Context

Logging is plain-text console output (`LOGGING` in `config/settings/base.py`). Production log aggregation (Grafana/Loki, Datadog, CloudWatch) needs machine-readable, request-correlated records.

### Objective

Emit structured JSON logs on stdout in production: request logs with method/path/status/duration, a request-ID middleware propagating `X-Request-ID`, and exception traces as JSON fields.

### Acceptance criteria

- [ ] `config.settings.prod` uses a JSON log formatter; `dev`/`test` keep human-readable output.
- [ ] Request-ID middleware: honors inbound `X-Request-ID` (sanitized, max length), generates a UUID otherwise, sets the response header, and includes the ID in every log record for the request.
- [ ] No secrets (passwords, tokens, auth headers) ever appear in logs — verified by a test grepping representative log output.
- [ ] Health-check endpoint requests do not spam logs (filtered or reduced level).
- [ ] Behavior documented in `docs/operations/deployment.md` with a sample JSON record.

### Technical notes

- Standard library `logging` + a small custom `Formatter` is enough; avoid adding structlog unless justified and documented.
- Implement the middleware in `apps/core/middleware.py` with tests (request-id generation, propagation, header echo).

### Testing expectations

- pytest: middleware unit tests; a settings-level test asserting the prod formatter is JSON.

### Agent ownership

`sre`
