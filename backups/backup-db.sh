#!/bin/bash
# Database backup script for Lotec SaaS
# Run daily via cron: 0 3 * * * /home/luciano/lotec-saas/backups/backup-db.sh

set -euo pipefail

BACKUP_DIR="/home/luciano/lotec-saas/backups"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER="lotec-saas-postgres-1"

# Run backup
docker exec "$CONTAINER" pg_dump -U lotec_user -d lotec_db --format=custom > "$BACKUP_DIR/lotec_${DATE}.dump"

# Compress
gzip "$BACKUP_DIR/lotec_${DATE}.dump"

# Remove old backups
find "$BACKUP_DIR" -name "lotec_*.dump.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: lotec_${DATE}.dump.gz"
