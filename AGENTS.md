# AGENTS.md — TaskFlow project memory

Read this file before any task. It is the central, persistent project memory.

## Purpose

TaskFlow is a task and project management platform, and a realistic evaluation codebase for AI coding agents. Backend and frontend are independent applications communicating over a versioned REST API.

## Architecture

- **backend/** — Django 5 + DRF, PostgreSQL, JWT auth (`djangorestframework-simplejwt`), OpenAPI via `drf-spectacular`, pytest. Custom `User` model (UUID pk, email login) in `apps/accounts`. Tasks in `apps/tasks`. Shared utilities in `apps/core`. API lives under `/api/v1/`. Business rules live in `apps/tasks/services.py`, not in views/serializers.
- **frontend/** — Vue 3 + TypeScript + Vite, Pinia stores, Vue Router (protected routes), Tailwind CSS, Axios. API clients in `src/api/`, domain types in `src/types/`, tests in Vitest, E2E in Playwright.
- **infra/** — Docker files, scripts, GitHub issue configuration.
- **docs/** — Detailed documentation (see map below). Do not load every doc; read only what the current issue requires.
- **.opencode/agents/** — Specialized agent definitions: backend, frontend, qa, sre.
- **docs/backlog/issues/** — Local GitHub issue definitions + publishing script `infra/scripts/publish_backlog.sh`.

## Directory map

```
backend/
  config/            settings (base/dev/test/prod), urls, wsgi/asgi, celery absent
  apps/accounts/     custom User model, auth API
  apps/core/         shared utilities, base management command, health endpoint
  apps/tasks/        Task model, serializers, services, views, permissions
  tests/             pytest suite (unit, api, seeders)
  pyproject.toml     dependencies + tool config (pytest, ruff)
frontend/
  src/api/ axios clients · src/stores/ pinia · src/pages/ · src/components/ · src/types/
docs/
  architecture/  overview, backend, frontend, decisions/
  api/           conventions
  development/   setup, testing, commands, seeders
  agents/        workflow, responsibilities
  backlog/issues/  local issue definitions (one markdown per issue)
  operations/    deployment
```

## Conventions

- Backend: Ruff lint/format, type hints where practical, services for non-trivial logic, DRF viewsets + routers, URL names use `-` not `_` namespacing via `apps/`.
- Frontend: TypeScript strict, components PascalCase, composables `use*`, stores per domain, no hardcoded API data.
- Commits: conventional style (`feat:`, `fix:`, `test:`, `docs:`, `chore:`).
- Security: never commit secrets; never expose password hashes; task endpoints enforce object-level ownership; demo seeding is forbidden in production.

## Commands

See `docs/development/commands.md` for the complete list. Quick reference:

```bash
docker compose up -d --build          # start stack (Postgres + Django + Vite)
make migrate                          # apply migrations
make seed                             # seed demo data (idempotent, dev only)
make backend-test                     # pytest (backend)
make frontend-test                    # vitest (frontend)
make e2e                              # Playwright
make lint                             # ruff + eslint + vue-tsc
```

Local (no Docker) backend: `cd backend && python3.13 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]" && python manage.py migrate && python manage.py runserver`. Tests use a separate settings module (`config.settings.test`) with its own database name.

## Agent rules

1. One independent session per GitHub issue when practical.
2. Read `AGENTS.md`, then the assigned issue, then only the code/docs relevant to it.
3. Agents have scoped definitions in `.opencode/agents/{backend,frontend,qa,sre}.md` — follow your role's boundaries.
4. Run focused tests first; run full suite when justified. Never claim tests passed without running them.
5. Do not implement items from `docs/backlog/` during unrelated tasks.
6. Update docs when an architectural decision changes (`docs/architecture/decisions/`).
7. Session handoff: concise summary — issue, changes, files, test results, remaining work.

## Token efficiency

- Inspect targeted files, not entire directories.
- Do not reread unchanged files or repeat the project specification.
- Prefer concise summaries over long reports.
- Never trade correctness, security, or test coverage for fewer tokens.

## Detailed documentation

- Architecture: `docs/architecture/overview.md` (+ `backend.md`, `frontend.md`, `decisions/`)
- API conventions: `docs/api/conventions.md`
- Setup/testing/seeders/commands: `docs/development/{setup,testing,seeders,commands}.md`
- Agent workflow and responsibilities: `docs/agents/{workflow,responsibilities}.md`
- Backlog publishing: `docs/agents/workflow.md`, `infra/scripts/publish_backlog.sh`
- Operations: `docs/operations/deployment.md`

## License

BSD-2-Clause (see `LICENSE`). Third-party dependencies keep their own licenses.
