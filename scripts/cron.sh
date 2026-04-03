#!/bin/sh
set -eu

: "${POSTGRES_HOST:=db}"
: "${POSTGRES_USER:=ems_user}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
: "${POSTGRES_DB:=ems_db}"
: "${BACKUP_DEST:=/data/ems/backups/db}"
: "${CRON_SECRET:?CRON_SECRET is required}"

mkdir -p /data/ems/logs
mkdir -p "${BACKUP_DEST}"
mkdir -p /data/ems/backups/files
mkdir -p /data/ems/uploads

chmod +x /scripts/backup_db.sh

cat <<EOF | crontab -
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# DB backup every night at 02:00
0 2 * * * /scripts/backup_db.sh >> /data/ems/logs/backup.log 2>&1

# Files backup every night at 02:30
30 2 * * * rsync -av /data/ems/uploads/ /data/ems/backups/files/ >> /data/ems/logs/backup.log 2>&1

# Cleanup revoked tokens older than 13 hours
0 3 * * * psql postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}/${POSTGRES_DB} -c "DELETE FROM revoked_tokens WHERE created_at < NOW() - INTERVAL '13 hours';" >> /data/ems/logs/cleanup.log 2>&1

# Cleanup audit logs older than 3 years
0 4 1 * * psql postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}/${POSTGRES_DB} -c "DELETE FROM audit_logs WHERE timestamp < NOW() - INTERVAL '3 years';" >> /data/ems/logs/cleanup.log 2>&1

# Disk usage warning when over 80%
*/30 * * * * df /data/ems | awk 'NR==2{if(substr($5,1,length($5)-1)+0>80) print "WARNING: disk "substr($5,1,length($5)-1)"% full"}' >> /data/ems/logs/disk.log 2>&1

# EMS reminder scheduler
0 16 * * * curl -fsS -X POST "http://app:8000/api/scheduler/exam-reminder?secret=${CRON_SECRET}" >> /data/ems/logs/cron.log 2>&1
0 17 * * * curl -fsS -X POST "http://app:8000/api/scheduler/daily-digest?secret=${CRON_SECRET}" >> /data/ems/logs/cron.log 2>&1
EOF
