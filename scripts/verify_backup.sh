#!/bin/bash

set -e

TEST_DB="meetshift_restore_test"

DB_USER=$(docker compose -f docker-compose.prod.yml exec -T db printenv POSTGRES_USER)

LATEST_BACKUP=$(find backups -type f -name "*.sql.gz" | sort | tail -n 1)

if [ -z "$LATEST_BACKUP" ]; then
  echo "No backup file found."
  exit 1
fi

cleanup() {
  echo "Cleaning up test database..."

  docker compose -f docker-compose.prod.yml exec -T db \
    dropdb \
    -U "$DB_USER" \
    --if-exists \
    "$TEST_DB"
}

trap cleanup EXIT

echo "Latest backup: $LATEST_BACKUP"

cleanup

echo "Creating test database..."

docker compose -f docker-compose.prod.yml exec -T db \
  createdb \
  -U "$DB_USER" \
  "$TEST_DB"

echo "Restoring backup..."

./scripts/restore_db.sh \
  "$LATEST_BACKUP" \
  "$TEST_DB"

echo "Checking Django migrations..."

MIGRATION_COUNT=$(docker compose -f docker-compose.prod.yml exec -T db \
  psql \
  -U "$DB_USER" \
  -d "$TEST_DB" \
  -tAc "SELECT COUNT(*) FROM django_migrations;")

if [ "$MIGRATION_COUNT" -le 0 ]; then
  echo "Backup verification failed: no Django migrations found."
  exit 1
fi

echo "Checking core_user table..."

docker compose -f docker-compose.prod.yml exec -T db \
  psql \
  -U "$DB_USER" \
  -d "$TEST_DB" \
  -c "SELECT COUNT(*) FROM core_user;"

echo "Backup verification successful."
