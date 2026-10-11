#!/usr/bin/env bash
# Forced SSH command. No interactive shell, forwarding, or arbitrary command.
set -euo pipefail
if [[ ${SSH_ORIGINAL_COMMAND:-} =~ ^deploy\ ([a-f0-9]{40})$ ]]; then
    exec sudo -n /usr/local/sbin/kuylab-release "${BASH_REMATCH[1]}"
fi
echo 'Only deploy <commit-sha> is allowed' >&2
exit 2
