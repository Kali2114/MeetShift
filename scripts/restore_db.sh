#!/bin/bash

set -e

BACKUP_FILE=$1
TARGET_DB=$2

if [ -z "$BACKUP_FILE" ] || [ -z "$TARGET_DB" ]; then
  echo "Usage: ./scripts/restore_db.sh backups/file.sql.gz target_database"
  exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup file not found: $BACKUP_FILE"
  exit 1
fi

DB_USER=$(docker compose -f docker-compose.prod.yml exec -T db printenv POSTGRES_USER)

echo "Restoring database '$TARGET_DB' from: $BACKUP_FILE"

gunzip -c "$BACKUP_FILE" | docker compose -f docker-compose.prod.yml exec -T db psql \
  -U "$DB_USER" \
  -d "$TARGET_DB"

echo "Database '$TARGET_DB' restored successfully."
