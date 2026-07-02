#!/bin/bash

set -e

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/meetshift_$TIMESTAMP.sql.gz"

mkdir -p "$BACKUP_DIR"

docker compose -f docker-compose.prod.yml exec -T db pg_dump \
  -U meetshift_user \
  -d meetshift \
  | gzip > "$BACKUP_FILE"

echo "Backup created: $BACKUP_FILE"

find "$BACKUP_DIR" -type f -name "*.sql.gz" -mtime +14 -delete

echo "Old backups (>14 days) removed."
