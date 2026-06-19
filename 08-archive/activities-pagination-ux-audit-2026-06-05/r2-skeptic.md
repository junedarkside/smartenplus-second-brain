---
name: r2-skeptic
description: Skeptic — challenges R1 specialists. Auto-DROPs UX-4, V-2, V-3, P-3. Conditional KEEPs for backend verify.
metadata:
  type: specialist-r2
  role: skeptic
  page: gyg-card-conventions
  smartenplus_route: /activities
---

# R2 — Skeptic (Pagination)

**Goal:** challenge R1 UX/Visual/Performance findings. Drop low-ROI / off-brand / out-of-scope patterns.

**Skeptic rules:**
- auto-DROP if ROI=low + brand-fit=maybe
- auto-DROP if effort > small AND ROI not high
- CONDITIONAL KEEP if data dependency unverified

---

## Verdict

- **UX-1 (pageSize=12):** ROI=high, brand-fit=yes, effort=trivial. **KEEP P0.** Math fix. No data, no UX, no brand cost. Pure free win.
- **UX-2 (skeleton count 6→12):** ROI=med, brand-fit=yes, effort=trivial. **KEEP P1.** Honest loading state matches honest result state.
- **UX-3 (load more):** ROI=high, brand-fit=yes, effort=medium. **KEEP P2.** Big win but larger scope; defer to next iteration.
- **UX-4 ("N+ results" microcopy):** ROI=low, brand-fit=yes, effort=small. **AUTO-DROP.** Backend doesn't expose `has_next` cleanly; API returns `count` only. Frontend-only workaround = guess. Defer until backend field confirmed.
- **UX-5 (scroll persistence):** ROI=med, brand-fit=yes, effort=small. **KEEP P2.** Real UX win, but sessionStorage quirk risk (per CLAUDE.md "sessionStorage formData" gotcha). Defer.
- **V-1 (remove min-h):** ROI=high, brand-fit=yes, effort=trivial. **KEEP P0.** Pairs with UX-1. Without removing min-h, dead space still there.
- **V-2 (CSS grid auto-fill):** ROI=med, brand-fit=maybe, effort=medium. **AUTO-DROP.** Changes card width unpredictably — risk of regression. Defer.
- **V-3 (md=3 reflow):** ROI=low, brand-fit=yes, effort=trivial. **AUTO-DROP.** Cosmetic only. 16-card orphan is the real issue, not column count.
- **P-1 (remove min-h):** ROI=high, brand-fit=yes, effort=trivial. **KEEP P0.** Same edit as V-1.
- **P-2 (SSR/SSG):** ROI=med, brand-fit=yes, effort=large. **DEFER.** Out of scope; covered in 2026-06-04 plan.
- **P-3 (lazy-load images):** ROI=low, brand-fit=yes, effort=small. **DEFER.** Already lazy-loaded; marginal gain.

## Skeptic Open Questions (1)

1. **Backend `page_size=12`:** does API cap at max value? Verify `ContractListPagination.page_size_query_param` allows ≤12 default. If API has implicit min/max, this could break.

## Drop-to-P3 Rule

- **UX-1/V-1/P-1:** if backend caps `page_size < 12` → P3 (cannot ship without backend change)

## Adopted 2026-06-05 (this session)

All Skeptic KEEP verdicts adopted. UX-1 + V-1 + P-1 = P0 pair. UX-2 = P1. UX-3, UX-5 = P2 deferred.

## Related

- [[r1-ux]]
- [[r1-visual]]
- [[r1-performance]]
- [[r3-leader-synthesis]]
