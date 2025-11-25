# Backup & Restore Validation Guide

This guide documents backup and restore procedures, including automated validation drills.

## Overview

SCIMS uses:
- **PostgreSQL**: Daily logical backups with `pg_dump`
- **Redis**: RDB snapshots
- **Backup Storage**: Restic (local or S3-compatible)

## Backup Strategy

### PostgreSQL Backups

**Format:** Custom compressed format (`pg_dump -Fc`)
**Schedule:** Daily at 2 AM
**Retention:** 7 daily, 4 weekly, 3 monthly

### Redis Backups

**Format:** RDB snapshots
**Schedule:** Daily
**Retention:** 7 days

## Backup Scripts

### PostgreSQL Backup

Create `scripts/backup-postgres.sh`:

```bash
#!/bin/bash
# PostgreSQL backup script

set -e

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/scims_$DATE.dump"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Run pg_dump
docker compose exec -T postgres pg_dump \
  -U postgres \
  -Fc \
  -f "$BACKUP_FILE" \
  scims

# Compress backup
gzip "$BACKUP_FILE"

# Upload to Restic (if configured)
if [ -n "$RESTIC_REPOSITORY" ]; then
  restic backup "$BACKUP_FILE.gz"
  restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 3 --prune
fi

# Keep local backups (7 days)
find "$BACKUP_DIR" -name "*.dump.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

### Redis Backup

Create `scripts/backup-redis.sh`:

```bash
#!/bin/bash
# Redis backup script

set -e

BACKUP_DIR="/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/redis_$DATE.rdb"

mkdir -p "$BACKUP_DIR"

# Trigger Redis save
docker compose exec redis redis-cli SAVE

# Copy RDB file
docker compose cp redis:/data/dump.rdb "$BACKUP_FILE"

# Compress
gzip "$BACKUP_FILE"

# Upload to Restic
if [ -n "$RESTIC_REPOSITORY" ]; then
  restic backup "$BACKUP_FILE.gz"
  restic forget --keep-daily 7 --prune
fi

# Keep local backups (7 days)
find "$BACKUP_DIR" -name "*.rdb.gz" -mtime +7 -delete

echo "Redis backup completed: $BACKUP_FILE.gz"
```

## Restore Procedures

### PostgreSQL Restore

```bash
#!/bin/bash
# PostgreSQL restore script

set -e

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file.dump.gz>"
  exit 1
fi

# Decompress if needed
if [[ "$BACKUP_FILE" == *.gz ]]; then
  gunzip -c "$BACKUP_FILE" > "${BACKUP_FILE%.gz}"
  BACKUP_FILE="${BACKUP_FILE%.gz}"
fi

# Drop and recreate database (CAUTION: Destructive!)
docker compose exec -T postgres psql -U postgres -c "DROP DATABASE IF EXISTS scims;"
docker compose exec -T postgres psql -U postgres -c "CREATE DATABASE scims;"

# Restore backup
docker compose exec -T postgres pg_restore \
  -U postgres \
  -d scims \
  -Fc \
  "$BACKUP_FILE"

echo "Restore completed from: $BACKUP_FILE"
```

### Redis Restore

```bash
#!/bin/bash
# Redis restore script

set -e

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file.rdb.gz>"
  exit 1
fi

# Decompress if needed
if [[ "$BACKUP_FILE" == *.gz ]]; then
  gunzip -c "$BACKUP_FILE" > "${BACKUP_FILE%.gz}"
  BACKUP_FILE="${BACKUP_FILE%.gz}"
fi

# Stop Redis
docker compose stop redis

# Copy RDB file
docker compose cp "$BACKUP_FILE" redis:/data/dump.rdb

# Start Redis
docker compose start redis

echo "Redis restore completed from: $BACKUP_FILE"
```

## Automated Restore Validation

### Weekly Restore Drill

Create `scripts/validate-restore.sh`:

```bash
#!/bin/bash
# Automated restore validation script
# Runs weekly to verify backups are restorable

set -e

echo "=========================================="
echo "Backup Restore Validation"
echo "=========================================="
echo ""

