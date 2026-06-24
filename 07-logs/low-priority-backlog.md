# Low-Priority Backlog

Moved from `master-state.md` Section 2 (2026-06-24 vault optimization). Deferred nits, needs-condition tasks, cosmetic debt. Not blocking. Audit trail — never delete.

## Frontend UI nits

| # | Issue | Status | Where |
|---|-------|--------|-------|
| HD-2 | CartButton dim (70%) | Low — acceptable | `CartButton.js:116` |
| HD-3 | xl padding gap | Low | `main-header.js:90` |
| HD-6 | Logo size jump | P2 | `main-header.js:66,95` |
| GAP-3 | Mobile position flip | P2 | `main-header.js:45-77` |
| GAP-5 | Nav hidden while searching | P2 — accepted | `main-header.js:112` |
| GAP-6 | threshold=0 abrupt snap | P3 | `useStickyVisibility.js:12` |
| GAP-7 | Wordmark hidden md-xl | P3 | `main-header.js:95` |
| F11-FOLLOWUP | B2B corporate CTA strip | DEFERRED — BD recommended. Awaits product decision on 280px slot | TBD |
| F11-FOLLOWUP | Shared `<Accordion>` / `<FAQAccordion>` atom | DEFERRED — UX flagged | `components/UI/` (new file) |
| AT-2 | Airport-transfer width mismatch | Inner margins | `StationInformation.js` etc. |
| IMG-ALT-DEBUG-1 | Next.js HMR cross-module callback staleness. Optional refactor: move mutation INTO dialog, drop parent `onSubmit` indirection. Atom [[nextjs-hmr-cross-module-callback-staleness]] | OPEN — low | `pages/routemanagement/operators/images/ImageEditDialog.js`, `index.js:140-178` |
| RR-1-FOLLOWUP | `submit-review/[...slug].js:77` brittle slug fallback. API returns `booking_item_slug` only — confirm contract | OPEN — low | `pages/rate-review/submit-review/[...slug].js:77` |
| 15 | `refetchOnMountOrArgChange` — needs justification | OPEN | `useTripData.js:16,24` |

## Backend / data / cleanup debt

| # | Issue | Status | Where |
|---|-------|--------|-------|
| CMA-1 | Contract Model Ambiguity — P1/P2 partial. Remaining: data inventory | OPEN | `operators/models.py` |
| Nav | NavigationSection empty — restart backend + populate | OPEN | `pages_info` |
| Explore | `location_type` CharField — needs `Location` model change | OPEN | `stations/models.py` |
| SILAPHAT-DESC | `Operator.description` holds route notes, not real about-copy — data quality | OPEN #127 — BD/copy task | `operators/models.py` |
| BOOKING-24H | `booking_count_yesterday` is rolling 24h not calendar yesterday (mislabeled) | OPEN #127 — rename or relabel | `products/serializers.py:353-363` |
| BE-GIT-DIVERGE | Prod backend git history diverged from origin (merge-noise) — pulls merge not FF | OPEN #127 — cosmetic | `smartenplus-backend` |
| 1 | AdminBookingSummaryViewSet auth — needs frontend sign-off | OPEN | `orders/views.py` |
| 2 | Delete RefundViewSet — waiting on zero `DEPRECATED_ENDPOINT_USED` | OPEN | `cards/views.py` |
| 3 | Remove Stripe 410 stub — waiting on zero prod traffic | OPEN | `payments/urls.py` |
| 8 | Forex endpoint naming — naming debt | OPEN | `cards/urls.py` |

## SEO / Admin

| # | Issue | Status | Where |
|---|-------|--------|-------|
| GSC-1 | GSC Crawled-Not-Indexed — Phase 1+2 shipped, monitoring. Phase 3 needs backend `route_exists` | OPEN | `seoConfig.js:41`, `server-sitemap.xml` |
| FAQ-1 | ExperienceFAQ — P0-P2 done. Admin `ageRestriction` deferred | OPEN | `admin-dashboard/DayTripDetails.js` |
| AT-1 | Airport Transfer redesign P0. Spec: [[transportation-category-audit]] | OPEN | `AirportTransferRouteCard.js` |
| SORT-VOCAB | Dual sort vocab: QuickSortPills PascalCase vs SortDropDown `-booked_count` — pick one, propagate | OPEN #127 | `components/UI/` |

## Related
- [[master-state]] — active items live here
- [[closed-items]] — resolved
