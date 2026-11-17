# Database seeders & demo data

Seeders are **management commands for demo data** — not test fixtures. Automated tests use Factory Boy factories instead.

## Commands

```bash
python manage.py seed_data                     # users (default 5) + tasks (default 40)
python manage.py seed_data --users 10 --tasks 100
python manage.py seed_data --users 20 --tasks 500
python manage.py seed_users --count 10
python manage.py seed_tasks --count 100
python manage.py seed_data --clear             # remove ONLY demo records
```

Docker equivalents: `make seed`, `make seed-users`, `make seed-tasks`, `make clear-demo`.

## Implementation

- `apps.core.management.base_seed.BaseSeedCommand` — shared base: env guard, options (`--count/--users/--tasks/--clear`), styled output, transaction wrapping.
- `apps/accounts/management/commands/seed_users.py` — creates demo users.
- `apps/tasks/management/commands/seed_tasks.py` — creates demo tasks owned by demo users.
- `apps/tasks/seed/demo_tasks.py` — deterministic demo task catalog (titles/descriptions/status/priority/due-date spread) used to generate varied, repeatable records.
- `seed_data.py` orchestrates both in order.

## Demo accounts

- Emails: `demo1@taskflow.local`, `demo2@taskflow.local`, … up to `--users`.
- Password: `SEED_DEMO_PASSWORD` env var, default `demo-password-123` (**development only — never reuse in production**).
- Login with any demo email + that password; each user only sees their own tasks (verify isolation in the UI).

## Generated task variety

All statuses × all priorities; with/without description; due dates in the past / today / upcoming / absent; multiple owners; enough volume for pagination, filtering, ordering and dashboard metrics (targets: past-due ≥ 10%, due-today bucket, high-priority ≥ 20%).

## Idempotency

- Seeder runs detect existing demo records by the stable email domain `@taskflow.local` and the deterministic demo catalog keys. Re-running **never duplicates** records and never touches non-demo data.
- `--count/--users/--tasks` ensure minimum counts; existing demo records count toward the target.

## Cleanup (`--clear`)

- Removes only users matching the demo email convention and only tasks whose marker belongs to the demo catalog. Unrelated records are untouched.
- Refuses to run when `settings.ENVIRONMENT` is `production` (hard error) or when confirmation env `SEED_CONFIRM_DESTRUCTIVE != "yes"`. Warns clearly on refusal. No blanket `flush` is ever used.

## Environment rules

- Allowed freely: `development` (and CI `test`).
- `production`: all seeding (including non-destructive) is refused with a clear error.

## Adding a new seeder

1. Add a catalog module under the owning app (`apps/<app>/seed/`).
2. Create a command extending `BaseSeedCommand`; implement `run_seed(count)` and `run_clear()` with the same demo-marker strategy.
3. Register it in `seed_data` orchestration.
4. Add tests: idempotency, counts, cleanup safety, environment guard.

## Troubleshooting

- **"Seeding is not allowed in production"** — check `ENVIRONMENT` env var.
- **"Refusing destructive cleanup"** — set `SEED_CONFIRM_DESTRUCTIVE=yes`.
- **Zero tasks created** — ensure users seeded first (`seed_users`) or run `seed_data`.
