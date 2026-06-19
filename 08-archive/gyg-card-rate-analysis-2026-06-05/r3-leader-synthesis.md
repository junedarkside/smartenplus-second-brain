---
name: r3-leader-synthesis
description: R3 Leader. Adjudicate Skeptic. Final 5 with P0/P1/P2 ranking. Implementation hints + LoC estimate per pattern.
metadata:
  type: synthesis
  role: leader
  page: gyg-card-conventions
  smartenplus_route: /activities
---

# R3 — Leader Synthesis (Card Rate Display)

**Role:** adjudicate R1↔R2. Final 5 patterns with P0/P1/P2 ranking.

**Priority rubric:**
- **P0 = free-win tier:** trivial effort + brand-fit yes + visible-or-correctness signal
- **P1 = trust/scanability lift + brand-fit yes** (med-high ROI, small effort)
- **P2 = polish + small/medium effort + brand-fit yes/maybe** (low-med ROI, optional)
- **P3 = backend debt / future / deferred**

**Skeptic open questions (3):** P0 bug verify (currency mismatch), UX-1 data (booking_pace), UX-2 data (pay_later).

**Leader ruling (drop-to-P3 rule):** assume best-case for the pattern. If verification fails, the pattern drops to P3.

---

## Skeptic Verdict Adoption

| Skeptic Verdict | Leader Action | Reason |
|-----------------|---------------|--------|
| UX-1 KEEP conditional P1 | Adopt as P1 | Yes brand + high ROI + small effort. Conditional on backend data. |
| UX-2 KEEP conditional P2 | Adopt as P2 | Med ROI + yes brand + trivial. Conditional on backend data. |
| UX-3 KEEP P1 | Adopt as P1 | Med ROI + yes brand + trivial. Zero data dependency. Free win. |
| UX-4 KEEP P2 | Adopt as P2 | Low ROI + yes brand + trivial. Free polish. |
| UX-5 DEFER P3 | Adopt as P3 | Marketing copy scope, not engineering. |

---

## Final 5 (ranked P0 → P2)

### Final 1 — P0: Verify `original_price` currency (correctness)

- **Priority:** P0
- **ROI:** high (correctness, prevents broken discount math = trust destruction)
- **Brand-fit:** yes
- **Effort:** small (1 backend ask + 1 frontend guard)
- **Caveat:** Verify `Contract.original_price` in same currency as `ratecards[].selling_rate`. If mismatch, frontend divide `/ rate` produces garbage.

### Final 2 — P1: Per-unit hint on price

- **Priority:** P1
- **ROI:** med (clarity, prevents price-confusion complaints)
- **Brand-fit:** yes
- **Effort:** trivial
- **What-Works (GYG):** "per person" / "per group" suffix on card price (GYG defers to detail page; SmartEnPlus can show on card)
- **Implementation hint:** Modify `PricingDisplay.js` to accept optional `unit` prop, render after price. Modify `DayTripCard.js:260-267` to pass `unit` derived from `getPricingType(workingContract)`.
- **Reuse:** `utils/pricingTypeHelper.js` `getPricingType()` — no new utility.
- **Estimated LoC:** 4-6

### Final 3 — P1: "Likely to sell out" urgency badge

- **Priority:** P1
- **ROI:** high (urgency = conversion)
- **Brand-fit:** yes
- **Effort:** small
- **Caveat:** **Verify `Contract.booking_pace` or `capacity` field exists.** If not, defer P3.
- **Implementation hint:** New component `components/activities/browse/UrgencyBadge.js` rendered top-left of card (heart on top-right). Conditional on `remaining / capacity < 0.2`.
- **Estimated LoC:** 8-12

### Final 4 — P2: "Reserve now & pay later" badge

- **Priority:** P2
- **ROI:** med (trust lift)
- **Brand-fit:** yes
- **Effort:** trivial
- **Caveat:** **Verify `Contract.pay_later` flag exists.** If not, defer P3.
- **Implementation hint:** New component `components/activities/browse/PayLaterBadge.js`. Render as bullet in existing feature row (matches `freeCancellation` pattern).
- **Estimated LoC:** 4-6

### Final 5 — P2: "Was $X" prefix on strikethrough

- **Priority:** P2
- **ROI:** low (clarity polish)
- **Brand-fit:** yes
- **Effort:** trivial
- **Implementation hint:** Change `PricingDisplay.js:140-143` to render `Was {formatCurrency(originalPrice, currency)}` instead of just `{formatCurrency(originalPrice, currency)}`.
- **Estimated LoC:** 1

---

## P3 Backend Debt (Out of scope, flagged for future)

| Pattern | Backend Need | Round |
|---------|--------------|-------|
| Audio guide 41 langs | `audio_guide_languages[]` on Contract | P3 |
| Private group badge | `is_private_group` boolean on Contract | P3 |
| Per-aspect rating (Guide/Transport/Value) | `ReviewAspect` model + aggregation | P3 |
| Provider response to reviews | `provider_response_text` + `provider_response_date` on Review | P3 |
| AI-summarized review | LLM service + cache + display | P3 (user-deferred) |
| Lowest-price-guarantee | Marketing copy decision | P3 (deferred) |

---

## Out-of-Scope This Round

- Color-coding (uniform gold standard, no ROI justification)
- "New" badge for low-review tours (separate task, may add if data shows low-review cards lose clicks)
- Cherry-picked 5-star reviews (off-brand)
- Newsletter signup (platform-wide)
- Currency code overlay in price string (currency symbol already handles)

---

## Implementation Order (recommended)

1. **P0 bug verify** — confirm `original_price` currency. Add frontend guard if mismatch. Trivial.
2. **P1 UX-3 per-unit hint** — reuse `getPricingType`, ship same week.
3. **P1 UX-1 urgency badge** — conditional on backend field. Verify, then ship.
4. **P2 UX-4 "Was" prefix** — 1-line edit, ship any time.
5. **P2 UX-2 pay-later badge** — conditional on backend field. Verify, then ship.

---

## Adopted 2026-06-05 (this session)

- **P0 (currency verify)**: SKIPPED — no time to verify backend in this session, deferred to next round
- **Drop rating gate**: SHIPPED (commit `3ce3c12`) — adjacent fix, related but separate scope
- **Color-coding**: REJECTED — uniform gold standard

## Related

- [[r1-ux]]
- [[r2-skeptic]]
- [[../gyg-page-analysis-2026-06-04-overview|../gyg-page-analysis-2026-06-04]] — sibling: detail page
- [[../activities-pagination-ux-audit-2026-06-05]] — sibling: pagination audit (this session)
