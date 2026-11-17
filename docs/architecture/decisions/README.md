# Architecture decision records

Significant decisions are recorded here as short ADRs. Keep entries concise: context, decision, consequences.

## 001 — Monolithic architecture

- **Context:** Small team, evaluation-focused codebase, no microservices requirement.
- **Decision:** Single Django app + single Vue app. Extensibility via new Django apps and service modules.
- **Consequences:** Simple deployment; future modules must respect app boundaries.

## 002 — UUID primary keys

- **Context:** Tasks and users are exposed in URLs; sequential integers leak volume information.
- **Decision:** UUID v4 primary keys for `User` and `Task`.
- **Consequences:** Slightly larger indexes; safer public identifiers.

## 003 — Custom user model from day 1

- **Context:** Swapping Django's default user model after first migration is costly.
- **Decision:** `accounts.User` (UUID pk, email login, first/last name, timestamps) set as `AUTH_USER_MODEL` before the first migration.
- **Consequences:** All FK references use `settings.AUTH_USER_MODEL`.

## 004 — JWT with rotation and blacklist

- **Context:** Stateless SPA auth.
- **Decision:** SimpleJWT with access/refresh; refresh rotation enabled; logout blacklists the refresh token.
- **Consequences:** Requires blacklist app in DB; documented token lifetimes.

## 005 — Service layer for task business logic

- **Context:** Keep views/serializers thin; logic reusable outside HTTP.
- **Decision:** `apps/tasks/services.py` holds non-trivial operations; trivial CRUD stays in the viewset.
- **Consequences:** Services are unit-testable without HTTP; avoid premature abstraction.

## 006 — Demo seeders with ownership tagging

- **Context:** Repeatable demo data that must be removable without touching real data.
- **Decision:** Management commands built on `apps.core.base_seed.BaseSeedCommand`; demo users follow a stable `demo+<n>@taskflow.local` email convention; demo tasks are tagged via a module-level marker set (deterministic `demo_task_<key>` naming in descriptions? no — via a dedicated metadata module listing seeded task keys) so `--clear` removes only tagged records.
- **Consequences:** Idempotent reseeding; destructive ops guarded by environment checks and explicit confirmation; no extra fields on production models.

## 007 — Environment-split settings

- **Decision:** `config.settings.{base,dev,test,prod}` selected by `DJANGO_SETTINGS_MODULE` (compose/Makefile defaults).
- **Consequences:** Seeders and tests can detect environment (`settings.ENVIRONMENT`) for safety guards.
