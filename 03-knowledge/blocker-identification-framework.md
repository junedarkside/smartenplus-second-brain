# Blocker Identification Framework

## Summary
Systematic approach for identifying, categorizing, and prioritizing project blockers with implementation cost estimates.

## Context
Use during project analysis, technical debt assessment, or go-live readiness reviews. Separates "must fix before launch" from "can defer post-launch."

## Blocker Definition

**BLOCKER** = Issue that MUST be resolved before go-live because:
- Customer credibility collapse (trust destruction)
- Safety/legal risk (regulatory compliance, physical safety)
- Revenue protection (prevents revenue loss)
- Contract breach (violates SLA or partner agreements)

**MAJOR** = Production readiness issue that impacts operations but doesn't gate launch.

## Identification Process

### 1. Workflow Trace
Map current state machine and identify break points:

```
Step 1 → Step 2 → [BREAK] → Step 4
```

**Question:** "What breaks when this step fails?"

### 2. Impact Assessment
Categorize by business consequence:

| Impact Type | BLOCKER | MAJOR | MINOR |
|-------------|---------|-------|-------|
| Customer trust loss | ✅ | ✅ | ❌ |
| Safety risk | ✅ | ❌ | ❌ |
| Contract breach | ✅ | ❌ | ❌ |
| Revenue loss | ✅ | ✅ | ❌ |
| Operational inefficiency | ❌ | ✅ | ✅ |
| UX friction | ❌ | ✅ | ✅ |

### 3. Cost Estimation
Break down implementation effort by component:

```
Total hours = BE + FE + Ops + Product decisions

BE: Model changes + API endpoints + migrations
FE: Components + UI + states  
Ops: Celery tasks + monitoring + runbooks
Product: SLA definitions + business rules
```

**Rule of thumb:** If blocker >40h, split into phases.

### 4. Owner Assignment
Map to team accountable for execution:

- **Backend** (BE): Database, API, business logic
- **Frontend** (FE): Components, UI, state management
- **Product:** SLA, business rules, policy decisions
- **Ops:** Monitoring, runbooks, deployment
- **Comms:** Email templates, copy, messaging

## Prioritization Matrix

```
         | Low Cost | High Cost |
---------|----------|-----------|
BLOCKER  |   DO     |   SPLIT   |
MAJOR    |  DEFER   |  DEFER    |
MINOR    |  IGNORE  |  IGNORE   |
```

**DO:** Build immediately (gates launch)
**SPLIT:** Phase approach (Phase 1: core, Phase 2: full)
**DEFER:** Post-launch backlog
**IGNORE:** Won't fix

## Output Format

**Top 5 blockers (from analysis):**

| # | Blocker | Severity | Fix | Cost | Owner |
|---|---------|----------|-----|------|-------|
| 1 | Name | BLOCKER | Solution | 6h (3h BE + 2h FE + 1h test) | Backend |
| 2 | Name | BLOCKER | Solution | 10h (6h BE + 3h FE + 1h product) | Product |

**Launch sequence:** Blocker 1 → Blocker 2 → Blocker 3 → (optional: 4+5)

## Decision Support

Framework provides **go/no-go** decision input:
- **What needs to be built?** (5 specific blockers)
- **Why is it important?** (business impact)
- **How much effort?** (30.5h total)
- **Who owns it?** (team assignment)
- **What's the sequence?** (priority order)

## Related
- [[cs-business-analysis-methodology]]
- [[implementation-prioritization-matrix]]
- [[stakeholder-concern-capture-pattern]]