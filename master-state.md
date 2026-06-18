# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-18 (session #132 END)

**Achieved this session (#132) — Checkout "Complete your trip" recommendation ENGINE built end-to-end: P0 regression fix, zone system, seed data, price bugs, card-count tuning. All on feature branches (committed, NOT pushed/merged).**

- **P0 hybrid regression FIXED** (`841e59f`): non-transport carts (spa/tour) got ZERO recs — backend `hybrid` ran only route-based finders (all `[]` with no `trip.route`). Fix: `hybrid`+no-route → `find_nearby_activities`. Test added. Found by /grill audit.
- **Seed-data root cause fixed:** 17 activity contracts shared a dummy NULL-station trip → cross-destination wrong recs (Chiang Mai tour → Phi Phi/Samui). Detached trips (local DB). Fixed `create_day_tours.py` + `create_all_service_tours.py` to stop attaching dummy trips. New idempotent `seed_demo_destination` command (anchor id 185 = Phuket demo, all zones).
- **Zone system shipped** (`feat/checkout-recommendation-zones`, BE+FE):
  - `find_transport_at_location` (ESSENTIAL, route-station→location bridge) + `CATEGORY_MATRIX` config + `find_nearby_activities` split into POPULAR (cross-category) / SIMILAR (same-category, cap 1).
  - Dropped `+30` same-category bonus (rewarded "more tours"). `booked_count` tiebreak. Per-zone caps `ZONE_LIMITS {essential:2, popular:3, similar:1}`.
  - FE: groups by `type`, renders conditional labeled zones (Getting there / Popular in <dest> / You might also like), reuses `RecommendationCard`.
- **Price bug:** `Min(selling_rate)` picked free INFANT 0.00 → "Price on request". Filtered `selling_rate__gt=0` across 7 finders.
- **Card-count review items shipped:** `recommendation_add_cart` GTM (BookingModal), mobile POPULAR cap 2 (`useMediaQuery`), POPULAR cap 4→3, fixed render-path `empty`-event bug (→useEffect).
- **4 vault review addenda** in [[recommendation-engine-completion-roadmap]]: strategy doc, card-count proposal, zones best-practice verdict, gap roadmap.
- UPGRADE zone deliberately NOT built (needs `upgrade_of` FK — no heuristic debt).

- **⚠️ NOT PUSHED:** BE+FE `feat/checkout-recommendation-zones` committed locally, sits on top of P0 branch `fix/recommendation-serializer-fields`. Nothing merged/deployed.

**Resume point (EXACT):**
1. **Push + PR chain (order matters):** `fix/recommendation-serializer-fields` (P0 + image/price/logo_url) → develop FIRST, then `feat/checkout-recommendation-zones` → develop (sits on top). Both BE+FE.
2. **Deploy BE** after merge → image/price/zone fixes reach prod. Then run `seed_demo_destination` / seed detach on prod if testing there.
3. **Highest-value next (from review):** add_cart/purchase analytics already partly done — finish `recommendation_purchase` + measure zone conversion before more zones.
4. **Deferred (documented):** UPGRADE zone (`upgrade_of` FK), EDITOR'S PICKS (needs curation flag + ops), mobile carousel, weekly trending counter.
5. **#129 ISR PROD ACTIVATION still pending** (BE develop→main + `FRONTEND_URL=www` + restart worker).

_(Session #131 block archived → `07-logs/session-history.md`.)_

---


**Carry-forward bugs (open, from #127):**
- **BE-IMAGE-DEDUP** tech debt (Section 2) — `process_operator_image` vs `process_review_image` dup + upload-validation copy-pasted ×5 files.
- silaphat `Operator.description` holds route notes, not real about-copy — data quality.
- `booking_count_yesterday` (`products/serializers.py:353-363`) — rolling 24h not calendar yesterday.
- Dual sort vocab: QuickSortPills PascalCase vs SortDropDown `-booked_count`.
- Prod backend git history diverged from origin (merge-noise) — pulls always merge, not FF. Cosmetic.

**Next session: starting state**
- vault: `master` @ new commit (this adds #132)
- BE: `feat/checkout-recommendation-zones` @ `90707a3` (clean, NOT pushed) — sits on top of `fix/recommendation-serializer-fields` (P0+serializer, pushed end #131).
- FE: `feat/checkout-recommendation-zones` @ `1c829f2` (clean, NOT pushed) — on top of `fix/people-also-book-title-image-price` (pushed end #131).
- FE `main` = `develop` @ `35c524d` — duration fix + ISR route, **SHIPPED TO PROD.**
- admin-dashboard: `main` @ `874d74d` (unchanged)
- content: `master` @ `3756e5b` (clean)
- ⚠️ Push order: serializer/title-image branches → develop FIRST, then zones branches (stacked on top).
- ⚠️ #129 ISR activation: BE-only remaining — deploy BE develop→main + set prod `FRONTEND_URL=www` + restart worker.

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **REC-CHECKOUT-ZONES** | Checkout "Complete your trip" recommendation engine: P0 hybrid regression fix + zone system (ESSENTIAL/POPULAR/SIMILAR) + matrix + transport finder + per-zone caps + price-bug fixes + card-count tuning + add_cart GTM + mobile cap. Built #132. **2 branches, committed NOT pushed:** BE+FE `feat/checkout-recommendation-zones` sits on top of BE `fix/recommendation-serializer-fields` (P0+image/price/logo_url). Tests pass (1 pre-existing unrelated fail). | OPEN #132 — push + PR chain (serializer branch FIRST, then zones) → develop → BE deploy. | `products/services.py`, `components/recommendations/*`, [[recommendation-engine-completion-roadmap]] |
| **REC-PRECOMPUTE-CACHEKEY** | Low. `products/tasks.py:67` precompute builds cache key `recommendations:{id}:{type}:{limit}` (4-part) but `get_recommendations:667` runtime key is 5-part (`:{rate_date or 'none'}`). Precompute writes never hit at runtime → wasted warm. Pre-existing, found in #132 verify. | OPEN #132 — out of scope of P0 fix. | `smartenplus-backend/products/tasks.py:67` |
| **ISR-REVALIDATE-GAP** | Admin contract edit not reaching prod `/activities/detail` (revalidate 3600) + `/trips/detail` (revalidate 300). Backend busts Redis correctly (`operators/signals.py:33`); Next.js Pages-Router ISR HTML never told to regen + no `/api/revalidate` route → stale, forever on cold pages (persistent `next_cache` volume). Fix (4 steps, build order in plan): (1) BE `daily_counter`→`.update(F+1)` enabler stops per-view post_save, (2) FE `pages/api/revalidate.js` POSTs `{slug}` owns path map, (3) BE `revalidate_frontend_isr` Celery task + `_trigger_revalidate` signal helper, (4) `REVALIDATION_SECRET` both repos incl GH Actions runtime path. Task no-ops on empty secret. | **IMPLEMENTED #129 → develop** (BE `4eaaf8d`, FE `66d896e`). All 4 steps done + verified (29 tests, manage.py check, ESLint, no-storm proof). **Prod root cause found:** `FRONTEND_URL` was apex → 301→www dropped the POST; fixed default→www (`d37dee3`). **FE SHIPPED #130** (main `35c524d` carries ISR route). **BE ACTIVATION PENDING:** deploy BE develop→main + set prod `FRONTEND_URL=www` + restart worker, then smoke-test (see Section 1 resume). | `operators/signals.py`, `operators/tasks.py`, `products/views.py:884`, `Smartenplus/settings.py:373`, FE `pages/api/revalidate.js`, `deploy-ghcr.sh` |
| **DURATION-DAYS-CARDS** | Day-tour browse cards omit duration: public LIST `ContractSerializer` doesn't expose `tour_duration_days`, so cards can't show "N Days" (detail page works, uses `__all__`). FE-only fix #130 chose omission over false "1 Day". Option B: add `tour_duration_days` to list serializer `fields`. One-line, low risk (read-only int); needs BE deploy + ISR cache clear. | OPEN #130 — optional follow-up, low priority. FE helper unchanged either way. | `smartenplus-backend/operators/serializers.py` (ContractSerializer), [[category-aware-duration-formatter]] |
| **BE-IMAGE-DEDUP** | BE image-processing duplication (moderate, pre-existing). Cluster 1: WebP resize/compress algorithm duplicated ~2-3× — `operators/utils.py:process_operator_image` (now parametrized #126b), `dialogue/utils.py:process_review_image` (120KB hardcoded), plus WebP/thumbnail code in `operators/admin.py`. Cluster 2: upload validation (ext whitelist + size) copy-pasted across 5 files (`stations/views.py`, `operators/utils.py`, `operators/views.py`, `pages_info/models.py`, `dialogue/utils.py`) each with own constants → drift risk. Consolidate → one `core/image_utils.py`: `process_image_to_webp(file, *, max_output_size, max_dimensions)` + `validate_upload(file, *, allowed_ext, max_size)`, migrate all callers. | OPEN #126 — dedicated refactor session. High blast radius (operators/dialogue/stations/pages_info), zero user value, all spots work. Do NOT bolt onto feature work. | `operators/utils.py`, `dialogue/utils.py` |
| **VAULT-DATE-RENAMES** | 105 files embed dates in filenames (violates "no dates in filenames" rule). Rename breaks every inbound wikilink. Needs separate planning round: `git mv` + atomic search-replace of all `[[old-name]]` → `[[new-name]]`. | OPEN #125 — next-wave vault work. | [[vault-optimization-snapshot-2026-06-16]] |
| **SEO-SITEMAP-FIX** | Implement fixes from whole-site SEO+sitemap audit | MERGED 2026-06-12. P0+P1+P2 `1f3f7a2` merged → develop `d88f50b`, pushed. Fake reviews ×4 deleted, sitemap 128→86 URLs, noindex fixed ×5 pages, dead JSON-LD pipeline removed. Build exit 0, greps clean. **Remaining:** deploy to prod, GSC Googlebot/WAF verify (manual), nginx 301s (infra), P3 dead-code sweep. Soft-404 stays with GSC-1. | develop `d88f50b`, [[seo-sitemap-whole-site-audit-2026-06-11]] |
| **CROSS-SELL-BD-INVENTORY** | BD creates Koh Lipe inventory to activate cross-sell | OPEN. BD task — no eng work. Needs: (1) return route Koh Lipe→Hat Yai Airport, (2) DAY_TOUR contracts at Koh Lipe, (3) SPA_WELLNESS contracts at Koh Lipe. Cross-sell auto-hides until `recommendation_count > 0`. **All 4 FE surfaces already live and verified 2026-06-13. GTM `item_category` + activity-detail accuracy ALSO already shipped (`hooks/useOmisePayment.js:59`+`:144`, `RelatedExperiences.js:7`) — were wrongly listed as open eng work.** Only BD inventory blocks value. Sole open eng item: multi-item post-booking (`bookingContext.js:33`, Sprint 2, not urgent). See [[cross-sell-integration-status-2026-06-13]]. | BD action |
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
