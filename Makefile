# TaskFlow developer commands (GNU Make).
# Run `make help` for the full list.

BACKEND_DIR := backend
FRONTEND_DIR := frontend

.PHONY: help up down build logs migrate migrations seed seed-users seed-tasks clear-demo \
        backend-test backend-lint backend-format frontend-install frontend-dev frontend-test \
        frontend-lint frontend-build e2e test lint superuser

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

up: ## Start all services (db, backend, frontend)
	docker compose up -d --build

down: ## Stop all services
	docker compose down

build: ## Rebuild service images
	docker compose build

logs: ## Follow logs from all services
	docker compose logs -f

migrate: ## Run database migrations
	docker compose exec backend python manage.py migrate

migrations: ## Create migrations after model changes
	docker compose exec backend python manage.py makemigrations

superuser: ## Create a Django superuser
	docker compose exec backend python manage.py createsuperuser

seed: ## Seed demo users + tasks (idempotent, dev only)
	docker compose exec backend python manage.py seed_data

seed-users: ## Seed demo users only
	docker compose exec backend python manage.py seed_users

seed-tasks: ## Seed demo tasks only
	docker compose exec backend python manage.py seed_tasks

clear-demo: ## Remove only demo records (interactive confirmation)
	docker compose exec backend python manage.py seed_data --clear

backend-test: ## Run backend test suite
	cd $(BACKEND_DIR) && python -m pytest

backend-lint: ## Run backend linter
	cd $(BACKEND_DIR) && python -m ruff check .

frontend-install: ## Install frontend dependencies
	cd $(FRONTEND_DIR) && npm ci

frontend-dev: ## Run the frontend dev server
	cd $(FRONTEND_DIR) && npm run dev

frontend-test: ## Run frontend unit tests
	cd $(FRONTEND_DIR) && npm run test

frontend-lint: ## Lint + typecheck frontend
	cd $(FRONTEND_DIR) && npm run lint && npm run typecheck

frontend-build: ## Build frontend for production
	cd $(FRONTEND_DIR) && npm run build

e2e: ## Run Playwright end-to-end tests
	cd $(FRONTEND_DIR) && npm run test:e2e

test: backend-test frontend-test ## Run backend and frontend test suites
lint: backend-lint frontend-lint ## Run all linters
