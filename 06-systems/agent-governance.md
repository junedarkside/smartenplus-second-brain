# Agent Governance (canonical)

## Summary
One rule set for every Claude session and agent in `admin-dashboard`, `smartenplus-frontend`, `smartenplus-backend`: branch policy and model cost rules (kept to ~20 lines on purpose: every line is loaded in every session of every repo).

## Context
The same policy was copied by hand into 3 `CLAUDE.md` files and drifted (only the frontend had branch policy and model rules). `@` imports of a file outside the repo do not load (tested 2026-11-08: in-folder import works, external relative and absolute paths do not), so each repo keeps a verbatim copy of the block below and `scripts/check-agent-governance.sh` diffs them against this file.

## How to change it
1. Edit the block between the markers below (this file is the source of truth).
2. Paste the same block between the same markers in the 3 repo `CLAUDE.md` files (one branch per repo, off `develop`).
3. Run `bash scripts/check-agent-governance.sh` from the vault root. Empty diff = in sync.

## Enforcement
- `~/.claude/hooks/branch-guard.sh` (PreToolUse on Bash, 3 code repos only). Checks every `&&`/`;`/`|` segment. Blocks: `commit` on `main`/`develop`; `merge`/`push` on `main`; any push targeting `main` (incl. `HEAD:refs/heads/main`, bare push whose upstream is `main`); `rebase/reset/cherry-pick/revert/am/pull` on `main`; destructive `branch/tag/update-ref` on `main`; `--force`; `--no-verify`. Allowed (owner decision 2026-11-08): merge and push `develop`. Vault and other repos are exempt. Rewritten 2026-11-09 (old copy `branch-guard.sh.bak-2026-11-09`).
- `~/.claude/hooks/agent-model-guard.sh` (PreToolUse on Agent, 3 code repos only): blocks `Explore`/`Plan`/`general-purpose` spawns without an explicit `model`. Custom agents rely on their frontmatter pin; forks and untyped spawns inherit the parent. Simplified 2026-11-09 (old copy `agent-model-guard.sh.bak-2026-11-09`; it also blocked forks and unpinned custom agents). Settings backups: `~/.claude/settings*.json.bak-2026-11-09`.
- `~/.claude/settings.json` `permissions.deny` blocks reading `.env*` secret files, `secrets/`, `*.key`, `*.pem` and `curl`.
- Not covered: your own terminal, CI, GitHub branch rules, `bash -c`/scripts, `gh pr merge`, sessions started outside a repo folder. See [[master-state]] for the open item.

## Canonical block

<!-- AGENT-GOVERNANCE:BEGIN -->
### Git Branch Policy — MANDATORY
- Never commit to `main` or `develop`. Branch off `develop`: `fix|feat|refactor|chore/<desc>`, commit there.
- Claude may merge feature branches into `develop` and push `develop`. Claude never touches `main` (owner deploys develop→main).
- `~/.claude/hooks/branch-guard.sh` enforces this (also blocks force push and `--no-verify`). If it blocks you, switch to a feature branch; do not work around it.

### Model Cost — MANDATORY
- Match model to risk. `haiku`: lookup, lint/build runs. `sonnet`: default for code that ships. `opus`: only when the user asks, or payment/auth/shared-API design review. Never below `sonnet` for payment, auth, shared helpers.
- Pin `model:` in every `.claude/agents/*.md`. Pass an explicit `model` when spawning Explore/Plan/general-purpose.
- Can name the file or symbol? Use `Read`/`Grep`/`Glob`, not an agent. Unknown multi-area search: one Explore call (`haiku` if pure lookup), never several.
- Mechanical work goes to `lookup-scout` / `check-runner` (haiku). Hard review goes to `opus-reviewer`. Trust the agent's report; do not redo its work.
- Tool output over ~50 KB: cite `path:line`, do not paste it back.
- "Create team": first need agent count, roles, scope, deliverable. Missing any → ask once, do not guess.
<!-- AGENT-GOVERNANCE:END -->

## Related
[[claude-agent-model-pinning-pattern]] · [[claude-cost-optimization-patterns]] · [[agent-sharing-requirements]]
