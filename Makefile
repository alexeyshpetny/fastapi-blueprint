SERVICE_NAME = shpetny-fastapi-blueprint-api
ALEMBIC_CONFIG = src/alembic.ini

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make install - Install dependencies (with dev group)"
	@echo "  make ci      - Run all CI checks (lint, type-check, security, tests)"
	@echo "  make lint    - Check code without making changes (ruff, mypy)"
	@echo "  make format  - Format code (ruff format and fix)"
	@echo "  make fix     - Auto-fix linting issues"
	@echo "  make security - Run security checks (bandit)"
	@echo "  make test    - Run all tests with coverage"
	@echo "  make test-unit - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-fast - Run tests without coverage (faster)"
	@echo "  make clean   - Remove cache and build artifacts"
	@echo "  make start   - Build and start Docker containers"
	@echo "  make build   - Build Docker images"
	@echo "  make up      - Start Docker containers"
	@echo "  make down    - Stop Docker containers"
	@echo "  make migrate - Run database migrations"
	@echo "  make create-migrations - Create new migration files"

.PHONY: install
install:
	uv sync --group dev

.PHONY: ci
ci: lint security test

.PHONY: lint
lint:
	uv run ruff check .
	uv run mypy .

.PHONY: format
format:
	uv run ruff format .
	uv run ruff check --fix .

.PHONY: fix
fix:
	uv run ruff check --fix .

.PHONY: security
security:
	uv run bandit -c pyproject.toml -r src/ -ll

.PHONY: test
test:
	uv run pytest

.PHONY: test-unit
test-unit:
	uv run pytest -m unit

.PHONY: test-integration
test-integration:
	uv run pytest -m integration

.PHONY: test-fast
test-fast:
	uv run pytest -x --ff

.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml dist/ build/ 2>/dev/null || true

.PHONY: start
start: build up

.PHONY: build
build:
	docker compose build

.PHONY: up
up:
	docker compose up -d
	docker compose ps

.PHONY: down
down:
	docker compose down

.PHONY: connect
connect:
	docker exec -it $(SERVICE_NAME) /bin/bash

.PHONY: logs
logs:
	docker logs -f $(SERVICE_NAME)

.PHONY: migrate
migrate:
	docker exec $(SERVICE_NAME) bash -c 'cd src && alembic upgrade head'

.PHONY: create-migrations
create-migrations:
	docker exec --user root $(SERVICE_NAME) alembic --config $(ALEMBIC_CONFIG) revision --autogenerate --message auto
	@docker exec --user root $(SERVICE_NAME) chown -R $$(id -u):$$(id -g) /app/src/migrations/versions/
