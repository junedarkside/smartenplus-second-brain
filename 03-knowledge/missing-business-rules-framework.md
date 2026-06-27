# Missing Business Rules Framework

## Summary
Structured approach for documenting business rule gaps identified during workflow analysis, capturing undefined decision points that could block implementation.

## Context
Use when workflow analysis reveals edge cases, gaps, or undefined behaviors. These aren't bugs — they're business rules that were never specified.

## Rule Identification

**Signal:** "What happens when..." questions have no documented answer

**Common sources:**
- Edge cases (quarantined bookings, expired tokens)
- Policy conflicts (OTA vs. direct customer treatment)
- Validation boundaries (what's rejectable vs. admin discretion)
- Operational handoffs (who does what in emergency scenarios)

## Rule Documentation Format

### Template

```
**Rule #X:** [Rule name] — [Decision question]

**Current state:** [How workflow handles it today — often "undefined" or "ad-hoc"]

**Real-world scenario:** [Example failure case showing consequences]

**Business impact:** [Customer impact, operational cost, risk exposure]

**Three options:** [Alternative approaches with tradeoffs]

**Recommendation:** [Proposed solution + rationale]

**Implementation priority:** [BLOCKER / MAJOR / MINOR]

**Owner decision:** [Who must confirm?]
```

## Rule Categories

### 1. Edge Case Handling
What happens at workflow boundaries?

**Examples:**
- Quarantined bookings + customer requests
- Expired magic links + admin-initiated tickets
- Mixed OTA + direct bookings on same trip

### 2. Policy Conflicts
When business rules conflict, which takes precedence?

**Examples:**
- OTA guest portal: service comms vs. marketing restrictions
- Customer self-service vs. operational complexity
- Immediate UX vs. backend validation

### 3. Validation Boundaries
What's auto-rejected vs. admin discretion?

**Examples:**
- Past date changes (obviously invalid)
- Sold-out requests (operator knowledge required)
- Policy exceptions (VIP handling)

### 4. Operational Handoffs
Who's responsible in emergency scenarios?

**Examples:**
- 4am weather cancellations
- Duty contact specifications
- Fast-track emergency paths

## Decision Process

### Phase 1: Categorize
**BLOCKER** = Contract risk, safety, or legal exposure
**MAJOR** = Operational efficiency or customer perception
**MINOR** = Nice-to-have optimization

### Phase 2: Owner Confirmation
Map rules to decision owners:

| Rule Category | Owner | Why |
|---------------|-------|-----|
| Policy conflicts | Owner | Commercial decision |
| Legal/contract | Legal | Compliance |
| Operational | Ops | Workflow expertise |
| Technical | Engineering | Implementation |

### Phase 3: Implementation
For BLOCKER/MAJOR rules requiring code:

**Option A: Code guard + policy**
- ✅ Guaranteed enforcement
- ❌ Rigid for edge cases

**Option B: Policy-only**
- ✅ Flexible for human judgment
- ❌ Human error-prone

**Option C: Both (recommended)**
- Code guard defaults
- Policy documents exceptions
- Override for edge cases

## Examples from CS Analysis

### Rule #1: Quarantined Bookings + Customer Request
**Decision:** Block submission for quarantined bookings
**Priority:** MEDIUM
**Owner:** Engineering decision

### Rule #2: Mixed-Booking Cancellation  
**Decision:** Manual process documented, v2 architecture planned
**Priority:** LOW (v2 feature)
**Owner:** Product decision

### Rule #3: `closed_no_action` Resolution Note Mandatory
**Decision:** Model-level validation (required field)
**Priority:** HIGH (customer perception)
**Owner:** Engineering

### Rule #4: Channel Conflict — No Upsell in OTA Portal
**Decision:** OWNER CONFIRMATION REQUIRED (contract risk)
**Priority:** BLOCKER (OTA launch gate)
**Owner:** Owner decision

### Rule #5: Request Feasibility Validation
**Decision:** Hybrid — API validates obvious rules, admin handles edge cases
**Priority:** MEDIUM
**Owner:** Engineering

## Anti-Patterns

❌ **Skip documentation:** "We'll figure it out when we hit it" → emergency decisions
❌ **Engineering-only:** "Dev decides business rule" → misaligned with business needs
❌ **Over-specification:** Documenting every edge case → analysis paralysis

✅ **Document undefined rules:** Capture decision points, not every permutation
✅ **Owner confirmation:** Business rules require business owner input
✅ **Implementation guidance:** Provide options with tradeoffs, not just one answer

## Output Format

**Missing business rules summary:**

```
## Missing Business Rules (N total)

**Rule #1:** [Name] — [Decision question]
**Rule #2:** [Name] — [Decision question]
...

**Summary by priority:**
- BLOCKER: [Count] (require owner decision)
- MAJOR: [Count] (engineering discretion)
- MINOR: [Count] (defer)

**Decision required:** [Which rules need owner confirmation before implementation]
```

## Related
- [[cs-business-analysis-methodology]]
- [[blocker-identification-framework]]
- [[stakeholder-concern-capture-pattern]]