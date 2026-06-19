---
name: activities-pagination-ux-audit-2026-06-05
description: 3-specialist UX/UI + frontend audit on /activities listing pagination. Root cause: pageSize=16 mismatch with 3-col desktop grid leaves orphan card on last row + outer min-height creates dead space on short result lists. 5 findings: 2 P0, 1 P1, 2 P2. All P0+P1 SHIPPED in commits 3ce3c12 + 2226981.
metadata:
  type: project
  page: http://localhost:3000/activities
  issue: list number of product not proper for this screen size 1 pagination but there is 2 left space
  smartenplus_route: /activities
  date: 2026-06-05
---

# /activities Pagination UX Audit — 2026-06-05

## Summary

User flagged `/activities` listing: result count per page wrong for screen size — single page renders 1 card on last row with 2 empty grid cells (orphan card pattern). Root cause: `pageSize=16` (FilterDayTripsPage.js:53) mismatched with 3-col desktop grid → 16/3=5.33 rows → orphan. Secondary issue: outer wrapper `min-h-[calc(100vh-6rem)]` (line 116) creates vertical dead space on short result lists. 3-specialist review + skeptic + leader ranked 5 fixes: 2 P0, 1 P1, 2 P2.

## Decision (Adopted 2026-06-05)

**P0 + P1 SHIPPED.** Merged to develop at `2bfc2bd`.

| Commit | Change | LoC |
|--------|--------|-----|
| `3ce3c12` | (rating gate drop, sibling fix) | 1 |
| `2226981` | `pageSize: 16` → `12`, remove `min-h-[calc(100vh-6rem)]`, bump skeleton to 12 | 4 |

P2 (load-more, scroll persistence) deferred to next round.

## Context

**Why this audit:** pagination = conversion gate. Orphan card on last row = "no more results" signal even though user could paginate. Empty cells = "missing data" perception. Both erode trust.

**SmartEnPlus state (before fix):**
- Page: `pages/activities/index.js` → `FilterDayTripsPage` → `DayTripList` → `DayTripCard` grid
- `FilterDayTripsPage.js:53` — `pageSize: 16` (hardcoded, **FIXED to 12**)
- `DayTripList.js:91` — Grid `xs=12 sm=6 md=4 lg=4 xl=4` (1 / 2 / 3 / 3 / 3 cols)
- `DayTripList.js:42` — skeleton count `[...Array(6)]` (**FIXED to 12**)
- `FilterDayTripsPage.js:116` — outer 2-col grid `min-h-[calc(100vh-6rem)]` (**REMOVED**)
- `FilterDayTripsPage.js:139-156` — MUI `Pagination` shown only if `totalPages > 1`, centered, 44px tap target, brand-colored active page
- API: `store/api/dayTripsApi.js:54,72-73` — accepts arbitrary `page_size` param
- Backend: `smartenplus-backend/products/views.py:49-53` — `CustomPagination.page_size_query_param='page_size'`, `max_page_size=100`. **Frontend `pageSize: 12` works without backend change.**

## Math Breakdown (the bug)

| Screen | Cols | pageSize=16 | pageSize=12 | pageSize=18 |
|--------|------|-------------|-------------|-------------|
| Mobile xs | 1 | 16 rows | 12 rows | 18 rows |
| Tablet sm | 2 | 8 rows | 6 rows | 9 rows |
| Desktop md/lg/xl | 3 | **5.33 rows (orphan)** | 4 rows (clean) | 6 rows (clean) |

`pageSize=16` is the only value that doesn't divide cleanly into 3 (desktop) or 2 (tablet). `pageSize=12` divides cleanly into BOTH (12/3=4, 12/2=6, 12/1=12).

## GYG Reference (general)

- 4-5 columns on desktop, ~24 cards per page, "Load more" button (no numbered pagination)
- 6 columns on 2xl screens
- Cards slightly smaller (180-200px wide)
- No orphan pattern: load-more is append-only

## Specialist Findings

- `r1-ux.md` — UX/Conversion (5 patterns)
- `r1-visual.md` — Visual Design (3 patterns)
- `r1-performance.md` — Frontend Performance (3 patterns)

## Discussion: Debate

See `r2-skeptic.md` for auto-DROPs.

## Leader Synthesis

See `r3-leader-synthesis.md` for final 5 ranked.

## Key Files

### Vault files created
- `01-projects/activities-pagination-ux-audit-2026-06-05/r1-ux.md`
- `01-projects/activities-pagination-ux-audit-2026-06-05/r1-visual.md`
- `01-projects/activities-pagination-ux-audit-2026-06-05/r1-performance.md`
- `01-projects/activities-pagination-ux-audit-2026-06-05/r2-skeptic.md`
- `01-projects/activities-pagination-ux-audit-2026-06-05/r3-leader-synthesis.md`

### SmartEnPlus components modified
- `components/activities/browse/FilterDayTripsPage.js` (3 LoC)
- `components/activities/browse/DayTripList.js` (1 LoC)

### Backend verified
- `smartenplus-backend/products/views.py:49-53` — `CustomPagination` accepts `page_size` (max 100). PASS.

## Out of Scope

- Load-more button (P2 UX-3) — separate task
- CSS grid `auto-fill` responsive cards (P2 V-2) — separate task, card-width risk
- SSR/SSG first page (P2 P-2) — covered in 2026-06-04 plan
- Lazy-load images (P3 P-3) — separate task
- Destinations/Trips listings pagination audit — separate audit if needed

## Related

- [[gyg-page-analysis-2026-06-04-overview|gyg-page-analysis-2026-06-04]] — sibling: detail page audit
- [[gyg-card-rate-analysis-2026-06-05]] — sibling: card rate display audit (this session)
- [[trip-detail-uxui-audit-2026-05-22]] — prior detail page audit pattern (3-specialist)
- [[seo-homepage-specialist-team]] — SEO specialist team pattern

## Orphan Link-Backlog (Linked 2026-06-13)
- [[activities-sort-filter-ux]] — activities sort/filter UX pattern (sibling activity-search reference)
