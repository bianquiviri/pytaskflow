# Backend architecture

## Stack

Django 5 · Django REST Framework · PostgreSQL (psycopg) · `djangorestframework-simplejwt` (JWT) · `drf-spectacular` (OpenAPI) · pytest/pytest-django · Factory Boy · Ruff.

## Project layout

```
backend/
  manage.py
  pyproject.toml
  config/
    settings/   base.py dev.py test.py prod.py
    urls.py     root urlconf (/api/v1/, /api/schema, /api/docs)
    asgi.py wsgi.py
  apps/
    __init__.py
    core/       shared base command, health view, pagination class
    accounts/   User model, manager, auth endpoints
    tasks/      Task model, serializers, permissions, services, viewset
  tests/
    conftest.py factories/  unit/  api/  seeders/
```

## Key components

### `apps.accounts`
- `User(AbstractBaseUser, PermissionsMixin)` — UUID pk, unique email (login), first/last name, `is_active`, `created_at`, `updated_at`. Manager requires email. `AUTH_USER_MODEL = "accounts.User"` set from the first migration.
- API: register, login, refresh, logout (blacklists refresh token), me. All under `/api/v1/auth/`.

### `apps.tasks`
- `Task` — UUID pk, title, optional description, `status ∈ {TODO, IN_PROGRESS, DONE}`, `priority ∈ {LOW, MEDIUM, HIGH}`, optional `due_date`, FK `owner` (deletion cascade), timestamps. Indexes on `(owner, status)`, `(owner, priority)`, `due_date`. Default ordering `-created_at`.
- `serializers.py` — input validation (choices, field lengths); no business rules.
- `services.py` — non-trivial operations (e.g., `create_task_for_owner`, `update_task` ownership-aware, status transition helpers). Trivial CRUD stays in the viewset.
- `permissions.py` — `IsOwner`: object-level check that `obj.owner == request.user`.

### `apps.core`
- `BaseSeedCommand` — shared management-command base: environment guard, count options, idempotency helpers, `--clear` handling. Used by `accounts` and `tasks` seeders.
- Health endpoints (public, no auth): `GET /api/v1/health/` liveness — static `{"status": "ok"}`, never touches the DB; `GET /api/v1/ready/` readiness — runs `SELECT 1` (2s hard timeout) and returns 200 `{"ready": true, ...}` or 503 `{"ready": false, "checks": {"database": false}}`.
- `SmallResultsPagination` (default page size 20, `page_size` query param up to 100).

## API surface (`/api/v1/`)

- `auth/register/`, `auth/login/`, `auth/refresh/`, `auth/logout/`, `auth/me/`
- `tasks/` + `tasks/{id}/` (GET/PUT/PATCH/DELETE) — list supports `status`, `priority`, `search`, `ordering` filters.
- `health/` (liveness) and `ready/` (readiness)
- OpenAPI: `/api/schema/` and Swagger UI `/api/docs/` (drf-spectacular).

Authentication uses `SimpleJWT` bearer tokens: access token default 30 min, refresh 7 days (configurable via env). Refresh rotation enabled with blacklisting on logout.

## Conventions

- Ruff for lint + format (`pyproject.toml` section).
- Errors use DRF's standard body shape (`{"field": ["message"]}` / `{"detail": "..."}`) — documented in `docs/api/conventions.md`.
- Tests use a dedicated test database; password hasher switched to MD5 for speed in `config.settings.test`.
- Never expose password hashes; registration/login responses return only user profile fields and tokens.
