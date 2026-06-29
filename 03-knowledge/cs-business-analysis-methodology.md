# CS Business Analysis Methodology

## Summary
Structured approach for analyzing customer service centralization workflows from business perspective.

## Context
Use when analyzing CS workflows, customer service operations, or booking command center systems. Extracts workflow gaps, stakeholder concerns, and business risks.

## Analysis Framework

### 1. Workflow Gaps
Identify break points in current state machine where business impact occurs.

**Gap analysis format:**
```
### Gap Name (SEVERITY)
**Problem:** [What breaks in current workflow]
**Workflow break:** [Step-by-step failure scenario]
**Required fix:** [Specific solution]
**Impact:** [Business consequence]
```

**Severity levels:** BLOCKER (gates launch), MAJOR (production readiness), MINOR (polish)

### 2. Stakeholder Concerns
Capture perspectives from all actors in workflow: Staff, OTA, Operator, Customer.

**Stakeholder format:**
```
### Stakeholder Role
**Pain points:**
- [Specific operational friction]
- [Missing capability]
- [Process bottleneck]

**Quote:** "[Direct quote revealing the core concern]"
```

### 3. Top Business Gaps
Prioritize by severity × implementation cost.

**Gap prioritization:**
```
### Gap X: Name (SEVERITY)
**Severity:** [Business impact]
**Fix:** [Solution]
**Cost:** [Hours] (BE + FE + test breakdown)
**Owner:** [Team responsible]
```

### 4. Missing Business Rules
Document decision points where business rules are undefined.

**Rule format:**
```
**Rule #X:** [Rule name] — [Decision question]

**Current state:** [How workflow handles it today]
**Real-world scenario:** [Example failure case]
**Business impact:** [Consequences]
**Three options:** [Alternatives with tradeoffs]
**Recommendation:** [Proposed approach]
```

## Decision Points

Analysis supports "should we build this" decisions by providing:
- **What needs to be built** (specific blockers/gaps)
- **Why it's important** (business impact assessment)
- **How much effort** (implementation cost with breakdown)
- **Who owns it** (team assignment)
- **What's the sequence** (priority order with dependencies)

## Output Structure

**High-level analysis (supports decision-making):**
- 3-5 top blockers with cost estimates
- 7-10 major gaps catalogued
- 5 missing business rules documented
- Stakeholder perspectives captured

**Detailed implementation plan (supports execution):**
- Individual tickets/tasks for each blocker
- Acceptance criteria (Gherkin format)
- Technical specs (API changes, model changes, FE components)
- Dependency graph
- Testing requirements

## Related
- [[stakeholder-concern-capture-pattern]]
- [[blocker-identification-framework]]
- [[implementation-prioritization-matrix]]