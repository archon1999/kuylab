#!/usr/bin/env bash
# One-time provisioning job; no recurring timer or credentials in the repository.
set -Eeuo pipefail
umask 077
exec 8>/run/lock/kuylab-domain-activation.lock
flock -n 8 || exit 0
cd /opt/kuylab/repository
if [[ -f /etc/kuylab/build.env ]]; then
    set -a
    source /etc/kuylab/build.env
    set +a
fi

deadline=$((SECONDS + 86400))
while (( SECONDS < deadline )); do
    status=0
    bash ops/enable-https.sh || status=$?
    if (( status == 0 )); then
        echo 'Origin HTTPS is ready; waiting for both public HTTPS endpoints.'
        while (( SECONDS < deadline )); do
            if curl --fail --silent --connect-timeout 5 --max-time 12 \
                https://kuylab.uz/health/ready/ >/dev/null && \
               curl --fail --silent --connect-timeout 5 --max-time 12 \
                https://www.kuylab.uz/health/ready/ >/dev/null; then
                date -u +%FT%TZ > /opt/kuylab/domain-active
                systemctl disable kuylab-domain-activation.service
                echo 'KuyLab public HTTPS is active on both domain names.'
                exit 0
            fi
            sleep 30
        done
    elif (( status == 75 )); then
        sleep 60
    else
        # Avoid repeated ACME validation failures while DNS caches converge.
        echo "HTTPS activation failed ($status); retrying in 30 minutes."
        sleep 1800
    fi
done
echo 'Domain activation timed out after 24 hours; inspect DNS and this journal.' >&2
exit 1
