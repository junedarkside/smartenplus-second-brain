# Claude Cost Optimization Patterns

Derived from SmartEnPlus usage reports (2026-10-06, 2026-10-07). Applied fixes + patterns.

## Usage Report Breakdown

| Issue | % of cost | Root cause | Fix |
|-------|-----------|-----------|-----|
| Subagent-heavy sessions | 78% | Agents spawn without model pin | Pin `model:` on all agents |
| >150k context | 33% | Long orchestrator sessions no compaction | `/compact` hint at Phase 2→3 in orchestrators |
| >100k cache miss | 20% | Sessions go idle without compacting | User habit: `/compact` before stepping away |
| Explore subagent | 28% | No model constraint on Explore | Pass `model: "haiku"` on pure-lookup Explore calls |
| /wrapup skill | 13% | Skill had no model frontmatter | Added `model: haiku` to skill.md |

## Config Fixes (one-time)

1. **Pin `model:` in every agent frontmatter** — no agent runs on implicit default
2. **Skill frontmatter** — `model: haiku` for mechanical skills (wrapup), `model: sonnet` for judgment skills (herdr)
3. **Remove unavailable tools from context-manager** — `redis/elasticsearch/vector-db` not in stack → spawn failure

## Ongoing User Habits

- `/compact` before stepping away from any long session
- `/clear` between unrelated tasks (not just `/compact`)
- Explore agent: pass `model: "haiku"` for pure lookup; keep sonnet for judgment
- Never stack 2 Explore agents "just in case" (~739k tokens/call)

## /compact Placement in Orchestrators

For multi-phase orchestrator agents (seo-homepage-auditor, trip-detail-uxui-auditor), add after Phase 2 output:

```
**→ Run `/compact` now before continuing to Phase 3 to trim context and avoid cache miss cost.**
```

This targets the 33% >150k context issue for audit sessions that accumulate WebFetch + file read output across phases.

## Post-Edit Verification — Haiku for Grep Checks

Grep-only Post-Edit checks (All callers, No dead code/stubs) → spawn `haiku` Explore agent. Zero judgment needed — pure text search.

Test runner (`npm test` / `python manage.py test`) stays in main thread (sonnet) — test failure interpretation requires judgment.

Pattern:
```
Agent({
  subagent_type: "Explore",
  model: "haiku",
  prompt: "Run: grep -rn 'TODO|FIXME|console\\.log|stub' <changed files>. Report any hits."
})
```

Added to Post-Edit table footer in all 3 repo CLAUDE.md files (2026-10-06).

## Usage Review 2026-10-07 (#471) — context size, not model pinning, drove the cost

Model pinning (above) was already done and was NOT the problem: all project agents and 19/20 user agents were pinned, Haiku was only 1.5% of cost. Session: $27.80, Sonnet 98%, 92.1M cache-read tokens over 281 main requests = **~328k average context per request** (~$0.10/request), 99% cache hits, 56 min API vs 3h45m wall, weekly limit 73% used after about a day. Cost = context size x request count, not cache misses.

| Driver | Evidence | Fix |
|---|---|---|
| One session for six jobs (API, review API, AD pages, editor, UX fixes, merge/cleanup) | 39% of usage above 150k context | One task per session; `/clear` after merge/push |
| `/wrapup` at 300k+ context | skill = ~5% of usage | `/compact` or `/clear` first, then `/wrapup` (git + vault hold the state) |
| Plan-mode bounces (~8 round trips: "cannot write the demo file in plan mode") | each bounce = a full 300k-context request | Ask for visual demos before entering plan mode, or turn plan mode off before asking for files |
| Three review rounds on one feature (plan, built code, UX) | ~14 agents; each real bug found though (delete race, link loss, unsanitized English HTML) | One agent on risky logic only (security, concurrency, data loss); let lint/test/build cover the rest |
| Five visual demo pages | ~8-10k output tokens each (~12% of output); output is the priciest token type | Text diagram first; page only when the decision needs a picture |

**Panel caveat:** "95% from subagent-heavy sessions" describes sessions, not a breakdown; each agent type was ~1% (total ~6-8%), the main thread dominated.

### Routine

1. `/context` now and then; status line shows ctx % and cost (below).
2. `/compact keep: branches, decisions, open bugs` at ~100-150k, never at the limit.
3. `/clear` between unrelated tasks and after merge/push. Plan, build, merge/cleanup, wrap-up = separate sessions.
4. Keep tool output small (`tail`, `Read` with `offset/limit`), do not paste big outputs back.
5. Turn `claude-in-chrome` off when not browsing.

### Settings changed 2026-10-07 (user level, reversible)

- `~/.claude/statusline-usage.sh` (new) = caveman badge + `ctx NN%` + session cost, turns red with "~Nk compact" once the window passes ~150k tokens (or 60% when the window size is unknown). `settings.json` `statusLine.command` now points to it. Rollback: set it back to `bash "~/.claude/plugins/cache/caveman/caveman/84cc3c14fa1e/hooks/caveman-statusline.sh"` (backup: `~/.claude/settings.json.bak-before-statusline-2026-10-07`). The badge path contains a plugin-version hash; after a caveman plugin update the badge silently disappears until the hash in the script is updated.
- **`claude-switch` overwrites `settings.json`.** `~/claude-switch` (alias in `.zshrc`) copies `~/.claude/settings-{claude,glm,minimax}.json` over `~/.claude/settings.json`, so any edit made only to `settings.json` is lost on the next switch. The `statusLine` command was therefore also changed in all three switch files (backups `*.bak-before-statusline-2026-10-07`). Rule: edit the matching `settings-*.json` too. Known drift (not fixed): `settings.json` has an `autoMode` block and `permissions.allow` differing from `settings-claude.json`; a switch to Claude drops them.
- Moved unused user agents to `~/.claude/agents-disabled/`: `api-documenter`, `multi-agent-orchestrator`, `context-manager` (no recorded use; descriptions loaded into every turn). Kept `ux-research-specialist` (used June/Aug debates, listed in `smartenplus-leader`), `websocket-architect` (listed in `smartenplus-leader`), `business-analyst-expert`. Rollback = move the files back.

## Related
[[claude-agent-roster-smartenplus]]
