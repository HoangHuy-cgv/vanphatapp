#!/usr/bin/env bash
# Nightly offsite backup: compose backup profile -> local ./backups -> R2.
# Cron on VPS (daily 02:00): 0 2 * * * /opt/vanphat/infra/backup-r2.sh
# Requires: rclone with an `r2` remote (access key in rclone.conf, never in repo).
set -euo pipefail
cd /opt/vanphat

# 1. Bench backup (DB + files) into the `backups` volume, exposed at ./backups.
docker compose --profile backup run --rm backup

# 2. Sync to R2 (30-day retention handled by bucket lifecycle rule).
rclone sync ./backups r2:vanphat-erp-backups --min-age 1d --log-file ./backups/rclone.log

# 3. Keep 7 local days only; R2 is the archive.
find ./backups -maxdepth 1 -mtime +7 -delete
