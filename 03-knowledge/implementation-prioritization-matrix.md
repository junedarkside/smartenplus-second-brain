# Implementation Prioritization Matrix

## Summary
Systematic approach for sequencing implementation work, balancing business impact, technical dependencies, and resource constraints.

## Context
Use when transitioning from analysis to execution. Takes identified blockers/gaps and produces a buildable sequence with effort estimates and ownership.

## Prioritization Dimensions

### 1. Business Impact (Y-axis)
**BLOCKER** = Gates go-live (customer trust, safety, contract, revenue)
**MAJOR** = Production readiness (operational efficiency, customer perception)
**MINOR** = Optimization (UX polish, nice-to-have)

### 2. Technical Dependencies (X-axis)
**No deps** = Can build independently
**Sequential** = Requires other blockers first
**Parallel** = Can build simultaneously with others

### 3. Implementation Cost (Size)
**XS** <4h, **S** 4-8h, **M** 8-16h, **L** 16-32h, **XL** >32h

## Prioritization Matrix

```
         | No deps | Sequential | Parallel |
---------|---------|-----------|----------|
BLOCKER  |   DO 1st |  DO after dep | Can parallel |
MAJOR    | Defer   | Defer      | Defer |
MINOR    | Post-launch | Post-launch | Never |
```

**DO 1st:** Independent blockers → build immediately
**DO after dep:** Blockers with prerequisites → sequence after prerequisite
**Can parallel:** Independent blockers of similar size → simultaneous work
**Defer:** Post-launch backlog → business value but doesn't gate launch

## Sequencing Rules

### Rule 1: Unblockers First
Build in dependency order. If Blocker B requires Blocker A's API, build A first.

### Rule 2: Cost-Balance Parallelization
If Blocker A (6h) + Blocker B (10h) have no deps, can parallel. If limited to 1 BE dev, sequence by total time.

### Rule 3: Owner-Decision Gates
Stop before rules requiring owner confirmation. Don't build until business decides.

### Rule 4: Phase Boundary
If total blocker effort >40h, consider phased approach:
- **Phase 1:** Core blockers (minimum viable)
- **Phase 2:** Full blockers (complete solution)

## Effort Estimation Breakdown

### Standard Template

```
**Cost:** X hours (BE + FE + test + product)

BE: [Model changes + API + migrations] → Xh
FE: [Components + UI + states] → Yh  
Test: [Unit + integration + smoke] → Zh
Product: [SLA + business rules] → Wh

**Total:** X+Y+Z+W hours
```

### Rule of Thumb
- **Model + API + migration:** 3-6h (BE)
- **Component + UI + states:** 2-4h (FE)
- **Testing:** 20% of dev time
- **Product decisions:** 1-2h (if required)

## Launch Sequence Output

### Format

**Blockers (must gate go-live):**
1. **Blocker 1** — Xh (BE + FE + test)
2. **Blocker 2** — Yh (BE + FE + test)
3. **Blocker 3** — Zh (Ops + BE + FE)

**Total blocker effort:** ~X hours

**Can ship post-launch:**
- Major 1 (Zh) — [Owner if any]
- Major 2 (Yh) — [Owner if any]

**What can ship NOW (no new blockers):**
- [Existing features already built]
- [Features pending non-blocker work]

## Dependency Mapping

### Example from CS Analysis

```
NEW-1 (resolve-block guard, 6h)
  ↓
OQ-3 (SLA display, 10h)
  ↓ (uses resolve-block guard validation)
Emergency path (13.5h)
  ↓ (uses SLA infrastructure)
Magic link (4h)
```

**Parallel opportunities:**
- Magic link (4h) can run parallel to NEW-1 + OQ-3
- Email redesign (1.5h) can run parallel to any

**Critical path:** 6h + 10h + 13.5h = 29.5h
**With parallelization:** Max(29.5h, 4h) = 29.5h

## Owner Assignment Matrix

| Work Type | Owner | Examples |
|-----------|-------|----------|
| **Backend** | Backend team | Model changes, API, migrations, Celery tasks |
| **Frontend** | Frontend team | Components, UI, state, polling |
| **Ops** | Ops team | Runbooks, monitoring, duty contact spec |
| **Product** | Product owner | SLA definitions, business rules, policy decisions |
| **Comms** | Communications | Email templates, copy, messaging, trust context |

## Decision Points

### Before Implementation
1. **Approach decision:** Build all blockers? Phased? Accept risk and launch partial?
2. **Owner decisions:** Confirm business rules requiring owner input
3. **Resource availability:** Do we have BE + FE capacity for parallel work?

### During Implementation  
1. **Sequence adjustments:** If blocker blocked by external dependency, re-prioritize
2. **Scope changes:** If blocker more complex than estimated, consider phased approach
3. **Risk reassessment:** If new risks discovered, update blocker status

## Output Template

**Implementation Priorities (Launch Sequence):**

```
## Blockers (Must Gate Go-Live)

1. **[Blocker 1]** — Xh total
   - BE: Xh (model + API + migration)
   - FE: Yh (component + UI)
   - Test: Zh
   - Owner: [Team]

2. **[Blocker 2]** — Yh total
   - BE: Xh
   - FE: Yh  
   - Test: Zh
   - Owner: [Team]

**Total blocker effort:** ~X hours

## Can Ship Post-Launch

- **[Major 1]** — Zh (Owner: [Team])
- **[Major 2]** — Yh (Owner: [Team])

## What Can Ship NOW

- [Existing features already built, no new blockers]
```

## Related
- [[blocker-identification-framework]]
- [[cs-business-analysis-methodology]]
- [[missing-business-rules-framework]]