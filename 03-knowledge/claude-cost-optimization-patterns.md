# Claude Cost Optimization Patterns

Derived from SmartEnPlus usage report (2026-10-06). Applied fixes + patterns.

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
