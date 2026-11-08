#!/bin/sh
# Run INSIDE a PostgreSQL 16 container. Supply a NEW restore database name.
# Example: sh backup-and-restore.sh Hospiatl_Lab_db stage_a_restore_new /tmp/backup_2026-11-08.dump
set -eu
source_db=${1:?Source database required}
restore_db=${2:?New restore database required}
backup_file=${3:?Backup path required}
: "${POSTGRES_USER:?POSTGRES_USER must be set}"
if [ "$source_db" = "$restore_db" ]; then
  echo 'Refusing to restore over source database' >&2
  exit 1
fi
if [ -e "$backup_file" ]; then
  echo 'Backup file already exists; choose a new path' >&2
  exit 1
fi
pg_dump -U "$POSTGRES_USER" -d "$source_db" -Fc --no-owner --no-privileges -f "$backup_file"
createdb -U "$POSTGRES_USER" "$restore_db"
pg_restore -U "$POSTGRES_USER" -d "$restore_db" --no-owner --no-privileges --exit-on-error "$backup_file"
echo "Backup created and restored into new database: $restore_db"
