# Agent Governance (canonical)

## Summary
One rule set for every Claude session and agent in `admin-dashboard`, `smartenplus-frontend`, `smartenplus-backend`: branch policy, model cost tiers, subagent routing, context discipline, team spawn discipline.

## Context
The same policy was copied by hand into 3 `CLAUDE.md` files and drifted (only the frontend had branch policy and model rules). `@` imports of a file outside the repo do not load (tested 2026-11-08: in-folder import works, external relative and absolute paths do not), so each repo keeps a verbatim copy of the block below and `scripts/check-agent-governance.sh` diffs them against this file.

## How to change it
1. Edit the block between the markers below (this file is the source of truth).
2. Paste the same block between the same markers in the 3 repo `CLAUDE.md` files (one branch per repo, off `develop`).
3. Run `bash scripts/check-agent-governance.sh` from the vault root. Empty diff = in sync.

## Enforcement
- Claude: `~/.claude/hooks/branch-guard.sh` (PreToolUse on Bash, registered in `~/.claude/settings.json`) blocks `git commit` on `main`/`develop`, `git merge/push` on `main`, pushes targeting `main`, `--force`, `--no-verify` in the 3 code repos. `main` is untouchable for Claude: also blocks `reset/rebase/cherry-pick/revert/am/pull` on `main`, and `branch/update-ref/tag` aimed at it. Since 2026-11-08 Claude is allowed to `git merge` into and `git push` `develop` (owner decision). The vault and other repos are exempt. Backup of the settings before the change: `~/.claude/settings.json.bak-2026-11-08`.
- `~/.claude/settings.json` `permissions.deny` blocks reading `.env*` secret files, `secrets/`, `*.key`, `*.pem` and `curl`.
- Not covered: your own terminal, CI, GitHub branch rules. See [[master-state]] for the open item.

## Canonical block

<!-- AGENT-GOVERNANCE:BEGIN -->
### Git Branch Policy — MANDATORY
**NEVER commit code changes directly to `main` or `develop`.** Claude may merge feature branches into `develop` and push `develop`; never `main`. Always:
1. `git checkout develop && git pull`
2. `git checkout -b <type>/<short-desc>` (types: `fix/`, `feat/`, `refactor/`, `chore/`)
3. Make changes + commit on the feature branch
4. Merge to `develop` only (never directly to `main`) — Claude may do this merge and push `develop` (owner policy 2026-11-08); `--force` and `--no-verify` stay blocked
5. `main` = production-only; only merged via develop→main deploy flow

Violation = lost history, broken prod, no rollback point. Enforced for Claude by `~/.claude/hooks/branch-guard.sh` (blocks commit on `main`/`develop`, merge/push on `main`, `--force`, `--no-verify`). If it blocks you, switch to a feature branch — do not work around it.

### Subagent Routing — Skip the Agent Tool When…

The Agent (Explore) tool costs ~739k tokens per call. **Spawn it only when the answer requires multi-area discovery you can't enumerate.** Use direct tools otherwise:

| Task pattern | Right tool | Why |
|---|---|---|
| Known file path, read context | `Read` with `offset`/`limit` | 1 call, ~2k tokens |
| Known symbol, find references | `Grep` (ripgrep) | 1 call, ~5k tokens |
| File pattern search | `Glob` | 1 call, ~1k tokens |
| Cross-area scan, unknown locations | `Agent` (Explore) | justified only here |

**Decision rule:** if you can name the file or symbol in your next sentence, you do not need Explore. If the task says "scan / audit / find all / review everything", pass the candidate file list into the Explore task prompt — don't let it rediscover the codebase.

**Model routing:** when Explore is justified and the task is pure lookup (find/read/summarize, no judgment), pass `model: "haiku"` to the Agent call. Keep default model for anything requiring judgment (review, design, payment/security-sensitive code).

### Model Cost Constraints — MANDATORY

Match model to task risk, not flat downgrade. Wrong output costs more (rework, prod bugs) than the token delta between tiers — cost never overrides correctness on payment/security/shared-API code.

- **Pin models in every `.claude/agents/*.md` frontmatter.** No agent runs on implicit default. Tiering by risk, not habit:
  - `haiku` — pure lookup/summarize, zero judgment (fact-gather, doc audits, "find X and report").
  - `sonnet` (default) — implementation, review, design, refactors, anything judgment-bearing. Floor for code that ships.
  - `opus` — only user-requested, hard architectural tradeoffs, or payment/security-critical design review. Never a standing agent default.
  - Never route payment, auth, or shared-helper-signature work below `sonnet` regardless of how "simple" the task looks — "simple" payment changes broke prod before.
- **One Explore call, not several.** Under-covered first pass → broaden its query. Don't stack a second Explore agent "just in case" (~739k tok/call).
- **No duplicate work across main thread + subagent.** Work delegated to Agent → don't re-run same Grep/Read in main thread "to confirm." Trust the report; re-open only the specific file still in question.
- **Background vs foreground agents.** Default background. Foreground/sync only when result blocks the very next step — sync spawns idle the caller and invite premature re-polling.
- **Perf/cost are joint, not traded off.** A cheaper model that needs a retry (bad diff, missed edge case, hallucinated API) costs more in wall-clock + tokens than starting at the right tier. Unsure between two tiers → pick the higher one for anything touching shipped code; reserve the lower tier for throwaway lookups whose output isn't itself the deliverable.

### Context Discipline — Avoid Paste-Echo Cycles

If a tool result or API response exceeds ~50 KB, do **not** paste it back into the next prompt. The model already has it in context. Re-pasting forces the prefix to re-send and breaks the prompt cache. For audit/debug, reference the file path + line number, not the payload.

### Team Spawn Discipline — Specify Before /clear

When the user says "create team to..." (or any variant: "spawn a team", "create an agent team", etc.), do **not** spawn until the prompt defines all 4 axes:

1. **Agent count** (e.g., "3 agents")
2. **Agent roles** (e.g., "frontend reviewer + backend reviewer + docs")
3. **Scope boundary** (files, URLs, timebox, or "everything X")
4. **Deliverable shape** (report? PR? plan? vault doc?)

If any of the 4 is missing, **ask the user to clarify in one short message**. Do not guess. Do not iteratively expand scope within a session.

Iterative chains ("create team to..." → "what else?" → "create team to..." in the same session) burn 1-1.7% of weekly tokens per shot (15-22M tokens, 100-400 API calls).
<!-- AGENT-GOVERNANCE:END -->

## Related
[[claude-agent-model-pinning-pattern]] · [[claude-cost-optimization-patterns]] · [[agent-sharing-requirements]]
