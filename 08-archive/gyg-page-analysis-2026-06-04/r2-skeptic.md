---
name: r2-skeptic
description: R2 Skeptic. Challenges every R1 missing-candidate. Enforces max-5 cap. Auto-DROP brand-fit=no. Auto-DROP ROI=low + brand-fit=maybe. Outputs final 5 ranked.
metadata:
  type: specialist-r2
  role: skeptic
  page: gyg-846675-chiang-rai
  smartenplus_route: /activities/detail/[...slug]
---

# R2 — Skeptic

**Role:** challenge every missing-candidate. Enforce max-5 cap. Reject off-brand.

**Skeptic rules (auto-applied):**
- brand-fit=no → DROP
- ROI=low AND brand-fit=maybe → DROP
- backend debt (audio guide, private group, review aspects) → DEFER P3
- user-deferred (AI summary) → DROP

**Tiebreak order (when ranking):** ROI high→low, brand-fit yes→maybe→no, effort trivial→large.

---

## Auto-DROP (no debate)

| ID | Pattern | Reason |
|----|---------|--------|
| UX-2 | Per-aspect rating breakdown | Backend debt (ReviewAspect model). DEFER P3. |
| UX-6 | SEO footer blocks (4×20 lists) | brand-fit=no (GYG-conversion-density). |
| P3-1 | Audio guide 41 langs | Backend debt. DEFER P3. |
| P3-2 | Private group badge | Backend debt. DEFER P3. |
| DEFER-1 | AI-summarized review | User-deferred. |
| UX-9 | Provider response to reviews | Likely backend debt. DEFER P3 pending verify. |

---

## Challenges (5 candidates remaining)

### C1 — UX-1: Not-suitable-for badges

- **R1-UX claim:** ROI=med, brand-fit=yes, effort=small
- **Skeptic counter:** GYG shows single example ("People with mobility impairments"). SmartEnPlus may have `difficulty_level` enum (EASY/MODERATE/CHALLENGING) — converting enum to badge is trivial, but "Not suitable for" is a different framing. Need to verify: does SmartEnPlus backend have a `restrictions` field, or is `difficulty_level` the only signal? If only `difficulty_level`, this is "difficulty badge reframe" not "new field".
- **Verdict:** KEEP
- **Reasoning:** Trust signal, low risk. Effort=small regardless of source field. Brand-fit=yes. R1-UX scoring holds.

---

### C2 — UX-3: Review sort + filter

- **R1-UX claim:** ROI=med, brand-fit=maybe, effort=medium
- **Skeptic counter:** Sort/filter only matters if `review_count >= 20`. SmartEnPlus tours may have <20 reviews. Filter dropdown on a 5-review page = empty state ugliness. Also: `ReviewListByProduct` may not be client-rendered (could be SSR/SSG baked in). Need to verify data flow before committing.
- **Verdict:** DOWNGRADE
- **Reasoning:** Brand-fit stays maybe. Effort may be larger than medium if SSR vs client mismatch. R1-UX said "client-rendered" — verify. If reviews are SSR, need to lift to client state OR add API param. **Leader should flag for verify before commit.**

---

### C3 — UX-4: Page feedback widget

- **R1-UX claim:** ROI=low, brand-fit=maybe, effort=small
- **Skeptic counter:** ROI=low AND brand-fit=maybe → **AUTO-DROP per Skeptic rule.** Trivial effort does not save it. "No conversion lift + neutral brand" = noise.
- **Verdict:** DROP
- **Reasoning:** Strict Skeptic enforcement. ROI=low + brand-fit=maybe = auto-DROP. GYG's widget is generic — not a pattern SmartEnPlus needs to copy. Telemetry can be added to GA event instead, zero UI cost.

---

### C4 — UX-5: Footer meta strip (Product ID + provider)

- **R1-UX claim:** ROI=low, brand-fit=yes, effort=trivial
- **Skeptic counter:** ROI=low BUT brand-fit=yes AND effort=trivial. Skeptic rule for ROI=low says drop when brand-fit=maybe. This is brand-fit=yes + trivial effort. Borderline. Also overlaps with SEO-9 (provider in JSON-LD). Free win if it's literally 1 line.
- **Verdict:** KEEP
- **Reasoning:** Trivial effort + yes brand-fit. No cost. Doubles as SEO-9 (provider in JSON-LD). **Caveat:** must verify it doesn't duplicate existing info already shown in `ExperienceTitleArea` operator logo. If already shown, this is pure noise — DROP. If not shown, KEEP.

---

### C5 — UX-7: Review thumbnails

- **R1-UX claim:** ROI=med, brand-fit=yes, effort=small
- **Skeptic counter:** R1-UX said "verify backend has field". SmartEnPlus `Review` model — does it have `images[]` or `photos[]`? If yes, KEEP. If no, this is backend debt = DEFER P3. **Block on verify.**
- **Verdict:** KEEP (conditional)
- **Reasoning:** ROI=med + brand-fit=yes. If backend has field, effort=small. Standard OTA pattern. **Caveat: must verify Review.images[] exists in backend before commit.**

---

### C6 — UX-8: "For reference only" itinerary disclaimer

- **R1-UX claim:** ROI=low, brand-fit=yes, effort=trivial
- **Skeptic counter:** ROI=low BUT brand-fit=yes + effort=trivial. Below Skeptic auto-DROP threshold (which requires brand-fit=maybe). Brand-fit=yes saves it. Trivial = no cost.
- **Verdict:** KEEP
- **Reasoning:** Effort=trivial. Brand-fit=yes. Legal-ish disclaimer = reduces support burden on "but the schedule said..." complaints. Pure free win.

---

