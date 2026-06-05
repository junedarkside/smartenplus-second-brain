---
name: r1-ux
description: Specialist A — UX/Conversion Designer. Score pagination patterns on ROI, brand-fit, effort. User complaint: orphan card + dead space.
metadata:
  type: specialist-r1
  role: ux-conversion-designer
  page: gyg-card-conventions
  smartenplus_route: /activities
---

# R1-UX — UX/Conversion Designer (Pagination)

**Goal:** identify pagination patterns addressing user complaint "1 pagination but there is 2 left space" — orphan card on last row + dead vertical space on short result lists.

**Scoring axes:**
- **ROI:** high (kills orphan / dead space) / med (loading-state honesty, scroll continuity) / low (clarity only)
- **Brand-fit:** yes (clean grid) / maybe (neutral)
- **Effort:** trivial (1 number change) / small (new prop) / medium (new component + state)

---

## Patterns (5 candidates)

| # | Pattern | ROI | Brand-fit | Effort |
|---|---------|-----|-----------|--------|
| UX-1 | `pageSize=12` (math fix: divides cleanly into 1/2/3 cols) | **high** (kills orphan) | yes (clean grid) | trivial (1 number) |
| UX-2 | Match skeleton count to pageSize (6 → 12) | med (loading-state honesty) | yes | trivial (1 number) |
| UX-3 | "Load more" button (GYG pattern) replace pagination | high (better perceived perf) | yes (modern OTA) | medium (append state) |
| UX-4 | Show "(N+ results available)" microcopy near pagination | low (clarity) | yes | small |
| UX-5 | Persist scroll position after page change | med (UX continuity) | yes | small (sessionStorage risk) |

## User Complaint Decoded

"1 pagination but there is 2 left space" = on 1-page result (e.g., 4-5 contracts total in DB), desktop shows 2 rows: row 1 full (3 cards), row 2 has 1-2 cards + 1-2 empty slots. Visually = "broken grid".

On paginated results with 16 per page = same orphan on last row (16/3=5.33).

## GYG Comparison (general)

- GYG: 4-5 cols on desktop, ~24 cards per page, "Load more" (no numbered pagination)
- 6 cols on 2xl screens
- Cards slightly smaller (180-200px wide)
- No orphan: load-more append-only

## Reuse Notes

- `Pagination` from `@mui/material` — already used (line 141 in FilterDayTripsPage)
- `Grid` from `@mui/material` — already used
- `useGetContractsQuery` from `store/api/dayTripsApi.js` — already supports any pageSize
- `COLORS` from `helpers/designSystem.js` — already imported

## Related

- [[r1-visual]]
- [[r1-performance]]
- [[r2-skeptic]]
- [[r3-leader-synthesis]]
