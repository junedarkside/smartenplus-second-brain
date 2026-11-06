# Admin-dashboard move audit (2026-11-06)

OLD = `/Users/charuwatnaranong/Desktop/AdminDashBoard/admin-dashboard`
NEW = `/Users/charuwatnaranong/Desktop/SmartEnPlus/admin-dashboard`

Sources: path-scout sweep, move-devops impact analysis, plus direct confirmation reads (frontend CLAUDE.md, hook lines, git config). Filename carries a date at the user's request, which deviates from the vault no-dates naming rule.

## 1. Verdict

The move is safe for the code: git is intact, no application code, Dockerfile, next.config.js or CI references the folder path, and cross-repo coupling is by API URL only. What is degraded is tooling: the SessionStart hooks (4 settings files plus `vault-brief.sh`) do not fire for sessions started in the NEW admin path and show a blank Admin slot elsewhere, `vault-wrapup.sh` reports admin as NOT FOUND (so `master-state.md` wrap-ups lose admin state), two agent prompts point at a nonexistent path, and Claude Code project memory/history for admin is keyed to OLD. All of it is silent or non-fatal, and all of it is fixable by one path substitution. Live docs hold 6 more stale references.

## 2. Fix list

Substitution used throughout: `Desktop/AdminDashBoard/admin-dashboard` -> `Desktop/SmartEnPlus/admin-dashboard`. SYNC.md and ENV.md use relative or CLAUDE.md-suffixed forms, noted per row.

| Pri | file:line | What breaks today | Exact change | Repo/branch handling | Approval |
|---|---|---|---|---|---|
| P0 | `~/.claude/settings.json:18` | Hook PROJECTS has OLD: session in NEW admin matches nothing, no SessionStart context. ADMIN_BRANCH/COMMIT `cd` fails, Admin slot blank | OLD -> NEW (all occurrences on line: PROJECTS, ADMIN_BRANCH, ADMIN_COMMIT) | Not a git repo; edit in place, keep a `.bak-before-admin-move-2026-11-06` copy like the existing backups | Y (~/.claude) |
| P0 | `~/.claude/settings-claude.json:31,33` | Same as above | OLD -> NEW | Same | Y |
| P0 | `~/.claude/settings-glm.json:35` | Same | OLD -> NEW | Same | Y |
| P0 | `~/.claude/settings-minimax.json:36` | Same | OLD -> NEW | Same | Y |
| P0 | `~/.claude/hooks/vault-brief.sh:7,33,34` | PROJECTS guard and ADMIN_BRANCH/ADMIN_COMMIT use OLD; admin falls back to `N/A` | OLD -> NEW | Same | Y |
| P0 | `smartenplus project/vault-wrapup.sh:9` | `admin-dashboard:OLD` -> prints `NOT FOUND`; /wrapup lacks admin branch/commit/dirty state | `admin-dashboard:OLD` -> `admin-dashboard:NEW` | Vault repo, not a feature-branch repo: commit directly with the vault's `ingest:`/`session-end:` style message and push per vault CLAUDE.md | N (vault, user-owned workflow); confirm with user before commit |
| P1 | `smartenplus-frontend/.claude/agents/smartenplus-leader.md:23,24,211` | `git -C OLD` fatal at leader startup (admin state missing); table at :211 misleads | OLD -> NEW | Frontend repo: branch `chore/admin-dashboard-path-update` off `develop`, merge to `develop` only | N (project file) but needs a commit decision (see section 4) |
| P1 | `~/.claude/agents/smartenplus-swe.md:15` | Agent told the wrong admin location; Read/Edit of admin files errors | OLD -> NEW | Not a git repo; backup then edit | Y (~/.claude) |
| P1 | `~/.claude/projects/-Users-charuwatnaranong-Desktop-AdminDashBoard-admin-dashboard` | Sessions in NEW start a fresh project dir: no resume, no auto-memory (see section 4) | Decision pending | n/a | Y |
| P2 | `smartenplus project/01-projects/admin-dashboard.md:17` | Repo table shows OLD (live doc) | OLD -> NEW | Vault, same as above | N |
| P2 | `smartenplus-frontend/docs/operations/ENV.md:12` | Dead relative link `../../AdminDashBoard/admin-dashboard/docs/operations/ENV.md` | -> `../../../admin-dashboard/docs/operations/ENV.md` (frontend `docs/operations` to repo parent is three levels up; verify link resolves) | Frontend repo, bundle with the P1 branch | N |
| P2 | `smartenplus-frontend/docs/agent-policy/SYNC.md:5` | Lists OLD `CLAUDE.md` path | OLD -> NEW | Same branch | N |
| P2 | `smartenplus-backend/docs/operations/ENV.md:30` | Dead relative link, same pattern | -> `../../../admin-dashboard/docs/operations/ENV.md` (verify) | Backend repo: `chore/admin-dashboard-path-update` off `develop` | N |
| P2 | `smartenplus-backend/docs/agent-policy/SYNC.md:5` | OLD CLAUDE.md path | OLD -> NEW | Same backend branch | N |
| P2 | `admin-dashboard/docs/agent-policy/SYNC.md:5` | OLD CLAUDE.md path | OLD -> NEW | Admin repo is currently on `main`: branch off `develop` first (`git checkout develop && git pull && git checkout -b chore/admin-dashboard-path-update`). Untracked `.scratch/` exists there, do not `git add -A` | N |
| P2 | `settings-claude.json.bak-before-*-2026-10-07:23` (2 files) | Harmless, only inside backups | Leave | n/a | n/a |

