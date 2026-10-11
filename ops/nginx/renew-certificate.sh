#!/usr/bin/env bash
set -euo pipefail
if [[ ${RENEWED_LINEAGE:-} == /etc/letsencrypt/live/kuylab.uz ]]; then
    nginx -t
    systemctl reload nginx
fi
