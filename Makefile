.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make lint   - Check code without making changes (ruff, isort, mypy)"
	@echo "  make format - Format code (ruff format, isort)"
	@echo "  make fix    - Auto-fix linting issues"

.PHONY: lint
lint:
	ruff check .
	isort --check .
	mypy .

.PHONY: format
format:
	ruff format --check .
	isort .

.PHONY: fix
fix:
	ruff check --fix .
	isort .
