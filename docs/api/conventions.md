# API conventions

Base URL: `http://localhost:8000/api/v1/` (versioned prefix mandatory).

## Authentication

- JWT bearer tokens: `Authorization: Bearer <access>`.
- Access token: 30 minutes (env `JWT_ACCESS_MINUTES`). Refresh token: 7 days (`JWT_REFRESH_DAYS`), rotation enabled.
- `POST /auth/login/` → `{access, refresh, user}`. `POST /auth/refresh/` → `{access, refresh}`.
- `POST /auth/logout/` blacklists the presented refresh token → `204`.

## Resources

### Auth

| Method | Path | Auth | Body | Success |
|---|---|---|---|---|
| POST | `/auth/register/` | public | `{email, password, first_name, last_name}` | 201 `{user}` (+tokens) |
| POST | `/auth/login/` | public | `{email, password}` | 200 `{access, refresh, user}` |
| POST | `/auth/refresh/` | public | `{refresh}` | 200 `{access, refresh}` |
| POST | `/auth/logout/` | JWT | `{refresh}` | 204 |
| GET | `/auth/me/` | JWT | — | 200 `{user}` |

### Tasks

Standard CRUD on `/tasks/` (list, create) and `/tasks/{uuid}/` (retrieve, update PUT/PATCH, delete). All require JWT; every query is scoped to `request.user` — cross-user access returns 404, not 403.

**List query params:**

- `status` (`todo|in_progress|done`) · `priority` (`low|medium|high`) — single values.
- `search` — matches title or description (case-insensitive).
- `ordering` — `created_at`, `due_date`, `priority`, prefix `-` for descending (e.g. `-due_date`).
- `page`, `page_size` (default 20, max 100).

**Response envelope:** DRF pagination `{count, next, previous, results}`.

**Task body:** `{title (required, ≤200), description (optional), status, priority, due_date (ISO 8601, optional)}`. Invalid enum values → 400 with field errors.

## Error shape

DRF defaults, consistently:

```json
{"field_name": ["Human readable error."]}
```

```json
{"detail": "Not found."}
```

`401` for missing/invalid credentials, `404` for missing or foreign resources, `400` for validation, `403` for authenticated-but-forbidden.

## Conventions for new endpoints

1. Never break existing field contracts; additive changes only (add fields/params, never rename).
2. Register new routes under `/api/v1/` with a versioned note in the docstring for drf-spectacular.
3. All request/response models must appear in the OpenAPI schema (`/api/schema/`, Swagger UI at `/api/docs/`).
4. Non-trivial logic goes to services; views stay thin.
5. Every new endpoint ships with pytest coverage (happy path + auth + validation + ownership).