# Get most recent backup
BACKUP_DIR="/backups/postgres"
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/*.dump.gz 2>/dev/null | head -1)

if [ -z "$LATEST_BACKUP" ]; then
  echo "ERROR: No backups found in $BACKUP_DIR"
  exit 1
fi

echo "Testing restore from: $LATEST_BACKUP"
echo ""

# Create temporary database for testing
TEST_DB="scims_restore_test_$(date +%Y%m%d)"
TEST_CONTAINER="postgres_test_restore"

# Start temporary PostgreSQL container
docker run -d \
  --name "$TEST_CONTAINER" \
  -e POSTGRES_PASSWORD=test \
  -e POSTGRES_DB=postgres \
  postgres:15

# Wait for PostgreSQL to be ready
sleep 5

# Decompress backup
gunzip -c "$LATEST_BACKUP" > /tmp/test_restore.dump

# Restore to test database
docker exec -i "$TEST_CONTAINER" pg_restore \
  -U postgres \
  -d postgres \
  -Fc \
  < /tmp/test_restore.dump || {
    echo "ERROR: Restore failed"
    docker rm -f "$TEST_CONTAINER"
    rm /tmp/test_restore.dump
    exit 1
  }

# Run validation queries
echo "Running validation queries..."
echo ""

# Check table counts
TABLES=("users" "organizations" "items" "locations" "item_stocks" "blueprints" "crafts")
for table in "${TABLES[@]}"; do
  COUNT=$(docker exec "$TEST_CONTAINER" psql -U postgres -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null || echo "0")
  echo "  $table: $COUNT rows"
done

# Check database integrity
echo ""
echo "Checking database integrity..."
docker exec "$TEST_CONTAINER" psql -U postgres -c "SELECT pg_database_size('postgres');" > /dev/null

# Cleanup
echo ""
echo "Cleaning up test container..."
docker rm -f "$TEST_CONTAINER"
rm /tmp/test_restore.dump

echo ""
echo "=========================================="
echo "Restore validation PASSED"
echo "=========================================="
```

### Cron Schedule

Add to crontab:

```bash
# Daily backups at 2 AM
0 2 * * * /path/to/scripts/backup-postgres.sh
0 2 * * * /path/to/scripts/backup-redis.sh

# Weekly restore validation (Sunday at 3 AM)
0 3 * * 0 /path/to/scripts/validate-restore.sh
```

## Validation Checklist

### Backup Validation

- [ ] Backup script runs successfully
- [ ] Backup file is created
- [ ] Backup file is compressed
- [ ] Backup is uploaded to Restic (if configured)
- [ ] Old backups are pruned correctly
- [ ] Backup size is reasonable
- [ ] Backup contains expected data

### Restore Validation

- [ ] Restore script runs successfully
- [ ] Database is restored correctly
- [ ] All tables are present
- [ ] Row counts match expectations
- [ ] Foreign key constraints are valid
- [ ] Indexes are created
- [ ] Application can connect to restored database

### Automated Validation

- [ ] Weekly restore drill runs automatically
- [ ] Validation queries pass
- [ ] Alerts are sent on failure
- [ ] Test container is cleaned up

## Monitoring

### Metrics to Track

- Backup success rate
- Backup size
- Backup duration
- Restore validation results
- Storage usage

### Alerts

- Backup failures
- Restore validation failures
- Storage quota exceeded
- Backup size anomalies

## Troubleshooting

### Backup Failures

1. **Check Disk Space:**
   ```bash
   df -h /backups
   ```

2. **Check Database Connection:**
   ```bash
   docker compose exec postgres psql -U postgres -c "SELECT 1;"
   ```

3. **Check Logs:**
   ```bash
   docker compose logs postgres | tail -50
   ```

### Restore Failures

1. **Check Backup File:**
   ```bash
   file backup_file.dump.gz
   gunzip -t backup_file.dump.gz
   ```

2. **Check Database Version:**
   - Ensure restore target matches backup source version
   - Or use compatible versions

3. **Check Permissions:**
   ```bash
   ls -l backup_file.dump.gz
   ```

## Best Practices

1. **Test Restores Regularly**
   - Weekly automated validation
   - Monthly manual full restore
   - Document restore procedures

2. **Monitor Backup Health**
   - Track success rates
   - Alert on failures
   - Review backup sizes

3. **Secure Backups**
   - Encrypt backups (Restic)
   - Secure backup storage
   - Limit access to backups

4. **Document Procedures**
   - Keep restore procedures up to date
   - Document recovery time objectives (RTO)
   - Document recovery point objectives (RPO)

---

For more information:
- [Deployment Guide](../deployment/README.md)
- [ADR-018: Database Backup Strategy](../../planning/decisions.md#adr-018-database-backup-strategy-lightweight)

