#!/bin/sh
PYTHONPATH=/app poetry run python3 /app/wallet/init_db.py && gunicorn wallet:app  -k uvicorn.workers.UvicornWorker "$@"
