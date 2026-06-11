# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-11 (session #96)

**Achieved this session (#96):**
- **Activity cross-sell 3-layer bug fixed** (debug-mantra + DB mockup):
  - Layer 1: `views.py:1755` — `'activity'` added to `valid_types` → unblocked 400
  - Layer 2: `services.py` — global trip guard removed (ValueError blocked all tripless contracts)
  - Layer 3: `services.py` — dispatch condition tightened to require `arrival_station` (contracts have `trip+route` but `arrival_station=None`); `find_nearby_activities()` added for activity→activity via `primary_location`/`service_areas`. Scoring: location base 50 + same category +30 + quality 0–20 + exact location +10.
  - Verified: `GET /api/v1/recommendations/118/?type=activity&limit=3` → 200, contract 123 score 90.0.
- **Cache WARNING silenced**: `clear_trip_cache` early-return for non-transport `service_category`. `logger.warning` → `logger.debug` for incomplete transport data.
- **Booking widget blank error fixed**: `advanceHourPassed` + `nonOperatingDay` added to Alert. `ADVANCE_HOUR_PASSED` constant added to `dayTripConstants.js`. Root cause: 2-day advance window passed for 06/13 on contract 123 — blocked correctly but no message shown.
- **2 atoms extracted**: [[activity-to-activity-cross-sell]], [[booking-widget-availability-error-display]]. [[recommendation-type-selection-by-service-category]] updated (was stale — said activity→activity unsupported).

**Resume point (EXACT):**
1. **COMMIT-PUSH** — both repos uncommitted: `smartenplus-backend` (products/services.py + products/views.py), `smartenplus-frontend` (DayTripBookingWidget.js + dayTripConstants.js). Commit + push + merge → develop.
2. **FRONTEND-AUDIT-MANUAL-PRS** — open 3 PRs on GitHub manually: fix/audit-checkout-passengers-hooks, fix/audit-rtk-query-cleanup, chore/audit-deadcode-and-hygiene. All merged locally; PR open for audit record.
3. **FRONTEND-AUDIT-FOLLOWUP-1** — 2 `exhaustive-deps` warnings in `FormikValuesSync.js:61:6`. Low priority.
4. **BOOKING-PAY-REPRO-1** — runtime repro C1 + C2. Unchanged.
5. **CROSS-SELL-MERGE** — PR `feat/redesign-people-also-book-cards` → `develop` pending. Unchanged.
6. **BRANCH-CLEANUP-REMOTE** — 81 merged remote `origin/2606*` branches pending deletion. Unchanged.

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **BOOKING-PAY-FIX-1** | Fix 4 verified bugs from booking-payment e2e audit | CLOSED #94. Merged `fix/checkout-stable-id-cleanup` → `develop` (`f271aef`). 53/53 tests, SM-1–SM-4 passed. | `hooks/checkout/useCartSync.js`, `components/UI/BookButton.js:41-43` |
| **BOOKING-PAY-REPRO-1** | Runtime repro C1 (formData lost on hard refresh) + C2 (transient error nukes cartId) | OPEN. Code-trace confirmed both; user ruling: repro before promotion. C1 repro: mixed cart → customize assignments → hard refresh `/checkout`. C2 fix if confirmed: clear only on `error.status === 404`. | `pages/checkout/index.js:107-201`, `components/HOC/check-and-createcart.js:67-72` |
| **CROSS-SELL-MERGE** | Merge `feat/redesign-people-also-book-cards` → `develop`; then BD creates inventory | OPEN. PR raised. After merge: BD creates (1) return route Koh Lipe→Hatyai Airport, (2) DAY_TOUR contracts at Koh Lipe, (3) SPA_WELLNESS contracts at Koh Lipe. Verify `checkout_recommendation_view` fires with `recommendation_count > 0`. | `feat/redesign-people-also-book-cards`, `checkout/index.js` |
| **BRANCH-CLEANUP-REMOTE** | 81 merged remote `origin/2606*` branches pending deletion | OPEN. Local cleanup (94) done in #84. Need: `git for-each-ref refs/remotes/origin/260 --format='%(refname:short)' \| sed 's\|^origin/\|\|' \| xargs -I {} git push origin --delete {}`. Verify `git branch -r \| wc -l` → 2. Run `git fetch --prune`. | `origin/2606*` (81 branches) |
| **FRONTEND-AUDIT-FIX-1** | Audit finding 3 (Formik render-prop useEffect) | CLOSED #95. PR1 `fix/audit-checkout-passengers-hooks` (e5261ab → 1e46314). New `FormikValuesSync.js` (105 lines) absorbs both effects via useFormikContext. Rules-of-hooks invariant restored. Lint clean. | `components/forms/checkout/FormikValuesSync.js`, `Passengers.js` |
| **FRONTEND-AUDIT-FIX-2** | Audit findings 1+2+4+5 (RTK Query) | CLOSED #95. PR2 `fix/audit-rtk-query-cleanup` (ecc76a9 → b6b956e). getSession pattern, activities key, cart-version extract, createCart single invalidation. New `store/cart-version.js` (12 lines). 3 sources of truth → 1. Lint clean. | `store/cart-version.js`, `store/cart-slice.js`, `store/api/*`, `store/index.js` |
| **FRONTEND-AUDIT-FIX-3** | Audit findings 6+7+8+9 (dead code + hygiene) | CLOSED #95. PR3 `chore/audit-deadcode-and-hygiene` (d69b473 → fbe9aab). 31 files, 4237 deletions, 7 insertions. Rebased onto develop post-PR1+PR2. | 5 dead-code paths, 5 .backup, 2 logs, db/ data/ *.diff *.sh, 4 archive, .gitignore |
| **FRONTEND-AUDIT-FOLLOWUP-1** | 2 exhaustive-deps warnings in FormikValuesSync.js:61:6 | OPEN. Pre-existing condition now visible (was masked by old eslint-disable that design removed). Fix: add explicit deps + suppression comment, or accept. Low priority. | `FormikValuesSync.js:61:6` |
| **FRONTEND-AUDIT-MANUAL-PRS** | Open 3 PRs on GitHub manually | OPEN. No `gh` CLI in environment. All 3 branches already merged to develop; opening PRs is for audit record. URLs in [[frontend-audit-implementation-2026-06-11]]. | 3 remote branches |
| **IMG-ALT-DEBUG-1** | Next.js HMR cross-module callback staleness | OPEN. Optional refactor: move mutation call INTO dialog component, drop parent `onSubmit` indirection. Atom: [[nextjs-hmr-cross-module-callback-staleness]]. Low priority. | `pages/routemanagement/operators/images/ImageEditDialog.js`, `index.js:140-178` |
| F11-FOLLOWUP | B2B corporate CTA strip | DEFERRED. BD recommended. Awaits product decision on 280px slot. | TBD |
| F11-FOLLOWUP | Shared `<Accordion>` / `<FAQAccordion>` atom | DEFERRED. UX flagged. | `components/UI/` (new file) |
| RR-1-FOLLOWUP | `submit-review/[...slug].js:77` brittle slug fallback | API returns `booking_item_slug` only. Confirm contract. Low priority. | `pages/rate-review/submit-review/[...slug].js:77` |
| GSC-1 | GSC Crawled-Not-Indexed | Phase 1+2 shipped, monitoring. Phase 3 needs backend `route_exists`. | `seoConfig.js:41`, `server-sitemap.xml` |
| CMA-1 | Contract Model Ambiguity | P1/P2 partial. Remaining: data inventory. | `operators/models.py` |
| FAQ-1 | ExperienceFAQ | P0-P2 done. Admin `ageRestriction` deferred. | `admin-dashboard/DayTripDetails.js` |
| AT-1 | Airport Transfer redesign | P0. Spec: `03-knowledge/transportation-category-audit`. | `AirportTransferRouteCard.js` |
| AT-2 | Airport-transfer width mismatch | Inner margins. | `StationInformation.js` etc. |
| 15 | refetchOnMountOrArgChange | Needs justification. | `useTripData.js:16,24` |
| 1 | AdminBookingSummaryViewSet auth | Needs frontend sign-off. | `orders/views.py` |
| 2 | Delete RefundViewSet | Waiting on zero DEPRECATED_ENDPOINT_USED. | `cards/views.py` |
| 3 | Remove Stripe 410 stub | Waiting on zero prod traffic. | `payments/urls.py` |
| 8 | Forex endpoint naming | Naming debt. | `cards/urls.py` |
| Nav | NavigationSection empty | Restart backend + populate. | `pages_info` |
| Explore | location_type CharField | Needs `Location` model change. | `stations/models.py` |
| HD-2 | CartButton dim (70%) | Low — acceptable. | `CartButton.js:116` |
| HD-3 | xl padding gap | Low. | `main-header.js:90` |
| HD-6 | Logo size jump | P2. | `main-header.js:66,95` |
| GAP-3 | Mobile position flip | P2. | `main-header.js:45-77` |
| GAP-5 | Nav hidden while searching | P2 — accepted. | `main-header.js:112` |
| GAP-6 | threshold=0 abrupt snap | P3. | `useStickyVisibility.js:12` |
| GAP-7 | Wordmark hidden md-xl | P3. | `main-header.js:95` |

---

**See also:** [[vault-protocol]] (API contract) · [[vault-guardrails]] (architecture) · [[session-history]] (#38+) · [[closed-items]] (resolved)
