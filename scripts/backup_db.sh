#!/bin/sh
set -eu

: "${POSTGRES_HOST:=db}"
: "${POSTGRES_USER:=ems_user}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
: "${POSTGRES_DB:=ems_db}"
: "${BACKUP_DEST:=/data/ems/backups/db}"

mkdir -p "${BACKUP_DEST}"

stamp="$(date +%Y%m%d_%H%M%S)"
outfile="${BACKUP_DEST}/ems_db_${stamp}.sql.gz"

export PGPASSWORD="${POSTGRES_PASSWORD}"

pg_dump -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" | gzip > "${outfile}"

find "${BACKUP_DEST}" -type f -name 'ems_db_*.sql.gz' -mtime +14 -delete
