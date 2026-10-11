#!/usr/bin/env bash
# Installed root-owned as /usr/local/sbin/kuylab-release during provisioning.
set -Eeuo pipefail
umask 077
[[ $# == 1 && $1 =~ ^[a-f0-9]{40}$ ]] || { echo 'Expected a commit SHA'; exit 2; }
sha=$1
root=/opt/kuylab
exec 9>/run/lock/kuylab-deploy.lock
flock -w 600 9
cd "$root/repository"
git fetch --quiet origin main
[[ $(git rev-parse origin/main) == "$sha" ]] || { echo 'Deploy only current main'; exit 2; }
available=$(df --output=avail -k "$root" | tail -1)
(( available > 1572864 )) || { echo 'Less than 1.5 GiB free; deployment stopped'; exit 1; }
git checkout --detach --force "$sha"
export RELEASE_SHA=$sha
docker compose build
docker compose up -d --wait db
mkdir -p "$root/backups"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$root/backups/$stamp.dump"
docker compose run --rm --no-deps backend python manage.py check --deploy --fail-level WARNING
docker compose run --rm --no-deps backend python manage.py migrate --noinput
docker compose run --rm --no-deps backend python manage.py createcachetable
docker compose run --rm --no-deps backend python manage.py seed_studio
previous=$(cat "$root/current-release" 2>/dev/null || true)
if ! docker compose up -d --wait --wait-timeout 120; then
    if [[ $previous =~ ^[a-f0-9]{40}$ ]]; then
        echo 'Application health failed; restoring previous images. Database is not automatically downgraded.'
        RELEASE_SHA=$previous docker compose up -d --no-build --wait --wait-timeout 120
    fi
    exit 1
fi
curl --fail --silent --show-error -H 'Host: kuylab.uz' -H 'X-Forwarded-Proto: https' http://127.0.0.1:18280/health/ready/
printf '%s\n' "$sha" > "$root/current-release"
[[ -z $previous ]] || printf '%s\n' "$previous" > "$root/previous-release"
echo "Deployed $sha"
