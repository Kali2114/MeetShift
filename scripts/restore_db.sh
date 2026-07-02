#!/bin/bash

set -e

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: ./scripts/restore_db.sh backups/file.sql.gz"
  exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup file not found: $BACKUP_FILE"
  exit 1
fi

echo "Restoring database from: $BACKUP_FILE"

gunzip -c "$BACKUP_FILE" | docker compose -f docker-compose.prod.yml exec -T db psql \
  -U meetshift_user \
  -d meetshift

echo "Database restored successfully."