### C7 — UX-10: Stop-type legend (Main / Other stop)

- **R1-UX claim:** ROI=low, brand-fit=maybe, effort=small
- **Skeptic counter:** ROI=low AND brand-fit=maybe → **AUTO-DROP per Skeptic rule.** Even though effort=small, the candidate fails the dual condition. GYG's legend is a differentiator only because GYG has many "other stops" in mixed itineraries. SmartEnPlus tours are typically curated with fewer stops — legend may add visual noise without informational gain.
- **Verdict:** DROP
- **Reasoning:** ROI=low + brand-fit=maybe = auto-DROP. GYG-specific pattern. Skip.

---

## Final 5 After Skeptic

| Rank | ID | Pattern | ROI | Brand-fit | Effort | Notes |
|------|----|---------|-----|-----------|--------|-------|
| 1 | UX-1 | Not-suitable-for badges | med | yes | small | Trust signal, low risk |
| 2 | UX-7 | Review thumbnails | med | yes | small | Conditional: verify Review.images[] backend field |
| 3 | UX-5 | Footer meta strip | low | yes | trivial | Doubles as SEO-9. Caveat: verify no duplicate in ExperienceTitleArea. |
| 4 | UX-8 | "For reference only" disclaimer | low | yes | trivial | Legal disclaimer, free win |
| 5 | UX-3 | Review sort + filter | med | maybe | medium | DOWNGRADE: verify SSR vs client data flow before commit |

**5 patterns. Cap enforced.**

**DROPPED (with reason):**
- UX-2 (per-aspect rating) — P3 backend debt
- UX-4 (page feedback) — ROI=low + brand-fit=maybe auto-drop
- UX-6 (SEO footer blocks) — brand-fit=no auto-drop
- UX-9 (provider response) — P3 backend debt
- UX-10 (stop-type legend) — ROI=low + brand-fit=maybe auto-drop
- Audio guide 41 langs — P3 backend debt
- Private group badge — P3 backend debt
- AI summary — user-deferred

---

## Open Questions for Leader

1. **UX-7 (review thumbnails):** Does `Review` model have `images[]` field? If no, defer P3. If yes, implement.
2. **UX-3 (sort/filter):** Is `ReviewListByProduct` client-rendered or SSR/SSG? Sort/filter needs client state. Verify before commit.
3. **UX-5 (footer meta):** Is `operator.operator_name` already visible in `ExperienceTitleArea`? If yes, this is duplicate → DROP or reframe.
4. **UX-1 (not-suitable-for):** Is there a `restrictions` TextField on Contract, or only `difficulty_level` enum? Verify source field.

Leader must adjudicate these before final synthesis.

## Verification Checklist

Pulled from Open Questions above. Each must clear before commit. If verify fails, pattern drops to P3 (not P0/P1/P2) — see main doc Verification Matrix for downstream impact.

| # | Pattern | Verify | Where | Owner | Drop-to-P3 if |
|---|---------|--------|-------|-------|---------------|
| V1 | UX-1 Not-suitable-for | `Contract.restrictions` TextField exists OR `difficulty_level` enum sufficient | Django admin or API response sample | Backend | Neither field gives a usable signal — defer P3 |
| V2 | UX-3 Review sort + filter | `ReviewListByProduct` is client-rendered (not SSR/SSG baked) | Component source + Redux store | Frontend lead | SSR/SSG — needs API params, effort medium → large |
| V3 | UX-5 Footer meta | `operator.operator_name` not already shown in `ExperienceTitleArea` | Read `ExperienceTitleArea.js` | Frontend lead | Already visible — DROP entirely (duplicate = noise) |
| V4 | UX-7 Review thumbnails | `Review.images[]` array in backend serializer response | Django `Review` model + API sample | Backend | Field absent — defer P3, no frontend workaround |

**Recommended order:** V3 + V2 first (frontend-only inspection, < 1 dev-day), then V1 + V4 (need backend team, ~2 dev-days including async).

---

## SEO Cross-Reference

| SEO ID | Pattern | Action |
|--------|---------|--------|
| SEO-2 | TouristAttraction schema | Add to `DayTripDetailSEO.js`. P1. Trivial. |
| SEO-3 | Review schema with author + datePublished | Add to `DayTripDetailSEO.js`. P1. Small. |
| SEO-5 | BreadcrumbList schema | Add to `DayTripDetailSEO.js`. P1. Trivial. |
| SEO-9 | Footer meta + provider JSON-LD | **Merged into UX-5.** One fix. |

**SEO findings parallel to UX-5/7/3 — should be bundled or kept separate?** Skeptic view: keep separate. SEO is silent (JSON-LD). UX is visible (footer strip). One frontend file, two outputs. Leader decides.

---

## Quality Check

- Patterns finalized: 5 (cap enforced)
- Auto-DROP rules applied: 3 (UX-4 ROI=low+brand=maybe, UX-6 brand=no, UX-10 ROI=low+brand=maybe)
- Auto-DEFER P3 applied: 3 (UX-2 per-aspect, UX-9 provider response, audio guide + private group sub-elements)
- User-deferred respected: 1 (DEFER-1 AI summary)
- Open questions → Verification Checklist: 4 (V1, V2, V3, V4)
- Tiebreak order applied: ROI high→low, brand-fit yes→maybe, effort trivial→large
- SEO cross-ref: 3 P1 fixes noted (SEO-2, SEO-3, SEO-5); SEO-9 merged with UX-5

---

## Related

- [[r1-ia]] — IA specialist
- [[r1-ux]] — UX specialist
- [[r1-seo]] — SEO specialist
- [[experience-detail-page-redesign]] — predecessor
