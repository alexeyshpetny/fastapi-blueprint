#!/bin/sh
set -e

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8080}"
ENVIRONMENT="${APP_ENVIRONMENT:-development}"
WORKERS="${WORKERS:-4}"
RUN_MIGRATIONS="${RUN_MIGRATIONS:-true}"

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    bash -c 'cd src && alembic upgrade head'
else
    echo "Skipping database migrations (RUN_MIGRATIONS=false)"
fi

if [ "$ENVIRONMENT" = "production" ]; then
    echo "Starting FastAPI server with Gunicorn on ${HOST}:${PORT}..."
    echo "Workers: ${WORKERS}"
    exec gunicorn src.main:application \
        --workers "${WORKERS}" \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind "${HOST}:${PORT}" \
        --timeout 120 \
        --keep-alive 5 \
        --graceful-timeout 30 \
        --access-logfile - \
        --error-logfile - \
        --log-level info
else
    echo "Starting FastAPI server with Uvicorn (development/Docker Compose) on ${HOST}:${PORT}..."
    exec uvicorn src.main:application \
        --host "${HOST}" \
        --port "${PORT}" \
        --reload \
        --timeout-keep-alive 5 \
        --timeout-graceful-shutdown 30
fi
