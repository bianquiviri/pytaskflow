# TaskFlow

Task and project management platform — and a realistic full-stack codebase for evaluating AI coding agents through GitHub issues.

- **Backend**: Django 5 + Django REST Framework, PostgreSQL, JWT auth, OpenAPI (Swagger UI), pytest.
- **Frontend**: Vue 3 + TypeScript + Vite, Pinia, Vue Router, Tailwind CSS, Vitest, Playwright.
- **Agents**: Four OpenCode agents (backend, frontend, qa, sre) with persistent project memory in `AGENTS.md`.
- **License**: BSD-2-Clause (see [`LICENSE`](LICENSE)).

## Repository structure

```
taskflow/
├── AGENTS.md            # persistent project memory (read first)
├── backend/             # Django project (config/, apps/, tests/)
├── frontend/            # Vue 3 SPA (src/, tests/)
├── infra/               # docker files, scripts, GitHub issue config
├── docs/                # architecture, api, development, agents, backlog, operations
├── .opencode/agents/    # specialized agent definitions
├── .github/workflows/   # CI: backend, frontend, e2e
├── docker-compose.yml   # dev stack: postgres + backend + frontend
└── Makefile             # developer commands
```

## Prerequisites

- Docker + Docker Compose **or** local Python 3.13 + Node.js ≥ 20 + a PostgreSQL instance
- For E2E tests: Playwright browsers (`npx playwright install chromium`)

## Quick start (Docker)

```bash
cp .env.example .env          # safe development defaults
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_data
```

| Service | URL |
|---|---|
| Backend API | http://localhost:8000/api/v1/ |
| Swagger UI | http://localhost:8000/api/docs/ |
| Frontend | http://localhost:5173 (or `$FRONTEND_PORT`) |

> If ports 5432/5173 are already in use on your machine, set `DB_PORT_HOST` / `FRONTEND_PORT` in `.env` — Django/seeders read `DB_PORT` for local (non-container) runs.

Demo login: `demo1@taskflow.local` / `demo-password-123` (value of `SEED_DEMO_PASSWORD`; development only — never reuse in production).

## Local development (no full Docker stack)

```bash
# backend (PostgreSQL reachable at DB_HOST/DB_PORT)
cd backend
python3.13 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python manage.py migrate && python manage.py runserver

# frontend
cd frontend && npm install && npm run dev
```

## Database seeders (demo data)

Seeders are idempotent management commands for **demo data** (not test fixtures):

```bash
make seed                     # or: docker compose exec backend python manage.py seed_data
python manage.py seed_data --users 10 --tasks 100
python manage.py seed_users --count 10
python manage.py seed_tasks --count 100
make clear-demo               # removes ONLY demo records (needs SEED_CONFIRM_DESTRUCTIVE=yes)
```

Demo users follow `demo<n>@taskflow.local`; cleanup removes only records identified as demo data and is refused in production. Details: [`docs/development/seeders.md`](docs/development/seeders.md).

## Tests

```bash
make backend-test      # pytest (backend/)
make frontend-test     # vitest (frontend/)
make e2e               # Playwright — requires the stack running
make lint              # ruff + eslint + vue-tsc
```

CI runs these on every PR (`.github/workflows/`).

## API documentation

- Swagger UI: http://localhost:8000/api/docs/
- OpenAPI schema: http://localhost:8000/api/schema/
- Conventions: [`docs/api/conventions.md`](docs/api/conventions.md)

## OpenCode agents

Agents live in `.opencode/agents/` (OpenCode v2 markdown format) and follow `AGENTS.md`:

| Agent | File | Scope |
|---|---|---|
| backend | `.opencode/agents/backend.md` | Django/DRF, auth, seeders, backend tests |
| frontend | `.opencode/agents/frontend.md` | Vue/TS UI, stores, API integration |
| qa | `.opencode/agents/qa.md` | Test strategy, regression, E2E, isolation checks |
| sre | `.opencode/agents/sre.md` | Docker, CI, env config, reliability |

Project config (`opencode.json`) enables automatic context compaction and tighter tool-output truncation for token-efficient sessions.

## GitHub backlog

24 issue definitions live locally in `docs/backlog/issues/`. Publishing to GitHub is **explicit and manual**:

```bash
./infra/scripts/publish_backlog.sh --dry-run   # validate without changes
./infra/scripts/publish_backlog.sh             # create labels + issues (idempotent)
```

Requires `gh` installed, `gh auth login`, and a git remote pointing to GitHub. Issues are assigned only when a real GitHub username is configured in [`infra/github/agent-assignees.yml`](infra/github/agent-assignees.yml); otherwise the `agent:*` label marks ownership.

## Documentation

- Architecture: [`docs/architecture/`](docs/architecture/overview.md) (+ ADRs in `decisions/`)
- Setup / testing / seeders / commands: [`docs/development/`](docs/development/setup.md)
- Agent workflow: [`docs/agents/workflow.md`](docs/agents/workflow.md)
- Deployment & operations: [`docs/operations/deployment.md`](docs/operations/deployment.md)

## Contributing

1. Work from a GitHub issue (`docs/backlog/issues/` once published).
2. One agent/session per issue; add or update tests for every change.
3. Backend: `ruff check .` + `pytest` must pass. Frontend: `eslint` + `vue-tsc` + `vitest` must pass.
4. Conventional commits (`feat:`, `fix:`, `test:`, `docs:`, `chore:`).

## License

BSD-2-Clause — see [`LICENSE`](LICENSE). Third-party dependencies keep their own licenses; nothing in this repository replaces their terms.
