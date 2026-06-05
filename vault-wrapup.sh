#!/bin/bash
# Vault Wrap-Up Helper — collects git state for all repos
# Usage: bash vault-wrapup.sh
# Output: pre-filled template for master-state.md Section 1

REPOS=(
  "smartenplus-backend:/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-backend"
  "smartenplus-frontend:/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-frontend"
  "admin-dashboard:/Users/charuwatnaranong/Desktop/AdminDashBoard/admin-dashboard"
  "smartenplus-content:/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-content"
)

VAULT="/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus project"
DATE=$(date +%Y-%m-%d)

echo "=== Git State ($DATE) ==="
echo ""

for entry in "${REPOS[@]}"; do
  name="${entry%%:*}"
  path="${entry#*:}"

  if [ -d "$path" ]; then
    branch=$(git -C "$path" branch --show-current 2>/dev/null)
    latest=$(git -C "$path" log --oneline -1 2>/dev/null)
    changes=$(git -C "$path" status --short 2>/dev/null)

    echo "### $name"
    echo "Branch: ${branch:-unknown}"
    echo "Latest: ${latest:-none}"
    if [ -n "$changes" ]; then
      echo "Changes:"
      echo "$changes"
    else
      echo "Changes: clean"
    fi
    echo ""
  else
    echo "### $name"
    echo "NOT FOUND: $path"
    echo ""
  fi
done

echo "=== Log Entry Template ==="
echo "## [$DATE] session-end | <one-line summary>"
echo ""

echo "=== Vault Status ==="
if [ -d "$VAULT" ]; then
  vault_changes=$(git -C "$VAULT" status --short 2>/dev/null)
  echo "Vault changes:"
  echo "${vault_changes:-clean}"
fi
