# Deployment & operations

## Environments

`ENVIRONMENT` ∈ `development | test | staging | production` (read by Django settings and seeders).

- development — Docker Compose, DEBUG on, demo seeding allowed.
- test — CI; isolated DB; seeding allowed for seeder tests only.
- production — DEBUG off, strong `SECRET_KEY`, strict `ALLOWED_HOSTS`, demo seeding hard-refused.

## Container images

- Backend: `infra/docker/Dockerfile.backend` (Python 3.13 slim, gunicorn in production mode, non-root user).
- Frontend: `infra/docker/Dockerfile.frontend` (Node 24 build stage → Nginx serving `dist/` with SPA fallback).

## Production notes (checklist)

1. Provision PostgreSQL 16 with its own credentials; enable backups before go-live.
2. Set env vars: `SECRET_KEY` (50+ random chars), `DEBUG=False`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, DB credentials, `JWT_*` lifetimes.
3. `python manage.py migrate` before rolling the new image; use `--check` in pipelines to detect missing migrations.
4. Serve behind TLS; terminate at the proxy; forward `X-Forwarded-*` headers.
5. Health endpoints (both public, unauthenticated):
   - `/api/v1/health/` — **liveness**: always 200 while the process serves requests; no dependency checks. Wire container/orchestrator liveness probes here (Docker `HEALTHCHECK`, Kubernetes `livenessProbe`). Never route traffic here — a live process is not necessarily able to serve it.
   - `/api/v1/ready/` — **readiness**: verifies dependencies (`SELECT 1` against PostgreSQL, 2s hard timeout) and returns 200 `{"ready": true, "checks": {"database": true}}` or 503 `{"ready": false, "checks": {"database": false}}`. Wire load balancers / ingress (Kubernetes `readinessProbe`) to it: on 503 the instance is pulled out of rotation until checks pass again. The 503 body never contains exception details.
   - Docker Compose backend healthcheck and the CI E2E wait step both use `/api/v1/ready/`.
6. Logging: structured JSON on stdout (configured in prod settings); aggregate with your platform of choice.
7. Never run `seed_data --clear` against production; the command refuses, but also exclude it from production images' documented runbook.

## CI/CD

GitHub Actions (`.github/workflows/`): backend (lint + tests with Postgres service), frontend (lint + typecheck + tests + build), e2e (compose stack + Playwright artifacts on failure). Workflows fail on any check failure.

## Demo data in shared environments

`staging` may receive demo data only by explicit, documented operator action; production never.
