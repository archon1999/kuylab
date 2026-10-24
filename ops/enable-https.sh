#!/usr/bin/env bash
# Run as root after DNS reaches this host, directly or through Cloudflare.
set -Eeuo pipefail
umask 077
cd /opt/kuylab/repository
if [[ -f /etc/kuylab/build.env ]]; then
    set -a
    source /etc/kuylab/build.env
    set +a
fi

# Checking an origin IP in DNS fails once records are proxied by Cloudflare.
# Instead prove that both public hostnames can reach our exact ACME webroot.
challenge_root=/var/www/kuylab-acme/.well-known/acme-challenge
install -d -m 755 "$challenge_root"
probe="$challenge_root/kuylab-preflight"
token=$(openssl rand -hex 24)
printf '%s' "$token" > "$probe"
chmod 644 "$probe"
trap 'rm -f -- "$probe"' EXIT
for hostname in kuylab.uz www.kuylab.uz; do
    response=$(curl --fail --silent --connect-timeout 5 --max-time 12 \
        "http://$hostname/.well-known/acme-challenge/kuylab-preflight" || true)
    if [[ $response != "$token" ]]; then
        echo "Waiting for public DNS/ACME routing: $hostname"
        exit 75
    fi
done

certbot certonly --non-interactive --keep-until-expiring --webroot -w /var/www/kuylab-acme -d kuylab.uz -d www.kuylab.uz
install -d -m 755 /etc/letsencrypt/renewal-hooks/deploy
install -m 755 ops/nginx/renew-certificate.sh /etc/letsencrypt/renewal-hooks/deploy/kuylab-reload
cp /etc/nginx/conf.d/kuylab.conf /etc/nginx/conf.d/kuylab.conf.backup
install -m 644 ops/nginx/kuylab-proxy.conf /etc/nginx/snippets/kuylab-proxy.conf
install -m 644 ops/nginx/kuylab-cloudflare.conf /etc/nginx/snippets/kuylab-cloudflare.conf
install -m 644 ops/nginx/kuylab-https.conf /etc/nginx/conf.d/kuylab.conf
if nginx -t; then
    systemctl reload nginx
else
    mv /etc/nginx/conf.d/kuylab.conf.backup /etc/nginx/conf.d/kuylab.conf
    exit 1
fi
# Verify the origin independently of edge certificate issuance and DNS caches.
curl --noproxy '*' --fail --silent --show-error --max-time 15 \
    --resolve kuylab.uz:443:127.0.0.1 https://kuylab.uz/health/ready/
