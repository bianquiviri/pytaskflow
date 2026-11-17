# Local development setup

## Prerequisites

- Docker + Docker Compose (recommended path)
- OR locally: Python 3.13 (`python3.13`), Node.js ≥ 20 (Node 24 used in CI), GNU Make
- For E2E: Playwright browsers (`npx playwright install chromium`)

## Option A — Docker (recommended)

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_data
```

- Backend: http://localhost:8000 (Swagger: http://localhost:8000/api/docs/)
- Frontend: http://localhost:5173
- Demo login: `demo1@taskflow.local` / value of `SEED_DEMO_PASSWORD` (default `demo-password-123`)

Stop: `docker compose down` (add `-v` to drop the database volume — destructive).

## Option B — Local processes

Backend (Python 3.13):

```bash
cd backend
python3.13 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp ../.env.example .env   # or export variables; dev settings read env first
python manage.py migrate
python manage.py runserver
```

Requires a PostgreSQL instance reachable at `DB_HOST`/`DB_PORT` (the compose `db` service works alone: `docker compose up -d db`).

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Environment variables

Copy `.env.example` → `.env`. Key variables: `SECRET_KEY`, `DEBUG`, `DB_*`, `JWT_*`, `VITE_API_BASE_URL`, `SEED_DEMO_PASSWORD`, `SEED_CONFIRM_DESTRUCTIVE`. Never commit `.env`.

## Migrations

```bash
make migrate        # apply
make migrations     # create after model changes (run inside backend container)
```

## Common issues

- **Port conflicts** (5432/8000/5173): stop local Postgres or change the compose port mapping.
- **`connection refused` on db**: wait for the healthcheck; the backend depends on `db: condition: service_healthy`.
- **Auth 401 in frontend**: check `VITE_API_BASE_URL` matches the backend origin and CORS list in `.env`.
