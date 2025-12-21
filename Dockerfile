FROM python:3.13-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir uv

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/opt/app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.13-slim AS final

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/opt/app/lib/python3.13/site-packages \
    PATH="/opt/app/bin:${PATH}"

WORKDIR /app

COPY --from=builder /opt/app /opt/app

COPY scripts/entrypoint.sh /app/entrypoint.sh
COPY src src

RUN chmod +x /app/entrypoint.sh \
    && groupadd -r appuser \
    && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080
ENTRYPOINT ["/app/entrypoint.sh"]
