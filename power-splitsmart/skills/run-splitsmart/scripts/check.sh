#!/usr/bin/env bash
# Verify a local SplitSmart server is responding.
set -euo pipefail
URL="${SPLITSMART_URL:-http://127.0.0.1:8000}"
if curl -fsS "$URL/api/groups" >/dev/null; then
  echo "OK: SplitSmart is running at $URL"
else
  echo "SplitSmart is not reachable at $URL" >&2
  exit 1
fi
