#!/bin/bash
set -e

echo "Running migrations..."
cd /app
alembic upgrade head

echo "Running seed..."
python -c "
from app.core.database import SessionLocal
from app.db.seed import seed_plans_and_features
db = SessionLocal()
try:
    seed_plans_and_features(db)
finally:
    db.close()
"

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
