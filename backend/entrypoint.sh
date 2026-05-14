#!/bin/bash
set -e

MAX_RETRIES=30
RETRY_INTERVAL=2

echo "==> Waiting for MySQL at ${DB_HOST}:${DB_PORT}..."
for i in $(seq 1 $MAX_RETRIES); do
    if python -c "
import pymysql, sys
try:
    pymysql.connect(host='${DB_HOST}', port=${DB_PORT}, user='${DB_USER}', password='${DB_PASSWORD}')
    print('connected')
except Exception as e:
    print(f'MySQL connection failed: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1; then
        echo "==> MySQL is ready."
        break
    fi
    if [ $i -eq $MAX_RETRIES ]; then
        echo "ERROR: MySQL did not become ready after $((MAX_RETRIES * RETRY_INTERVAL))s"
        exit 1
    fi
    sleep $RETRY_INTERVAL
done

echo "==> Waiting for Redis at ${REDIS_HOST}:${REDIS_PORT}..."
for i in $(seq 1 $MAX_RETRIES); do
    if python -c "
import redis, sys
try:
    r = redis.Redis(host='${REDIS_HOST}', port=${REDIS_PORT}, decode_responses=True)
    r.ping()
    print('connected')
except Exception as e:
    print(f'Redis connection failed: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1; then
        echo "==> Redis is ready."
        break
    fi
    if [ $i -eq $MAX_RETRIES ]; then
        echo "ERROR: Redis did not become ready after $((MAX_RETRIES * RETRY_INTERVAL))s"
        exit 1
    fi
    sleep $RETRY_INTERVAL
done

echo "==> Running database initialization..."
python sql/init_db.py --execute
echo "==> Database initialized."

echo "==> Starting FastAPI server..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8567 --no-access-log
