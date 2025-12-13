FROM python:3.13-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY src src

FROM python:3.13-slim AS final

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY scripts/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh \
    && groupadd -r appuser \
    && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080
ENTRYPOINT ["/app/entrypoint.sh"]
