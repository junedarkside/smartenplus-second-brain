---
name: gyg-card-rate-analysis-2026-06-05
description: SmartEnPlus /activities product card rate display vs GYG reference. UX/Conversion specialist review → Skeptic → Leader → 5 P0/P1/P2 patterns. Scope: card on listing page rate display, NOT detail page. Pairs with [[gyg-page-analysis-2026-06-04]] (detail page).
metadata:
  type: project
  page: http://localhost:3000/activities
  reference: https://www.getyourguide.com (bangkok-l36, phuket-l400, paris-l17, rome-l27)
  smartenplus_route: /activities
  fetch_note: GYG blocked by DataDome (HTTP 403 on all city pages, no Wayback snapshots). Reference relies on general knowledge of GYG card conventions.
  date: 2026-06-05
---

# GYG Card Rate Display — Debate 2026-06-05

## Summary

SmartEnPlus `/activities` card rate display (in `DayTripCard` + `PricingDisplay` compact mode) vs GYG card conventions. 1 specialist round (UX/Conversion) → Skeptic → Leader → final 5 patterns: 1 P0 (no-change), 2 P1, 2 P2. Top finding: SmartEnPlus already mirrors GYG card layout in spirit — gap is signal density (urgency, trust, per-unit label), not structure.

## Decision (Adopted 2026-06-05)

**Option A: keep drop-gate, skip color.** Shipped in commit `3ce3c12` on branch `260605-fix/activities-pagination-grid-math` (later merged to develop).

- Dropped `review_count >= 5` gate on `DayTripCard.js:236` → now `average_rating > 0`. Rating shows from 1 review.
- Skipped color-coding (GYG standard = uniform gold `#FFA000`). User confirmed: color = decoration, number is the signal.

## Context

**Why this audit:** prior 2026-06-04 GYG analysis covered the **detail page** only. User asked to extend to the **listing card** (`/activities`) — specifically the rate display. Card is the first conversion surface user sees; bad rate display = scroll-past = lost booking.

**SmartEnPlus state (today):**
- Page: `pages/activities/index.js` → `FilterDayTripsPage` → `DayTripList` → `DayTripCard`
- Card: `components/activities/browse/DayTripCard.js` (273 LoC, GYG-inspired per file comment line 2)
- Rate sub-component: `components/activities/shared/PricingDisplay.js` (170 LoC, 3 branches: no-rate gray fallback, compact inline, full with discount)
- Data: `useGetContractsQuery` from `store/api/dayTripsApi.js:53` → `Math.min(...validSellingRates)` (line 66 in DayTripCard)
- Currency: `useCurrency()` context, division by `currentRate.rate` (lines 32-34, 262-263)

## Gaps vs GYG (general reference)

1. **No "Likely to sell out" urgency badge** — high ROI, needs backend `booking_pace`/`capacity` field
2. **No "Reserve now & pay later" badge** — med ROI, needs backend `pay_later` flag
3. **No per-unit hint** — `From ฿1,200` ambiguous. Have `PricingTypeBadge` data, can render `/ person` | `/ vehicle`
4. **No "Was" prefix on strikethrough** — `$1,500 $1,200` reads as two prices
5. **No "Lowest price guarantee" trust signal** — GYG footer pattern

## Specialist Findings

See `r1-ux.md` for full scoring matrix.

## Discussion: Debate

See `r2-skeptic.md` for auto-DROPs and conditional keeps.

## Leader Synthesis

See `r3-leader-synthesis.md` for final 5 ranked P0 → P2.

## Key Files

### Vault files created
- `01-projects/gyg-card-rate-analysis-2026-06-05/r1-ux.md`
- `01-projects/gyg-card-rate-analysis-2026-06-05/r2-skeptic.md`
- `01-projects/gyg-card-rate-analysis-2026-06-05/r3-leader-synthesis.md`

### SmartEnPlus components referenced
- `components/activities/browse/DayTripCard.js`
- `components/activities/shared/PricingDisplay.js`
- `helpers/formatCurrency.js`
- `helpers/designSystem.js`

## Out of Scope

- Detail page rate display (covered by [[gyg-page-analysis-2026-06-04]])
- Search/filter bar rate display
- AB test for wording variants
- AI-summarized price ("Best price for July 4-6 weekend") — P3 future

## Related

- [[gyg-page-analysis-2026-06-04]] — sibling: detail page analysis
- [[experience-detail-page-redesign-2026-06-02]] — 9 components shipped, includes detail rate display
- [[business-development-thailand-platform-analysis]] — GYG competitive positioning
- [[trip-detail-uxui-audit-2026-05-22]] — prior detail page audit pattern
