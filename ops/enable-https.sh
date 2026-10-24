#!/usr/bin/env bash
# Run as root after both domain records point to this host.
set -Eeuo pipefail
cd /opt/kuylab/repository
getent ahostsv4 kuylab.uz | awk '{print $1}' | grep -qx '193.164.17.34'
getent ahostsv4 www.kuylab.uz | awk '{print $1}' | grep -qx '193.164.17.34'
certbot certonly --non-interactive --webroot -w /var/www/kuylab-acme -d kuylab.uz -d www.kuylab.uz
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
curl --fail --show-error https://kuylab.uz/health/ready/
