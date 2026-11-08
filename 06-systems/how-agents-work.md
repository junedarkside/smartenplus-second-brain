# How Claude agents work in the 3 repos

## Summary
One-page plain version of [[agent-governance]]. Three ideas, two habits. Read this first; read the canonical note only when changing the rules.

## The three ideas
1. **Cheapest worker that does the job.**
   - `haiku`: searching and running lint/build (`lookup-scout`, `check-runner`).
   - `sonnet`: writing and reviewing code (the default).
   - `opus`: only when you ask, or payment/auth/shared-API design review (`opus-reviewer`).
2. **Rules written once.** The master copy lives in [[agent-governance]]. Each repo `CLAUDE.md` holds a verbatim copy; `bash scripts/check-agent-governance.sh` (vault root) says if they drifted.
3. **Hooks block the dangerous things.** Rules in `CLAUDE.md` are advice; hooks are walls.
   - `branch-guard.sh`: Claude cannot commit to `main`/`develop`, cannot touch `main` at all, no force push, no `--no-verify`. Claude may merge and push `develop`.
   - `agent-model-guard.sh`: Explore/Plan/general-purpose spawns must name a model.
   - Deny rules: no reading `.env*`, keys, `secrets/`; no `curl`.

## The two habits
- Let Claude use the helper agents for searching and checks. Do not ask it to "scan everything" in the main thread.
- Say "use opus" only when you really want it.

## If a hook blocks you
Switch to a feature branch off `develop` (`git checkout develop && git checkout -b feat/<desc>`). Do not work around the hook.

## What the walls do NOT cover
Your own terminal, CI, GitHub rules, `bash -c` and scripts, `gh pr merge`, and sessions started outside a repo folder (e.g. the parent `SmartEnPlus/`). Open item: GitHub branch protection on `main` ([[master-state]]).

## Where things live
- Hooks and deny rules: `~/.claude/hooks/`, `~/.claude/settings.json` (mirrored in `settings-{claude,glm,minimax}.json` for claude-switch).
- Agents: `<repo>/.claude/agents/` (each pins its model).
- Rules: `<repo>/CLAUDE.md` (block between the AGENT-GOVERNANCE markers).

## Related
[[agent-governance]] · [[claude-agent-model-pinning-pattern]] · [[claude-cost-optimization-patterns]] · [[agent-sharing-requirements]]
