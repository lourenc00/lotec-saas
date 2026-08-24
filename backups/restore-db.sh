#!/bin/bash
# Restore script for Lotec SaaS
# Usage: ./restore-db.sh <backup_file>

set -euo pipefail

if [ -z "${1:-}" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 /home/luciano/lotec-saas/backups/lotec_20260819_030000.dump.gz"
    exit 1
fi

BACKUP_FILE="$1"
CONTAINER="lotec-saas-postgres-1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "WARNING: This will overwrite the current database!"
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

# Decompress if gzipped
if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | docker exec -i "$CONTAINER" pg_restore -U lotec_user -d lotec_db --clean --if-exists
else
    docker exec -i "$CONTAINER" pg_restore -U lotec_user -d lotec_db --clean --if-exists < "$BACKUP_FILE"
fi

echo "Restore completed."
