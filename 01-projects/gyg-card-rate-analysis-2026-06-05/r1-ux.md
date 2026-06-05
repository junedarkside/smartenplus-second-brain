---
name: r1-ux
description: Specialist — UX/Conversion Designer. Score card rate display gaps vs GYG reference. ROI/brand-fit/effort per pattern.
metadata:
  type: specialist-r1
  role: ux-conversion-designer
  page: gyg-card-conventions
  smartenplus_route: /activities
  source_note: GYG fetch blocked (DataDome). General knowledge used.
---

# R1 — UX/Conversion Designer (Card Rate Display)

**Goal:** identify rate-display patterns missing from SmartEnPlus `/activities` card vs GYG card conventions. Score ROI/brand-fit/effort.

**Scoring axes:**
- **ROI:** high (conversion lift) / med (trust/scanability lift) / low (polish only)
- **Brand-fit:** yes (premium calm) / maybe (neutral) / no (GYG-conversion-density smell)
- **Effort:** trivial (config/typography) / small (new prop) / medium (new component)

---

## Patterns (5 candidates)

| # | Pattern | ROI | Brand-fit | Effort |
|---|---------|-----|-----------|--------|
| UX-1 | "Likely to sell out" urgency badge | **high** | yes (travel urgency is honest) | small (data: `booking_pace` field or derive from `booked_count` vs capacity) |
| UX-2 | "Reserve now & pay later" badge near price | med | yes (matches `freeCancellation` bullet pattern) | trivial (1 conditional) |
| UX-3 | Per-unit hint on price ("per person" / "per group") | med | yes (already have `PricingTypeBadge` data) | trivial (use existing `getPricingType` util) |
| UX-4 | "Was $X" prefix on strikethrough | low | yes (clarity) | trivial (1 word) |
| UX-5 | Lowest-price-guarantee microcopy under price | low | yes (calm trust) | small (design + copy) |

## Observation: Current SmartEnPlus Already Mirrors GYG

**What works (matches GYG):**
- "From" label + price inline (compact mode, PricingDisplay.js:90-114) — same GYG pattern
- Brand-colored price (line 104) — high contrast
- Strikethrough original price + amber discount badge (lines 132-154) — standard OTA pattern
- "Price on Request" gray fallback for zero/missing rates (lines 36-87) — better than blank
- Lazy-load image + 220px hero — same height tier as GYG
- Entire card is clickable (line 92) — better than separate "View" CTA (GYG does same)
- `aria-label` on card (line 95) — accessibility win

**Headline:** structure is right. Gap is signal density.

## Critical Bug Found (P0)

**Strikethrough `original_price` divided by `rate`** (line 263 in DayTripCard): currency conversion can produce broken discount math if `original_price` stored in different currency than ratecards. **POTENTIAL BUG** — needs backend verify (`original_price_currency` field).

## Reuse Notes

- `utils/pricingTypeHelper.js` `getPricingType()` — exists, used by `PricingTypeBadge`. Reuse for UX-3.
- `helpers/formatCurrency.js` `formatCurrency()` — already used by PricingDisplay. Reuse.
- `COLORS.status.*` from `helpers/designSystem.js` — success/warning/error already mapped for any future color-coding.

## Related

- [[../gyg-page-analysis-2026-06-04]] — sibling: detail page
- [[r2-skeptic]]
- [[r3-leader-synthesis]]
