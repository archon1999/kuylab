# Production operations

## Environments

Local development uses `config.settings.local` and SQLite, with no Docker required.
Production uses `config.settings.production`, PostgreSQL 16, Gunicorn, WhiteNoise
and a static Nginx frontend. The host Nginx terminates TLS. PostgreSQL has no host
port; the frontend binds only `127.0.0.1:18280`. Media is served through authenticated
API endpoints, never directly by Nginx. Containers have memory limits, rotating
logs, health checks and persistent database/media volumes.

Paths on the host:

- `/opt/kuylab/repository`: checkout (deployment pins a main commit).
- `/etc/kuylab/production.env`: root-owned secrets, mode 600; see the example.
- `/etc/kuylab/database.env`: separate PostgreSQL administrator secret, mode 600.
- `/opt/kuylab/backups`: private database and media backups.
- `/opt/kuylab/current-release`, `previous-release`: image tags for recovery.
- `/etc/nginx/conf.d/kuylab.conf`: only KuyLab's virtual host.

Never run `docker compose down -v` on production. Never prune another project's
containers or volumes. The server hosts other applications.

## CI/CD

GitHub Actions checks the frontend, all backend tests on **both SQLite and
PostgreSQL**, Django migration drift, production security settings and Docker
builds. CodeQL analyzes Python and TypeScript separately. Dependabot opens update
PRs; updates are not automatically merged.

The `CI passed` status is required on `main`. Only a successful main workflow may
use the `production` environment. Configure:

- repository variable `DEPLOY_ENABLED=true` after initial provisioning;
- environment variable `DEPLOY_HOST`;
- environment secrets `DEPLOY_SSH_KEY`, `DEPLOY_KNOWN_HOSTS`.

The SSH key is dedicated to `kuylab-deploy`, with a forced command and no shell,
agent, X11, or TCP forwarding. It can only ask a root-owned wrapper to deploy the
current remote main SHA. The account is not in the Docker group. Use SSH host
keys verified during provisioning, not unchecked `ssh-keyscan` during deployment.

Base images are pinned by digest and application dependencies are locked. The
deploy script takes a lock, builds release-tagged images,
runs migrations and the idempotent curated seed, and waits for container health.
It restores the previous application images if startup fails. **Schema rollback is
not automatic**: migrations must remain compatible with the previous release.
There can be a short interruption while the single backend container is replaced.
This is not a highly available/zero-downtime deployment.

Privileged deployment wrappers are installed explicitly during provisioning.
Changes to those wrappers require an administrator to review and reinstall them.

## DNS and HTTPS

Create A records for `kuylab.uz` and `www.kuylab.uz` pointing at the server. Do not
leave AAAA records pointing at a different machine. Until DNS is connected, the
HTTP virtual host returns a maintenance response and the application remains
reachable only through the server's loopback port.

After both names resolve, run as root:

```sh
bash /opt/kuylab/repository/ops/enable-https.sh
certbot renew --dry-run
```

The script obtains a real certificate, validates Nginx and reloads it. Certbot's
existing renewal service must stay enabled. Public login requires HTTPS; secure
cookies and HTTPS redirects must not be disabled for a temporary public preview.
Web Audio worklets and service workers also require a secure browser context.

Cloudflare manages the `kuylab.uz` DNS zone on its Free plan. The registrar's
nameservers are `alina.ns.cloudflare.com` and `boyd.ns.cloudflare.com`. The apex
A record points to `193.164.17.34`; `www` is a CNAME to `kuylab.uz`. Keep these
records DNS-only until the origin certificate is issued, then proxy the two web
records and use **Full (strict)** encryption with TLS 1.2 or newer. Do not enable
Flexible encryption or proxy mail/FTP records.

After certificate activation, enable Cloudflare's Always Use HTTPS. Both origin
listeners serve the ACME webroot, so certificate validation continues to work
when the edge redirects HTTP challenges to HTTPS. Verify with
`certbot renew --cert-name kuylab.uz --dry-run` after enabling the proxy.

KuyLab's HTTPS virtual host trusts `CF-Connecting-IP` only when the connection
comes from Cloudflare's published IPv4/IPv6 proxy networks. This keeps per-client
login limits and access logs correct without trusting spoofed headers from direct
connections. Review `ops/nginx/kuylab-cloudflare.conf` when Cloudflare updates its
published ranges; the snippet is scoped to KuyLab and does not affect other sites.

## Backup and recovery

```sh
bash /opt/kuylab/repository/ops/backup.sh
```

This saves a custom-format `pg_dump`, a media archive, release SHA and checksums.
Automatic host-local backups are disabled on this deployment at the owner's
request to conserve disk space. The supplied systemd timer is disabled; the
command above remains available for an explicit manual backup. Retention keeps
seven successful full backups and ten pre-deployment dumps, confined to KuyLab's
backup directory. Database and media belong together.

Pre-migration dumps are also disabled by default. To opt in, an administrator
must create `/etc/kuylab/enable-local-backups`. To separately enable daily full
backups, install the supplied units and enable `kuylab-backup.timer`. Neither
is re-enabled by a deployment. Without backups, deleted data cannot be restored
from this host.
Host-local backups do not protect against loss of the host; arrange encrypted
off-host storage and a retention policy before relying on this for public users.
No external storage credentials are assumed or embedded in the repository.

Restore first to an isolated PostgreSQL database, verify with `pg_restore --list`,
then `pg_restore --exit-on-error --no-owner --no-acl` into the empty database.
Use the matching media archive and release. To restore the live database, stop
backend writes, take a fresh safety backup, restore into a new database and point
the environment at it. Do not drop an active database or automatically downgrade
schema migrations. Preserve the old database until verification is complete.

For an application-only rollback, verify schema compatibility and run from the
checkout with the recorded previous SHA:

```sh
export RELEASE_SHA=$(cat /opt/kuylab/previous-release)
docker compose up -d --no-build --wait
```

Keep at least the current and previous image tags. Review `docker system df` and
remove only explicitly identified obsolete **KuyLab** images when space is low.

## Local data migration

Copy a consistent SQLite backup first, then export Django fixtures with natural
foreign keys, excluding contenttypes, auth.permission, sessions and admin.logentry.
Transfer that private fixture and media over SSH, run migrations against empty
PostgreSQL, load the fixture, and run `seed_studio`. `loaddata` resets PostgreSQL
sequences. Verify model counts, account separation and the source MIDI hash.
Never put the fixture or any password hashes in GitHub or CI artifacts.

## Verification

```sh
docker compose ps
docker compose exec backend python manage.py check --deploy --fail-level WARNING
curl -f -H 'Host: kuylab.uz' -H 'X-Forwarded-Proto: https' \
  http://127.0.0.1:18280/health/ready/
```

The two health endpoints return only availability, not credentials or exception
details. Authentication, CSRF and account isolation tests run in CI. User state is
never included in public cache responses. Do not expose `/media/`, production
environment files or backup directories through Nginx.
