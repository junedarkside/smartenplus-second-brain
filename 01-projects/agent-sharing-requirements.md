# Agent Sharing Requirements

Requirements for a team to audit SmartEnPlus agent definitions and decide how to share them safely across the 3 repos and this vault. Read-only first, change only after the user approves a plan.

## Why

After `admin-dashboard` moved to `~/Desktop/SmartEnPlus/admin-dashboard` (see [[admin-dashboard]]), the cross-repo agents are uneven. `smartenplus-leader` lives only in the frontend repo, `smartenplus-swe` is global only, and frontend `CLAUDE.md` relies on `lookup-scout` and `opus-reviewer` that backend and admin do not have. Roster as last audited: [[claude-agent-roster-smartenplus]] (2026-10-06, now out of date). Pin rules: [[claude-agent-model-pinning-pattern]], [[claude-cost-optimization-patterns]].

## Scope

- `~/.claude/agents/` (global)
- `smartenplus-frontend/.claude/agents/`, `smartenplus-backend/.claude/agents/`, `admin-dashboard/.claude/agents/`
- This vault (no agents today) and `~/Desktop/SmartEnPlus/.claude/` (exists, no `agents/`)
- Settings and hooks that reference agents: `~/.claude/settings*.json`, `~/.claude/hooks/`, each repo's `.claude/settings.json`

## Known facts

- `smartenplus-leader`: frontend repo only. `smartenplus-swe`: global only.
- `nextjs-fullstack-architect` exists in both the frontend repo and global. Admin has `nextjs-developer`, `frontend-developer`, `debugger`. Backend has `django-backend`.
- Repo agents are tracked in git. `~/.claude` is not a git repo, so every change there needs a `.bak` copy first.
- Repo `CLAUDE.md` rule: every agent pins a model. `haiku` = lookup only, `sonnet` = default, `opus` = on request or payment/security design. Payment, auth, shared-helper work never below `sonnet`.
- Branch policy: never commit to `main` or `develop`. Feature branch off `develop` per repo. The vault commits directly.

## Sharing options considered

1. Move shared agents to `~/.claude/agents`. Every repo and the vault sees them. Not versioned, no backup across machines.
2. Use `~/Desktop/SmartEnPlus/.claude/agents` and launch Claude from the parent. UNVERIFIED that Claude Code loads agents from a parent folder. Not versioned (parent is not a git repo).
3. Keep the source in the vault (`agents/`) and symlink into `~/.claude/agents`. Versioned, one source, but symlinks work on this machine only.

Starting recommendation: option 3 for cross-repo agents (`smartenplus-leader`, `smartenplus-swe`, `lookup-scout`, `opus-reviewer`). Repo-specific agents (`react-specialist`, `django-backend`, SEO auditors) stay in their repos.

## Phase 1: audit (no edits)

1. Inventory: name, location, `model:` pin, tools, git-tracked or not, duplicates and clashes. Flag agents with no model pin.
2. Risk review per agent: model tier vs the rules above (especially payment/auth), tools broader than the job needs, rules that contradict current `CLAUDE.md` or use old paths/repo names, unguarded write access to repos, `~/.claude`, or the vault.
3. Test the unverified claim: does Claude Code load agents from a parent `.claude/agents`? Use a harmless dummy agent in a scratch location, then delete it.
4. Pick a sharing option with a reason: safety, versioning, portability, behaviour on a fresh clone.

## Phase 2: plan (no edits)

- Which agents become shared, which stay per repo.
- Step order, with a `.bak` copy of every `~/.claude` file before any change.
- Fresh clone check: if an agent leaves a tracked repo, a clone elsewhere must still work.
- Exact rollback for every step.
- List of steps that need user approval.

## Safety constraints

- Read-only until the user approves a plan.
- Back up first, change after, delete nothing until the new setup is verified.
- No pushes, no merges, no commits to `main` or `develop`.
- Add shared copies, verify, then remove repo copies in a separate approved step. Never both in one step.
- One pass per role. No spawn loops.

## Deliverable

One report in `07-logs/` with: inventory table, risk findings (high/medium/low), chosen option and why, step plan with backups and rollback, approval list, verification commands. Cite file paths and line numbers.

## Related

[[claude-agent-roster-smartenplus]] · [[claude-agent-model-pinning-pattern]] · [[claude-cost-optimization-patterns]] · [[admin-dashboard]]
