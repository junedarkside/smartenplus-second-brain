# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-11 (session #93)

**Achieved this session (#93):**
- **Two-pass verification of [[booking-payment-e2e-audit-2026-06-11]]** — audit-of-audit, all claims hand-checked against code:
  - Pass 1 (direct read): all 4 confirmed bugs + C1/C2 candidates + every backend claim exact. One omission fixed: 3 test files added to Bug 3 stable_id sweep (`useCheckoutAutoSave.test.js`, `savePassengerAssignmentsToCart.test.js`, `checkoutPersistence.test.js`).
  - Pass 2 (debug-mantra falsification): all root causes survived active disproof. Backend emits zero `stable_id` anywhere (double-confirms bugs 1/2); Effect 2 cannot rescue bug 1 (ref-equality early return `useCartSync.js:201-203`); `useCartSync.js:155` is sole `clearTripInfo` site (bug 2 has no alternate pruning path); C1 mount-state assumptions confirmed (`cartId: null` initial, `_persist.rehydrated` selector).
  - Doc amended with falsification notes — verified twice, safe to act on.
- **2 atoms extracted**: [[rtk-lazy-query-tuple-misuse]], [[redux-persist-gate-scope-gap]]

**Resume point (EXACT):**
1. **BOOKING-PAY-FIX-1** — implement bugs 1-4 from [[booking-payment-e2e-audit-2026-06-11]]: key cart sync by `item.id` (`useCartSync.js:41-42`, `147-177`), stable_id sweep (9 source + 3 test files, delete Effect 6), delete dead lazy query `BookButton.js:41-43`.
2. **BOOKING-PAY-REPRO-1** — runtime repro C1 (mixed cart → fill passengers → hard refresh `/checkout` → data gone?) and C2 (transient error nukes cartId in `check-and-createcart.js:67-72`).
3. **CROSS-SELL-MERGE** — PR `feat/redesign-people-also-book-cards` → `develop` pending. After merge: BD creates return route Koh Lipe→Hatyai Airport + DAY_TOUR/SPA contracts at Koh Lipe. Verify `checkout_recommendation_view` fires in GTM.

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **BOOKING-PAY-FIX-1** | Fix 4 verified bugs from booking-payment e2e audit | OPEN. Doc verified twice (#93). Bugs: (1) MEDIUM dead change-detection cart sync, (2) MEDIUM dead removed-item cleanup, (3) LOW stable_id remnants 9 source + 3 test files, (4) LOW dead lazy query in BookButton. | `hooks/checkout/useCartSync.js`, `components/UI/BookButton.js:41-43`, [[booking-payment-e2e-audit-2026-06-11]] |
| **BOOKING-PAY-REPRO-1** | Runtime repro C1 (formData lost on hard refresh) + C2 (transient error nukes cartId) | OPEN. Code-trace confirmed both; user ruling: repro before promotion. C1 repro: mixed cart → customize assignments → hard refresh `/checkout`. C2 fix if confirmed: clear only on `error.status === 404`. | `pages/checkout/index.js:107-201`, `components/HOC/check-and-createcart.js:67-72` |
| **CROSS-SELL-MERGE** | Merge `feat/redesign-people-also-book-cards` → `develop`; then BD creates inventory | OPEN. PR raised. After merge: BD creates (1) return route Koh Lipe→Hatyai Airport, (2) DAY_TOUR contracts at Koh Lipe, (3) SPA_WELLNESS contracts at Koh Lipe. Verify `checkout_recommendation_view` fires with `recommendation_count > 0`. | `feat/redesign-people-also-book-cards`, `checkout/index.js` |
| **BRANCH-CLEANUP-REMOTE** | 81 merged remote `origin/2606*` branches pending deletion | OPEN. Local cleanup (94) done in #84. Need: `git for-each-ref refs/remotes/origin/260 --format='%(refname:short)' \| sed 's\|^origin/\|\|' \| xargs -I {} git push origin --delete {}`. Verify `git branch -r \| wc -l` → 2. Run `git fetch --prune`. | `origin/2606*` (81 branches) |
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
