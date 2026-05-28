#!/usr/bin/env bash
set -euo pipefail

if [ -z "${PRIVATE_KEY:-}" ]; then
  if [ -n "${FOC_STORAGE_PRIVATE_KEY:-}" ]; then
    export PRIVATE_KEY="$FOC_STORAGE_PRIVATE_KEY"
  else
    echo "FOC Storage MCP requires FOC_STORAGE_PRIVATE_KEY or PRIVATE_KEY." >&2
    exit 2
  fi
fi

export FILECOIN_NETWORK="${FILECOIN_NETWORK:-calibration}"
export TOTAL_STORAGE_NEEDED_GiB="${TOTAL_STORAGE_NEEDED_GiB:-150}"
export PERSISTENCE_PERIOD_DAYS="${PERSISTENCE_PERIOD_DAYS:-365}"
export RUNOUT_NOTIFICATION_THRESHOLD_DAYS="${RUNOUT_NOTIFICATION_THRESHOLD_DAYS:-45}"

exec npx -y @fil-b/foc-storage-mcp
