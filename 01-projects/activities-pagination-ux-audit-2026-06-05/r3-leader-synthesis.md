---
name: r3-leader-synthesis
description: R3 Leader. Adjudicate Skeptic. Final 5 P0/P1/P2 ranked. Implementation hints + LoC + shipped status.
metadata:
  type: synthesis
  role: leader
  page: gyg-card-conventions
  smartenplus_route: /activities
---

# R3 — Leader Synthesis (Pagination)

**Role:** adjudicate R1↔R2. Final 5 patterns with P0/P1/P2 ranking.

**Priority rubric:**
- **P0 = free-win tier:** trivial effort + brand-fit yes + visible-or-correctness signal
- **P1 = trust/scanability lift + brand-fit yes** (med-high ROI, small effort)
- **P2 = polish + small/medium effort + brand-fit yes/maybe** (low-med ROI, optional)

---

## Skeptic Verdict Adoption

| Skeptic Verdict | Leader Action | Reason |
|-----------------|---------------|--------|
| UX-1 KEEP P0 | Adopt P0 | Trivial + yes brand + high ROI. Math fix. |
| UX-2 KEEP P1 | Adopt P1 | Trivial + yes brand + med ROI. |
| UX-3 KEEP P2 | Adopt P2 | Medium effort, defer. |
| UX-4 AUTO-DROP | Adopt DROP | Backend field missing. |
| UX-5 KEEP P2 | Adopt P2 | sessionStorage risk; defer. |
| V-1 KEEP P0 | Adopt P0 | Trivial + yes brand + high ROI. Pairs with UX-1. |
| V-2 AUTO-DROP | Adopt DROP | Card-width risk. |
| V-3 AUTO-DROP | Adopt DROP | Cosmetic. |
| P-1 KEEP P0 | Adopt P0 | Same edit as V-1. |
| P-2 DEFER | Adopt P3 | Out of scope. |
| P-3 DEFER | Adopt P3 | Marginal gain. |

---

## Final 5 (ranked P0 → P2)

### Final 1 — P0: `pageSize: 16` → `12` (UX-1)

- **Priority:** P0
- **ROI:** high (kills orphan)
- **Brand-fit:** yes (clean grid)
- **Effort:** trivial
- **Implementation hint:** `FilterDayTripsPage.js:53` change `pageSize: 16` → `pageSize: 12`. Also update divisor on line 64.
- **Backend verify:** `CustomPagination.max_page_size >= 12` — **PASS** (max=100).
- **Estimated LoC:** 2
- **SHIPPED:** commit `2226981`

### Final 2 — P0: Remove `min-h-[calc(100vh-6rem)]` (V-1 + P-1)

- **Priority:** P0
- **ROI:** high (no dead space, CLS improvement)
- **Brand-fit:** yes (premium calm)
- **Effort:** trivial
- **Implementation hint:** `FilterDayTripsPage.js:116` remove `min-h-[calc(100vh-6rem)]` class.
- **Estimated LoC:** 1
- **SHIPPED:** commit `2226981`

### Final 3 — P1: Skeleton count 6 → 12 (UX-2)

- **Priority:** P1
- **ROI:** med (loading-state honesty)
- **Brand-fit:** yes
- **Effort:** trivial
- **Implementation hint:** `DayTripList.js:42` change `[...Array(6)]` → `[...Array(12)]`.
- **Estimated LoC:** 1
- **SHIPPED:** commit `2226981`

### Final 4 — P2: "Load more" button (UX-3)

- **Priority:** P2
- **ROI:** high (better perceived perf)
- **Brand-fit:** yes (modern OTA)
- **Effort:** medium
- **Implementation hint:** Append state pattern. Track `loadedPages[]` in Redux or component state. On button click, refetch next page and append. Use IntersectionObserver for autoload.
- **Caveat:** Requires API support (no cursor pagination yet — would need backend).
- **Estimated LoC:** 25-40
- **STATUS:** deferred

### Final 5 — P2: Persist scroll on page change (UX-5)

- **Priority:** P2
- **ROI:** med
- **Brand-fit:** yes
- **Effort:** small
- **Caveat:** sessionStorage quirk risk per CLAUDE.md "sessionStorage formData" gotcha. Use `useEffect` after page change, not in `useState` initializer.
- **Estimated LoC:** 8-12
- **STATUS:** deferred

---

## P3 Backend Debt (Out of scope, flagged for future)

- SSR/SSG first page — covered in [[../gyg-page-analysis-2026-06-04-overview|../gyg-page-analysis-2026-06-04]]
- Lazy-load images beyond first 6 — separate image-optimization task
- "N+ results available" microcopy — needs `Contract.has_next` backend field
- Cursor pagination for "Load more" — backend change required

---

## Out-of-Scope This Round

- Destinations/Trips listings pagination — separate audit if needed
- Per-page-size user preference (let user pick 12/24/48) — out of scope
- Infinite scroll — UX risk, deferred

---

## Implementation Order (Shipped 2026-06-05)

1. **P0 pageSize=12** — committed `2226981`
2. **P0 remove min-h** — committed `2226981` (same commit)
3. **P1 skeleton count** — committed `2226981` (same commit)
4. P2 load more — deferred
5. P2 scroll persistence — deferred

**Total shipped:** 4 LoC, 2 files, 1 commit. Merged to develop at `2bfc2bd`.

---

## Quality Check

- Patterns finalized: 5 (cap enforced)
- Priority assignment: 2 P0 + 1 P1 + 2 P2
- Backend verify: PASS (CustomPagination allows page_size)
- Skeptic auto-DROPs: 3 (UX-4, V-2, V-3)
- P3 backend debt: 1 (UX-4 has_next field)
- User-deferred: 0
- Implementation hints: 5
- LoC shipped: 4
- Sequencing: trivial-first followed by medium-effort deferred

## Related

- [[r1-ux]]
- [[r1-visual]]
- [[r1-performance]]
- [[r2-skeptic]]
- [[../gyg-page-analysis-2026-06-04-overview|../gyg-page-analysis-2026-06-04]] — sibling: detail page audit
- [[../gyg-card-rate-analysis-2026-06-05]] — sibling: card rate display audit (this session)
