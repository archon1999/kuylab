#!/usr/bin/env bash
# Run once as root on the target host. Does not replace existing secrets or data.
set -Eeuo pipefail
umask 077
for executable in docker git python3 nginx sudo; do command -v "$executable" >/dev/null; done
install -d -m 700 /etc/kuylab /opt/kuylab /opt/kuylab/backups
install -d -m 755 /var/www/kuylab-acme
python3 - <<'PY'
import os, secrets, shlex
from pathlib import Path
directory = Path('/etc/kuylab')
files = {
    'build.env': ''.join(f'{name}={shlex.quote(os.environ[name])}\n' for name in ['HTTP_PROXY','HTTPS_PROXY','NO_PROXY','http_proxy','https_proxy','no_proxy','ALL_PROXY'] if name in os.environ),
    'database.env': 'POSTGRES_DB=kuylab\nPOSTGRES_USER=postgres\nPOSTGRES_PASSWORD=' + secrets.token_urlsafe(48) + '\n',
    'production.env': 'DJANGO_SETTINGS_MODULE=config.settings.production\nDJANGO_ALLOWED_HOSTS=kuylab.uz,www.kuylab.uz\nDJANGO_SECRET_KEY=' + secrets.token_urlsafe(64) + '\nPOSTGRES_DB=kuylab\nPOSTGRES_USER=kuylab\nPOSTGRES_PASSWORD=' + secrets.token_urlsafe(48) + '\nPOSTGRES_HOST=db\nMEDIA_ROOT=/data/media\n',
}
for name, content in files.items():
    path = directory / name
    if not path.exists():
        with path.open('x') as handle:
            handle.write(content)
        path.chmod(0o600)
PY
if [[ ! -d /opt/kuylab/repository/.git ]]; then
    git clone https://github.com/archon1999/kuylab.git /opt/kuylab/repository
fi
cd /opt/kuylab/repository
install -m 755 ops/deploy.sh /usr/local/sbin/kuylab-release
install -m 755 ops/ssh-deploy-command.sh /usr/local/sbin/kuylab-ssh-command
id kuylab-deploy >/dev/null 2>&1 || useradd --create-home --shell /bin/bash kuylab-deploy
install -d -m 700 -o kuylab-deploy -g kuylab-deploy /home/kuylab-deploy/.ssh
printf '%s\n' 'kuylab-deploy ALL=(root) NOPASSWD: /usr/local/sbin/kuylab-release' > /etc/sudoers.d/kuylab
chmod 440 /etc/sudoers.d/kuylab
visudo -cf /etc/sudoers.d/kuylab
if [[ ! -f /etc/nginx/conf.d/kuylab.conf ]]; then
    install -m 644 ops/nginx/kuylab-http.conf /etc/nginx/conf.d/kuylab.conf
    nginx -t
    systemctl reload nginx
fi
docker compose up -d --wait db
# App credentials never appear in command arguments or output. The app role is
# database owner for migrations, but has no superuser, CREATEDB or CREATEROLE rights.
python3 - <<'PY'
from pathlib import Path
import subprocess
values = dict(line.split('=', 1) for line in Path('/etc/kuylab/production.env').read_text().splitlines() if '=' in line)
password = values['POSTGRES_PASSWORD'].replace("'", "''")
sql = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'kuylab') THEN CREATE ROLE kuylab LOGIN PASSWORD '" + password + "' NOSUPERUSER NOCREATEDB NOCREATEROLE; END IF; END $$; ALTER DATABASE kuylab OWNER TO kuylab;"
subprocess.run(['docker','compose','exec','-T','db','psql','-U','postgres','-d','kuylab','-v','ON_ERROR_STOP=1','-q'], input=sql, text=True, check=True)
PY
echo 'Bootstrap ready. Install the restricted deploy public key separately.'
