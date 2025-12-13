.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make lint   - Check code without making changes (ruff, isort, mypy)"
	@echo "  make format - Format code (ruff format, isort)"
	@echo "  make fix    - Auto-fix linting issues"

.PHONY: lint
lint:
	uv run ruff check .
	uv run isort --check .
	uv run mypy .

.PHONY: format
format:
	uv run ruff format .
	uv run isort .

.PHONY: fix
fix:
	uv run ruff check --fix .
	uv run isort .
