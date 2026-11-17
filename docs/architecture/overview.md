# Architecture overview

TaskFlow is a monolithic full-stack application with two independently maintainable applications: a Django REST backend and a Vue 3 frontend. They communicate exclusively through the versioned REST API (`/api/v1/`) using JWT bearer tokens.

## High-level diagram

```
┌──────────────┐  HTTPS/HTTP   ┌────────────────────┐  psycopg   ┌────────────┐
│  Vue 3 (SPA) │ ────────────▶ │ Django 5 + DRF     │ ─────────▶ │ PostgreSQL │
│  Vite/Pinia  │   /api/v1/*   │ JWT + services     │            │   16       │
│  Tailwind    │ ◀──────────── │ drf-spectacular    │            └────────────┘
└──────────────┘    JWT JSON   └────────────────────┘
```

## Layers

- **Backend**: HTTP layer (views/serializers/permissions) stays thin. Non-trivial business rules live in `apps/tasks/services.py`. Models own validation and DB-level integrity (indexes, ordering, constraints).
- **Frontend**: Pages compose reusable components; domain state lives in Pinia stores; HTTP calls live in `src/api/` clients; pages never call Axios directly.
- **Boundaries**: The frontend imports only API contracts (`docs/api/conventions.md`, OpenAPI schema), never backend internals. The backend never depends on frontend build artifacts.

## Cross-cutting decisions

| Decision | Rationale | ADR |
|---|---|---|
| Monolith (no microservices) | Small team, evaluation codebase; extensibility via modular apps | `decisions/001-monolith.md` |
| UUID primary keys | Non-enumerable public identifiers | `decisions/002-uuid-pks.md` |
| Email-as-username custom user from day 1 | Avoids the painful default-User migration later | `decisions/003-custom-user.md` |
| JWT access + refresh with rotation | Stateless auth, short access windows | `decisions/004-jwt.md` |
| Service layer for task business logic | Keeps views/serializers thin, logic testable without HTTP | `decisions/005-service-layer.md` |
| Demo seeders as management commands with ownership tagging | Repeatable, idempotent, safely removable demo data | `decisions/006-seeders.md` |

Future modules (notifications, bulk operations, activity history — see `docs/backlog/`) should integrate through new apps/services, not by expanding existing ones.

## Environments

- `config.settings.base` — shared settings.
- `config.settings.dev` — development: DEBUG, CORS for Vite dev server, verbose logging.
- `config.settings.test` — testing: isolated test database, faster password hasher.
- `config.settings.prod` — production: no DEBUG, strict secrets, no demo-seed operations (hard-refused by seeders).

Environment-specific values come from environment variables (see `.env.example`).
