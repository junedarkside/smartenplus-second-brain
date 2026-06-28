# BD Commission Tier Framework

## Summary
Industry-standard commission rates per product category for SmartEnPlus operator outreach. Tier reflects margin economics + competitive landscape. Used as default in [[operator-outreach-question-template]] — confirm with finance before sending.

## Context
Derived 2026-06-28 during [[products-live-catalog-audit]] Phase 2 grill doc generation. Used as default for Commercial ask sections. SmartEnPlus-specific rates not documented in vault — pattern based on industry benchmarks (Booking.com, Klook, Viator public commission disclosures).

## Details

### Tier framework

| Category | Commission range | Rationale |
|---|---|---|
| **Transport (JOIN/PRIVATE)** | 15–20% | High volume, low AOV (~$10–50/booking). Operator margin already thin. |
| **Charter** | 15–20% | Similar to PRIVATE but hourly. Operator margin slightly higher (premium positioning). |
| **Day tours** | 18–22% | Mid AOV (~$30–150/booking). Operator margin healthier. |
| **Multi-day packages** | 15–20% | High AOV (~$200–2000) but operator margin tighter (covers lodging + guide). |
| **Spa / Wellness** | 20–25% | High margin service. Operator can absorb higher commission. |
| **Attraction tickets** | 10–15% | Low margin resellers. High volume. |
| **Event tickets** | 10–15% | Low margin resellers. Volume-based. |
| **Food / Dining** | 15–20% | Mid-tier service. |
| **Accommodation** | 12–18% | Hotel margins traditionally thin. Channel manager model. |
| **Other (SIM, insurance)** | 15–25% | Varies wildly — confirm per-product. |

### Payout structure (default)

- **Cadence:** Monthly
- **Timing:** T+7 from booking date (T+14 for accommodation)
- **Method:** Bank transfer, Wise, or operator-preferred

### Cancellation policy (default tiered)

| Time to service | Refund |
|---|---|
| 30+ days | 100% |
| 15–30 days | 50% |
| 7–14 days | 25% |
| <7 days | 0% |

Adjust per category (spa = 24h cutoff, attraction tickets = non-refundable).

## Decision
Default to these tiers in any new BD outreach unless finance has documented overrides. Flag in grill docs: "Confirm commission with finance if higher than 20%."

## Tradeoffs

- **Pro:** Reusable pattern across all 10 product categories
- **Pro:** Reflects real-world marketplace economics
- **Con:** SmartEnPlus-specific rates may differ — confirm with finance before contract
- **Con:** Volume discounts / seasonal tiers not captured — add per-deal

## Related

- [[operator-outreach-question-template]]
- [[products-live-catalog-audit]]
- [[business-development-thailand-bundling-margin]] (margin tier analysis)