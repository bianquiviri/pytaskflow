# Testing strategy

## Backend — pytest + pytest-django

Config in `backend/pyproject.toml` (`[tool.pytest.ini_options]`): `DJANGO_SETTINGS_MODULE = config.settings.test`, testpath `tests`, DB creation per session.

Suites:

- `tests/unit/` — services, model behavior (validation, ordering, defaults), serializers.
- `tests/api/` — registration, login/refresh/logout, `/me`, task CRUD, filtering, pagination, permissions, user-data isolation (user A cannot read/modify/delete user B's tasks), invalid identifiers, error shapes, auth throttling (429s).
- `tests/seeders/` — seeder orchestration, idempotency, counts, cleanup safety, production protection.

Rate limiting in tests: `config.settings.test` sets `DEFAULT_THROTTLE_CLASSES = ()`, so throttling is off for the entire suite and no regular test needs an override. `tests/api/test_throttling.py` opts back in per test with `throttling_at(...)`, which patches DRF 3.18's import-time snapshots (`APIView.throttle_classes` and `SimpleRateThrottle.THROTTLE_RATES`) — `override_settings(REST_FRAMEWORK=...)` alone would not affect throttle behavior. A cache cleared in an autouse fixture plus `ScopedRateThrottle`'s per-ident counting make the (N+1)-th request trip an `N/min` rate instantly, so no wall-clock sleeps are involved.

Factories live in `tests/factories/` (Factory Boy). Demo-data generators are separate and never imported by tests except the seeder tests.

```bash
cd backend && python -m pytest                     # full suite
python -m pytest tests/api/test_tasks.py           # focused
```

## Frontend — Vitest + Vue Test Utils

```bash
cd frontend && npm run test        # vitest (watch: npm run test:watch)
```

Coverage targets: stores (auth state, task list), components (rendering, validation), composables, router guard. API modules are mocked; no real network in unit tests.

## E2E — Playwright

```bash
cd frontend && npm run test:e2e    # requires running backend + frontend (or `npm run e2e` with webServer config)
```

Scenarios: register, login, create task, edit task, change status, delete task, route protection for unauthenticated users.

## Quality rules

- Tests are repeatable and never depend on production/demo data.
- Never report a passing suite that was not executed.
- Never weaken assertions to make code pass; fix the code or document the defect.
- CI runs backend (Ruff + pytest with Postgres service) and frontend (lint + typecheck + tests + build) on every PR; E2E runs the full compose stack.
