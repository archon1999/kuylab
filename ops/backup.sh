#!/usr/bin/env bash
# Keep database + media together. Copy the result off-host separately.
set -Eeuo pipefail
umask 077
root=/opt/kuylab
cd "$root/repository"
exec 9>/run/lock/kuylab-deploy.lock
flock -w 600 9
export RELEASE_SHA=$(cat "$root/current-release")
destination="$root/backups/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$destination"
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$destination/database.dump"
docker compose exec -T backend tar -C /data -czf - media > "$destination/media.tar.gz"
cp "$root/current-release" "$destination/release"
sha256sum "$destination"/* > "$destination/SHA256SUMS"
python3 ops/prune_backups.py
echo "Backup saved: $destination"
