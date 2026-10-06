# Claude Agent Model Pinning Pattern

**Context:** SmartEnPlus 3-repo system (FE + BE + Admin). Claude Code agent cost control.

## Rule

Every `.claude/agents/*.md` file MUST have `model:` in frontmatter. No pin = session default = unpredictable cost.

```yaml
---
name: my-agent
description: ...
model: sonnet   # ← required
tools: Read, Write, Edit, Bash, Glob, Grep
---
```

## Tier Assignment

| Model | Use when |
|-------|----------|
| `haiku` | Pure lookup/summarize, zero judgment (fact-gather, doc audits) |
| `sonnet` | Any implementation, review, design, refactor — floor for shipped code |
| `opus` | User-requested only; hard architectural tradeoffs; never a standing default |

**Payment/auth/shared-API work: never below `sonnet`** — wrong output costs more than model upgrade.

## Skills

Skill frontmatter also accepts `model:`. `/wrapup` = `haiku` (mechanical: git state + file writes). Herdr = `sonnet` (complex terminal coordination).

## Locations

- Global: `~/.claude/agents/*.md` — applies all sessions
- Project: `<repo>/.claude/agents/*.md` — overrides global for that repo
- Skills: `~/.claude/skills/<name>/skill.md`

## What Happened Without Pinning (2026-10-06)

4 FE project agents + herdr skill had no `model:` → ran at session default. Accounted for 28% of Explore subagent cost + 13% of /wrapup cost in usage report.
