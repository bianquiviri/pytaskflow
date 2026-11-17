# Development commands

## Docker

```bash
make up            # start db + backend + frontend (builds images)
make down          # stop
make logs          # follow logs
make build         # rebuild images
```

## Backend

```bash
make migrate            # docker exec migrations
make migrations         # makemigrations inside container
make superuser          # createsuperuser inside container
make backend-test       # pytest (local venv)
make backend-lint       # ruff check
# local
cd backend && source .venv/bin/activate
python manage.py runserver
python -m pytest
python -m ruff check .
```

## Seeders (see docs/development/seeders.md)

```bash
make seed                                  # seed_data (users + tasks)
make seed-users / make seed-tasks
make clear-demo                            # seed_data --clear (confirmation required)
```

## Frontend

```bash
make frontend-install   # npm ci
make frontend-dev       # vite dev server
make frontend-test      # vitest
make frontend-lint      # eslint + vue-tsc
make frontend-build     # production build
make e2e                # playwright
```

## Everything

```bash
make test   # backend + frontend suites
make lint   # all linters
```
