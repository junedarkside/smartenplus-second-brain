#!/bin/bash
# Diff the AGENT-GOVERNANCE block in the 3 code repos' CLAUDE.md against the vault canonical file.
# Usage: bash scripts/check-agent-governance.sh   (run from vault root). Exit 1 on drift.
VAULT="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="$(dirname "$VAULT")"
SRC="$VAULT/06-systems/agent-governance.md"
block() { sed -n '/<!-- AGENT-GOVERNANCE:BEGIN -->/,/<!-- AGENT-GOVERNANCE:END -->/p' "$1"; }
rc=0
for r in admin-dashboard smartenplus-frontend smartenplus-backend; do
  f="$ROOT/$r/CLAUDE.md"
  if [[ -z "$(block "$f")" ]]; then echo "MISSING block: $r/CLAUDE.md"; rc=1; continue; fi
  if diff <(block "$SRC") <(block "$f") >/dev/null; then echo "OK      $r"; else echo "DRIFT   $r"; diff <(block "$SRC") <(block "$f") | head -10; rc=1; fi
done
exit $rc
