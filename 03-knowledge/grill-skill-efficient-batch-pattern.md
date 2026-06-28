# Grill Skill — Efficient Batch Pattern

## Summary
For multi-gap BD question doc generation, use **two-pass grill**: pre-fill template from existing data for clear gaps, run grill skill only for ambiguous sections. Saves 70–80% of interactive rounds vs naive grill-per-gap.

## Context
Pattern derived 2026-06-28 during [[products-live-catalog-audit]] Phase 2 (10 BD gap docs). Naive approach would be 10× grill = 20–40 user replies. Efficient approach = 1–2 grill rounds + 9 pre-fills.

## Details

### Pattern

**Pass A — Pre-fill (no user input needed)**
For each gap, fill template sections from existing snapshot/data:
- Gap (copy from gap-inventory)
- What we need from operator (derive from gap type)
- Operator profile (from existing operator patterns in catalog)
- Compliance checklist (standard from template)
- Next step (standard return fields)

**Pass B — Grill only for unknowns**
Run `/grill` skill ONLY on sections that need user/strategic input:
- Demand signal (supply vs demand gap)
- Commercial ask (commission tier, Net vs retail)
- Strategic priority (HIGH/MED/LOW classification)

### Section-by-section classification

| Section | Pre-fillable? | Source |
|---|---|---|
| Gap | ✅ always | gap-inventory.md row |
| Demand signal | ⚠️ sometimes | competitor research + hypothesis |
| What we need | ✅ always | gap type → operator type mapping |
| Operator profile | ✅ always | existing operator patterns |
| Commercial ask | ⚠️ sometimes | industry standard + finance confirmation |
| Compliance checklist | ✅ always | standard [[operator-outreach-question-template]] |
| Next step | ✅ always | standard return fields |

### Worked example (Phase 2 execution)

| Gap | Pre-fill needed | Grill needed | Reason |
|---|---|---|---|
| gap-001 charter | 6/7 sections | Demand signal | Supply gap confirmation |
| gap-002 transfer | 6/7 sections | Strategic priority | Could be intentional |
| gap-003 multi-day | 5/7 sections | Demand + Commercial | High AOV, new product |
| gap-004 event | 7/7 sections | none | Clear empty category |
| gap-005 attraction | 7/7 sections | none | Clear empty category |
| gap-006 food | 7/7 sections | none | Niche, low priority |
| gap-007 accommodation | 6/7 sections | Strategic priority | Possibly intentional |
| gap-008 day-tour | 6/7 sections | Demand signal | Geographic skew strategy |
| gap-009 spa | 6/7 sections | Commercial | High-margin ask |
| gap-010 other | 7/7 sections | none | Catch-all |

**Result:** 10 docs in ~5 minutes vs ~30–40 minutes interactive.

## Decision
Default to two-pass pattern for any multi-doc BD/template generation task. Only fall back to pure interactive grill when all sections are ambiguous.

## Tradeoffs

- **Pro:** Massive speed-up for batch work
- **Pro:** Templates stay consistent (pre-fill uses standard patterns)
- **Pro:** Grill rounds focused on highest-value sections
- **Con:** Pre-filled sections may miss user-specific context (mitigate: flag uncertain assumptions with `[ASSUMPTION — VERIFY]` markers)
- **Con:** If user wants different template structure, pre-fill needs rework

## Related

- [[operator-outreach-question-template]]
- [[products-live-catalog-audit]]
- [[live-catalog-discovery-protocol]]