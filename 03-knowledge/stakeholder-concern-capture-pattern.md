# Stakeholder Concern Capture Pattern

## Summary
Systematic method for capturing stakeholder perspectives during workflow analysis, ensuring business requirements map to real operational pain points.

## Context
Use during business analysis, requirements gathering, or stakeholder interviews. Captures not just "what they want" but "why they care" — reveals operational friction points.

## Stakeholder Identification

**Map all actors in workflow:**
- **Staff/Internal:** Admin, CS agents, operations team
- **External partners:** OTA, operators, suppliers
- **End customers:** Direct customers, OTA guests
- **Regulatory:** Compliance, legal, safety

**Question:** "Who touches this workflow? Who's affected when it breaks?"

## Capture Format

### Per Stakeholder

```
### Stakeholder Role

**Pain points:**
- [Specific operational friction]
- [Missing capability causing re-work]
- [Process bottleneck]
- [Tool gap]

**Quote:** "[Direct quote revealing the core concern — use their words]"

**Voting power:** [Does this stakeholder have veto power?]
```

**Quote criteria:**
- Use stakeholder's exact words (captures emotion + terminology)
- Reveals the "why" behind the pain point
- Shows priority (what they mention first = most important)
- Exposes workarounds (shows what they're doing now)

## Analysis Synthesis

### Cross-Cutting Themes
Identify concerns raised by multiple stakeholders independently:

| Theme | Who raised it | Current doc status |
|-------|--------------|-------------------|
| **No SLA on `awaiting_ota_update`** | Customer, OTA, Admin | OQ-3 MAJOR — UNRESOLVED |
| **Emergency cancellation path** | Operator, Admin | NOT IN DOC — new gap |

**Pattern:** If 3+ stakeholders raise same issue independently → BLOCKER (regardless of technical severity)

### Voice Summaries
Synthesize each stakeholder's perspective:

```
#### 🔧 Staff/Internal (Nong — CS Lead, 40-60 tickets/day)
**Core complaint:** [One-sentence summary of primary pain]

**New gaps surfaced:**
- [Gap 1 with scenario]
- [Gap 2 with scenario]

**Highest priority ask:** [Specific action they need]
```

## Validation Technique

**Multi-persona simulation (5-voice method):**
1. Create 5 personas based on real stakeholder interviews
2. Each reads full doc cold (no prior context)
3. Each gives unfiltered feedback
4. PM synthesizes cross-cutting themes
5. All voices available in full transcript

**Reveals:**
- Gaps NOT in documentation (stakeholders surface them)
- Documentation disagreements (claim vs. reality mismatch)
- Priority misalignment (dev focuses on X, stakeholders need Y)

## Decision Points

**Stakeholder concerns drive:**
- **Priority:** If Operator raises safety issue → BLOCKER (regardless of effort)
- **Scope:** OTA contract risk → owner decision required before launch
- **Tradeoffs:** Customer UX vs. Staff efficiency → product decision

## Output Examples

### From CS Centralization Analysis

**Staff pain:** "`awaiting_ota_update` must block Resolve until at least one `OtaBookingEvent` is created after ticket entered that status. Without this guard, admin can click Resolve on Klook's verbal confirmation before the sync lands — customer sees 'Approved' on stale data."

**OTA pain:** "Dedicated OTA forwarding channel needed with acknowledgment receipt + SLA (proposed: 2h business hours). Currently 'email admin' with no SLA."

**Operator pain:** "Fast-track emergency cancellation path needed — bypasses full state machine, fires SES to all affected pax immediately without waiting for Supabase sync. 15min sync unacceptable for same-day; stale manifests = safety issue."

**Customer pain:** "Mandatory expected-response-time shown at ticket submission. Ties directly to SLA blocker. `closed_no_action` label 'No Change Needed' implies request was ignored — resolution_note must be mandatory here, not optional."

## Anti-Patterns

❌ **Generic capture:** "Staff want better UX" (too vague)
❌ **Technical translation:** "Stakeholder wants API endpoint X" (loses business context)
❌ **Aggregation:** "Stakeholders want faster resolution" (masks different needs)

✅ **Specific with quotes:** "Admin must resolve waiting for Supabase update → creates 'Approved' lie → customer calls OTA → credibility collapse"

## Related
- [[cs-business-analysis-methodology]]
- [[blocker-identification-framework]]
- [[missing-business-rules-framework]]