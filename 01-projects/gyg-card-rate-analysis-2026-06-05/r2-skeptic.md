---
name: r2-skeptic
description: Skeptic — challenges R1 UX/Conversion specialist. Auto-DROPs and conditional keeps with verification gates.
metadata:
  type: specialist-r2
  role: skeptic
  page: gyg-card-conventions
  smartenplus_route: /activities
---

# R2 — Skeptic (Card Rate Display)

**Goal:** challenge R1 UX/Conversion findings. Drop low-ROI / off-brand / out-of-scope patterns.

**Skeptic rules (mirrors gyg-page-analysis-2026-04-02):**
- auto-DROP if ROI=low + brand-fit=maybe
- auto-DROP if brand-fit=no (off-brand conversion-density smell)
- DOWNGRADE to P2 if effort > small and ROI not high
- CONDITIONAL KEEP if data dependency unverified

---

## Verdict

- **UX-1 (urgency badge):** ROI=high, brand-fit=yes, effort=small. **KEEP conditional P1.** Backend `booking_pace` or `capacity` field needed.
- **UX-2 (pay-later badge):** ROI=med, brand-fit=yes, effort=trivial. **KEEP conditional P2.** Backend `pay_later` flag needed.
- **UX-3 (per-unit hint):** ROI=med, brand-fit=yes, effort=trivial. **KEEP P1.** Reuse `getPricingType` util — zero new code.
- **UX-4 (was-prefix):** ROI=low, brand-fit=yes, effort=trivial. **KEEP P2.** Free polish.
- **UX-5 (lowest-price-guarantee):** ROI=low, brand-fit=yes, effort=small. **DEFER P3.** Marketing copy needs sign-off; not engineering scope.

## Skeptic Open Questions (3)

1. **P0 bug verify:** Is `original_price` stored in the same currency as `ratecards[].selling_rate`? If not, `/ rate` produces garbage discount math. Need backend `Contract.original_price_currency` field or guarantee same currency.
2. **UX-1 data:** Does `Contract` have `booking_pace` or `inventory_remaining`? If not, "Likely to sell out" can't be derived. Alternative: derive from `booked_count / capacity` (need `Contract.capacity`).
3. **UX-2 data:** Does `Contract` have `pay_at_property` or `reserve_now_pay_later` flag? If not, badge has no data source.

## Drop-to-P3 Rule (Leader adjudication)

Best-case for pattern. If verification fails at implementation, pattern drops to P3 — not P0/P1.

- **UX-1:** if no `booking_pace` AND `capacity` unavailable → P3 (cannot derive)
- **UX-2:** if no `pay_later` flag → P3 (cannot render)
- **UX-3:** no data dependency → no drop rule
- **UX-4:** no data dependency → no drop rule

## Color-Coding Discussion (Q from user)

User asked: "do we need fancy colour for rating?" (this is a separate question from rate display, but Skeptic addresses it in scope of visual design consistency)

**Position:** Skip color-coding. Reasons:
- GYG does NOT color-code. Uniform gold star. Industry standard.
- Viator/Booking.com color-code, but they need it — they sell 1000s of operators, signal density required
- SmartEnPlus: 1-3 ratings per tour typical. Number `4.8` is the signal, color is decoration
- Accessibility risk: red/green = colorblind failure (8% males, 0.5% females)
- Cultural: red=warning in West, red=lucky in Asia. Brand-consistent = uniform

**Verdict:** uniform `#FFA000` (current). No color prop.

## Adopted in Final Decision (2026-06-05)

User chose **Option A** after debate: keep drop-gate (`average_rating > 0`), skip color prop. Shipped in commit `3ce3c12` (rating gate change only).

## Related

- [[r1-ux]]
- [[r3-leader-synthesis]]
- [[../gyg-page-analysis-2026-06-04-overview|../gyg-page-analysis-2026-06-04]] — sibling: detail page analysis
