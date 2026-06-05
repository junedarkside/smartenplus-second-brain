# Vault Wrap-Up Optimization Report

## Date: 2026-06-05

## Problem
Vault wrap-up protocol burns ~18,500 tokens and 25 tool calls per session. 78% of master-state.md is dead weight loaded into context on every wrap-up despite never being edited.

## Current Cost

| Metric | Value |
|--------|-------|
| master-state.md | 275 lines (~3,500 tokens per read) |
| Tool calls (typical) | 25 |
| Tokens per wrap-up | ~18,500 |
| Wasteful reads | Sections 3+4 (2,500 tok), 13 old sessions (1,560 tok), 25 closed items (325 tok) |

## Recommended Approach: Hybrid A+B

Extract dead weight to separate files + bash script for git data collection.

### Projected Savings

| Metric | Current | Optimized | Savings |
|--------|---------|-----------|---------|
| master-state.md | 275 lines | ~60 lines | **78% smaller** |
| Tokens per wrap-up | ~18,500 | ~5,000 | **73% reduction** |
| Tool calls | 25 | 12 | **52% reduction** |

### Implementation Plan

**Step 1: Extract dead weight** (one-time, ~15 min)

Create these files from master-state.md content:
- `vault-protocol.md` — Section 3 (API contract), ~80 lines
- `vault-guardrails.md` — Section 4 (guardrails), ~65 lines
- `07-logs/session-history.md` — historical session blocks (#38-#49), ~130 lines
- `07-logs/closed-items.md` — struck-through items, ~25 lines

Delete from master-state.md:
- All historical session blocks (keep only latest)
- All struck-through items (keep only open)
- Active branches table (redundant with git)
- Sections 3+4 (moved to separate files)

**Step 2: Create automation script** `.claude/vault-wrapup.sh`

Script runs all git commands in one pass, outputs pre-filled templates:

```bash
# Usage: bash .claude/vault-wrapup.sh
# Output: /tmp/wrapup.md with git state + templates

REPOS=(
  "smartenplus-backend:/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-backend"
  "smartenplus-frontend:/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-frontend"
  "admin-dashboard:/Users/charuwatnaranong/Desktop/AdminDashBoard/admin-dashboard"
  "smartenplus-content:/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-content"
)

VAULT="/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus project"

# Collect git state
for repo in "${REPOS[@]}"; do
  name="${repo%%:*}"
  path="${repo#*:}"
  echo "### $name"
  echo "Branch: $(git -C "$path" branch --show-current)"
  echo "Latest: $(git -C "$path" log --oneline -1)"
  echo "Changes: $(git -C "$path" status --short)"
  echo ""
done

# Generate log entry template
echo "## Log Entry"
echo "## [$(date +%Y-%m-%d)] session-end | <summary>"
```

**Step 3: Update CLAUDE.md wrap-up protocol** (5 steps instead of 7)

```
1. Run `bash .claude/vault-wrapup.sh` → captures git state
2. Edit master-state.md Section 1 (fill achievements + resume point from script output)
3. Edit Section 2 only if open items changed
4. Append log.md entry
5. Commit+push vault + content repos
```

**Step 4: Update init protocol**

Remove git commands from init — replaced by script output in wrap-up. Init only reads:
- `master-state.md` (now ~60 lines)
- `vault-protocol.md` (only if working on API changes)
- `vault-guardrails.md` (only if working on payment/infra)

### Edge Cases

| Case | How handled |
|------|------------|
| Atom extraction | Agent extracts as normal, script unaffected |
| Session collisions | Script checks `git pull` before output |
| Mid-wrap resume | Slim file = fast read, continue from step |
| Need old session data | `grep "^## \[2026-06" 07-logs/session-history.md` |
| Need API contract | `cat vault-protocol.md` (on-demand only) |

### Optimized master-state.md Structure (~60 lines)

```markdown
# Master State — SmartEnPlus
## Section 1 — Session Handoff
**Updated:** YYYY-MM-DD (session #N)
**Achieved:** <latest session>
**Resume point:** <next steps>
## Section 2 — Loose Ends
| # | Issue | Status |
(open items only, no struck-through)
---
See also: vault-protocol.md, vault-guardrails.md, session-history.md
```

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Old sessions inaccessible | session-history.md preserves all data |
| API contract lookup harder | On-demand read, only when relevant |
| Script breaks | Fallback to manual git commands |
| Agent confused by new structure | CLAUDE.md protocol updated with explicit steps |

## Next Steps

1. Create extraction files
2. Write vault-wrapup.sh
3. Update CLAUDE.md protocol
4. Test with next session wrap-up
5. Iterate based on actual savings
