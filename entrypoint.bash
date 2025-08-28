set -e

echo "Waiting for postgres to start..."
while ! nc -z db 5432; do
  echo "Retrying connection..."
  sleep 3
done
echo "Postgres started"

echo "Applying db migrations"
alembic upgrade head
echo "Migrations successfully applied"

echo "Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8001