Already fixed by main thread (uncommitted): `smartenplus-frontend/CLAUDE.md` CROSS-REPO row, `smartenplus-backend/CLAUDE.md:188`, `smartenplus project/CLAUDE.md:123,124`.

Resolved conflict: move-devops said frontend CLAUDE.md still showed OLD. Confirmed false. Lines 198-203 now read `| admin-dashboard | ../admin-dashboard/ | Internal admin |`. That change is uncommitted and sits on branch `main` in the frontend repo (git status showed ` M CLAUDE.md`), so it must be moved to a feature branch before committing, never committed on `main`.

## 3. Leave-alone list

- All HISTORY: `smartenplus-frontend/CLAUDE.original.md:123`, `smartenplus-backend/CLAUDE.md.original.md` and `CLAUDE.md.backup-2026-02-10`, other `*.original.md` backups.
- Vault logs and records: `07-logs/vault-wrapup-optimization-report.md:56`, `01-projects/command-centre-pending-badge-implementation.md:6`, `01-projects/chat-review-e2e-manual-test-2026-07-07.md:265`, `08-archive/**`.
- `admin-dashboard/docs/archive/**` (6 files).
- The two `settings-claude.json.bak-*` files.
- Frontend/backend `admin-dashboard-operators` and `admin-dashboard-charge` strings: backend API endpoint names, not folder paths.
- Admin `.next` and `node_modules`: rebuild on demand (`rm -rf .next` only if odd build errors appear).

## 4. Pending decisions for the user

