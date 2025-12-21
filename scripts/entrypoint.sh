#!/bin/sh
set -e

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8080}"

echo "Starting FastAPI server on ${HOST}:${PORT}..."
exec uvicorn src.main:app \
    --host "${HOST}" \
    --port "${PORT}" \
    --timeout-keep-alive 5 \
    --timeout-graceful-shutdown 30
