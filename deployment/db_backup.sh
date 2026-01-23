#!/bin/bash

# Database Backup Script for SynergenHR

set -e

BACKUP_DIR="/opt/synergenhr/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

echo "💾 Creating database backup..."

# Check deployment type
if docker-compose -f docker-compose.prod.yml ps | grep -q "db.*Up" 2>/dev/null; then
    echo "📦 Docker deployment detected"
    
    # Docker backup
    docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres synergenhr > $BACKUP_DIR/synergenhr_backup_$DATE.sql
    
elif systemctl is-active --quiet postgresql; then
    echo "🐘 Manual PostgreSQL installation detected"
    
    # Manual installation backup
    sudo -u postgres pg_dump synergenhr > $BACKUP_DIR/synergenhr_backup_$DATE.sql
    
else
    echo "❌ Could not detect database installation!"
    exit 1
fi

# Compress backup
gzip $BACKUP_DIR/synergenhr_backup_$DATE.sql

echo "✅ Backup created: $BACKUP_DIR/synergenhr_backup_$DATE.sql.gz"

# Clean up old backups (keep last 7 days)
find $BACKUP_DIR -name "synergenhr_backup_*.sql.gz" -mtime +7 -delete

echo "🧹 Old backups cleaned up"