1. **Remote `main`.** Confirmed: `origin` and `main` both point to `git@github.com:junedarkside/smartenplus-dashboard.git`. `git config --get-regexp '^branch\..*\.remote$'` returned `origin` for every branch (develop, main, chore/claude-agents-cleanup, fix/sidebar-badge-no-poll, perf/api-trailing-slash, feat/payment-issues-page); no branch tracks remote `main`. Removing it is safe: `git -C NEW remote remove main`. It does not touch GitHub. It is pre-existing and unrelated to the move, so this is cleanup, not a requirement. A remote named the same as a branch makes `git push main` and `main/...` refs ambiguous, which is the reason to remove it.
2. **Memory dir.** The OLD-keyed dir contains `memory/` and `sessions-index.json`. Recommendation: migrate with `mv` to `-Users-charuwatnaranong-Desktop-SmartEnPlus-admin-dashboard`, but only after confirming the new-key dir does not exist (`ls ~/.claude/projects | grep SmartEnPlus-admin` returned nothing, so it does not yet exist) and with no Claude session open in either path. Reason: it preserves auto-memory and resume for admin work at the cost of one rename; the alternative (ignore) loses it silently. Also check the `~/.claude.json` `projects` key for trust/allowed-tools entries keyed to OLD (not inspected). Needs approval (~/.claude).
3. **Branch-slot bug (unrelated, pre-existing).** Confirmed: `~/.claude/settings.json:18` and `settings-claude.json:31` pass `"$FRONTEND_BRANCH"` as the 5th printf argument, so the "Admin:" line shows the frontend branch. Fix: that argument -> `"$ADMIN_BRANCH"` (the trailing `"$FRONTEND_BRANCH" "$ADMIN_COMMIT"` pair becomes `"$ADMIN_BRANCH" "$ADMIN_COMMIT"`). glm and minimax already use `$ADMIN_BRANCH`. Recommend fixing in the same edit since the lines are being touched anyway. I did not open `vault-brief.sh` lines 30-36 beyond the scout's report (line 33/34 OLD usage, `|| echo N/A` fallback) because the file read returned nothing at the sed range; re-check at implementation time. Needs approval.
4. **Commit the path fixes?** Recommended: yes, one small `chore/admin-dashboard-path-update` branch per repo (frontend, backend, admin), each off `develop`, merged to `develop` only. Frontend also carries the uncommitted CLAUDE.md change; start that branch from `develop` and carry the CLAUDE.md edit over. Vault changes commit straight to the vault repo. Nothing is committed until the user says so.
5. **Admin repo is on `main`.** Confirm intent; any admin edit needs a branch off `develop` first.

## 5. Verification steps after fixes

```bash
# No stale references left in live files (history/archive hits expected)
grep -rn "AdminDashBoard" ~/.claude/settings*.json ~/.claude/hooks ~/.claude/agents \
  "/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus project/vault-wrapup.sh" \
  /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-frontend/.claude \
  /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-frontend/docs \
  /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-backend/docs \
  /Users/charuwatnaranong/Desktop/SmartEnPlus/admin-dashboard/docs/agent-policy \
  | grep -v "\.bak-"

# JSON still valid
for f in ~/.claude/settings.json ~/.claude/settings-claude.json ~/.claude/settings-glm.json ~/.claude/settings-minimax.json; do python3 -m json.tool "$f" >/dev/null && echo "ok $f"; done

# vault-wrapup finds admin
bash "/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus project/vault-wrapup.sh" | grep -A3 "admin-dashboard"

# Hook fires from NEW path and shows the admin branch
cd /Users/charuwatnaranong/Desktop/SmartEnPlus/admin-dashboard && bash ~/.claude/hooks/vault-brief.sh | grep -i admin

# Doc links resolve (run from each file's directory)
test -f /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-frontend/docs/operations/../../../admin-dashboard/docs/operations/ENV.md && echo ok-fe
test -f /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-backend/docs/operations/../../../admin-dashboard/docs/operations/ENV.md && echo ok-be

# Remote and branch tracking
git -C /Users/charuwatnaranong/Desktop/SmartEnPlus/admin-dashboard remote -v
git -C /Users/charuwatnaranong/Desktop/SmartEnPlus/admin-dashboard fetch origin

# Admin app still builds from the new location
cd /Users/charuwatnaranong/Desktop/SmartEnPlus/admin-dashboard && npm run build
```

Also start a fresh Claude session inside NEW and confirm the SessionStart context appears and memory loads (after the memory-dir decision).

## 6. Residual risks

- `~/.claude.json` project-key trust/allowed-tools entries for OLD were not inspected; a session in NEW may re-prompt for trust and tool permissions.
- `smartenplus-content` path on `vault-wrapup.sh:11` was not verified by either agent.
- `ENV.md` relative-link depth is derived by reasoning, not tested; run the `test -f` checks above.
- Admin `.next` and `node_modules` caches may embed absolute OLD paths; stale-cache build errors resolve with `rm -rf .next`.
- Local editor/IDE workspace files, shell aliases, launchd/cron entries, and any other tool outside the three repos were not in the sweep scope.
- The `smartenplus-leader.md` and frontend CLAUDE.md edits are uncommitted on `main` in the frontend repo; risk of an accidental commit to `main` until they are moved to a feature branch.
