#!/bin/bash
# @AsTech — Backup all client data
BACKUP_DIR=/root/backups
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

tar czf "$BACKUP_DIR/as-tech-clients-$DATE.tar.gz" \
    -C /root/steuergpt/hermes/profiles/as-tech data/ 2>/dev/null

echo "✅ Backup: as-tech-clients-$DATE.tar.gz"
ls -lh "$BACKUP_DIR/as-tech-clients-$DATE.tar.gz"
