.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make install - Install dependencies (with dev group)"
	@echo "  make lint    - Check code without making changes (ruff, isort, mypy)"
	@echo "  make format  - Format code (ruff format, isort)"
	@echo "  make fix     - Auto-fix linting issues"
	@echo "  make test    - Run tests with coverage"
	@echo "  make clean   - Remove cache and build artifacts"

.PHONY: install
install:
	uv sync --group dev

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
