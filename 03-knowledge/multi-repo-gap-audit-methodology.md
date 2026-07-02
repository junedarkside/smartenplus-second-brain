# Multi-Repo Gap Audit Methodology — 3-Agent Review

## Summary
When auditing a complex feature across multiple repos (backend + frontend + admin), single-agent review misses cross-cutting gaps. Pattern: fan out 3 specialized agents (Backend / Frontend / Integration) → adversarial verification → synthesized report.

## Process

**Phase 1: Scope the audit**
- Define feature boundary (e.g., "Booking Command Centre — all 3 repos")
- List all entry points (API endpoints, UI pages, user flows)
- Decide audit depth (full code vs critical paths only)

**Phase 2: Deploy agents**

**Agent 1 — Backend Specialist**
- Scans: models, views, serializers, signals, tasks, migrations
- Finds: dead code, missing guards, race conditions, data integrity holes
- Output: structured gap list with file:line references

**Agent 2 — Frontend Specialist**
- Scans: components, pages, hooks, API calls, state management
- Finds: a11y gaps, missing loading states, race conditions, broken flows
- Output: structured gap list with component/file references

**Agent 3 — Integration Specialist**
- Scans: contract between repos, API surface, data flow, error handling
- Finds: mismatched assumptions, missing error cases, incomplete sync
- Output: structured gap list with endpoint/flow references

**Phase 3: Adversarial verification**
Leader reads each gap → verifies against live code (no hallucinations)
- "grep claims zero callers" → actually grep
- "Field doesn't exist" → check models + serializers
- "FE sends hidden flag" → grep FE code
Kill false positives before reporting.

**Phase 4: Synthesize + prioritize**
- CRITICAL: security holes, data loss, broken workflows
- HIGH: UX gaps, integrity issues, scale risks
- MEDIUM/LOW: polish, optimizations, future-proofing

## Anti-Patterns

**Single agent scanning everything:**
- Misses cross-repo context
- Context window exhaustion
- No adversarial verification

**No verification:**
- Agent hallucinates gaps → report false positives
- Later implementation waste

**No prioritization:**
- 20 findings in flat list → user overwhelmed
- CRITICAL lost in noise

## Template Report

```markdown
# [Feature] Gap Audit

## Summary
Date, scope, 3-agent team (Backend/Frontend/Integration), findings count.

## CRITICAL

### C1 — [Title] ✅verified
File:line reference. What the gap is. Impact. Fix approach.

## HIGH
[M same format]

## Recommended fix order
1. Security triad
2. Data integrity
3. UX
```

## When to Use

- **Pre-launch audits** — catching holes before prod
- **Post-incident audits** — "how did this bug happen?"
- **Architecture reviews** — validating new multi-repo features
- **Debt cleanup** — finding accumulated gaps

## Time/Cost

3 agents × ~15-20 minutes each = ~1 hour total
Verification phase = ~30 minutes
Total: 1.5-2 hours for comprehensive audit

## Related
- [[code-review-patterns]] — single-repo review process
- [[adversarial-verification]] — cross-checking findings

## Context
SmartEnPlus session #210 — command-centre 3-agent gap audit found 7 CRITICAL + 9 HIGH gaps → fixed 6 of 7 CRITICAL in session #211.
