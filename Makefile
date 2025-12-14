.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make install - Install dependencies (with dev group)"
	@echo "  make lint    - Check code without making changes (ruff, mypy)"
	@echo "  make format  - Format code (ruff format and fix)"
	@echo "  make fix     - Auto-fix linting issues"
	@echo "  make test    - Run tests with coverage"
	@echo "  make clean   - Remove cache and build artifacts"
	@echo "  make start   - Build and start Docker containers"
	@echo "  make build   - Build Docker images"
	@echo "  make up      - Start Docker containers"
	@echo "  make down    - Stop Docker containers"

.PHONY: install
install:
	uv sync --group dev

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

.PHONY: test
test:
	uv run pytest

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
