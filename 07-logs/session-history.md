# Session History

Archived from master-state.md. Latest session stays in master-state.md Section 1.

---

## Session #261 — 2026-07-22
SEAT-CHECK Part B SHIPPED → main — `operator_station_id` in Station Mapping dialog is now a Supabase `RouteID` autocomplete (unblocks #260's deferred item; **no BE proxy needed**). PostgREST leaks the exposed-schema list in the error `hint` on any invalid `Accept-Profile` → hook probes `schema('__probe__')`, parses hint, matches operator schema by name-prefix (longest, denylisted non-operator schemas), confirms via `Operator` col. `Lomprayah`→`lompraya` (lowercased 8-char truncation, not derivable); `RouteID` cols `Route`/`ID`/`Operator`, 39 rows. Label `"Route (ID)"`, saves `ID`; `freeSolo` preserves stale ids; no schema → free-text fallback. New `helpers/operatorRouteIds.js` (pure) + `hooks/useOperatorRouteIds.js` (module-cached discovery). Grid sorts by id asc. AD+BE deployed → main (AD `8780af4`, BE `5baebe8`). Prod remaining: `migrate operators` 0069+0070; recreate "lomprayah" op+mappings as real data. 2 atoms extracted. → [[postgrest-exposed-schema-hint-discovery]] · [[supabase-per-operator-schema-routeid]] · [[station-mapping-multi-operator-design]]

---

## Session #260 — 2026-07-22
SEAT-CHECK-RESELLER — `Contract.seat_check_operator` FK lets a reseller contract check seat availability against a source operator (Silaphat resells "lomprayah"). Resolution `operator = contract.seat_check_operator or contract.operator` covers mapping lookups + api_url. BE migration `0069`, AD form Autocomplete + transform. STATION-MAPPING-SEAT-API-VISIBILITY: page shows operator/API per mapping (chip + `Seat API` grid col via `operator_has_api` serializer field + `?our_station=` filter). DROP-CONTRACT-SEAT-API-URL: removed redundant `Contract.seat_availability_api_url` (1/81 usage, migration `0070`) + URL `.strip()` fix. All merged → develop + pushed (BE `5baebe8`, AD `3fc14e0`). Part B (Supabase id autocomplete) deferred — assumed `RouteID` anon-unreadable, needs BE proxy. → [[seat-availability-reseller-operator-gap]] [[station-mapping-multi-operator-design]]

---

## Session #259 — 2026-07-22
FAQ CSS FIX — Trip detail page FAQ section alignment + spacing fixed. Removed conflicting `mx-auto mx-2` → `mx-auto px-2 md:px-3 xl:px-0`. Fixed padding conflict (`p-4` outer → inner `<div className="p-4 md:p-5">`). Tightened heading `mb-3→mb-2`, item padding `py-2→py-3`, `rounded-md md:rounded-lg` → `rounded-md`. Committed `1e6eaec0` on `fix/faq-spacing-alignment` → merged develop → pushed `4758b4b1`.

## Session #258 — 2026-07-21
TRIPS QA + PROD DEPLOY + CHAT-IMAGE-SEND + SEAT-AVAILABILITY MIGRATE — Trips redesign QA passed, prod deployed (ISR cache flushed). CHAT-IMAGE-SEND prod deploy: Supabase SQL 003, Pillow bump, BE→AD→FE deployed, smoke passed. manage.py migrate 0066/0067/0068 on prod.

---

## Session #257 — 2026-07-21
SEAT-AVAILABILITY commit+push — Committed BE (`c535dd3`: 4 files + migrations 0066-0068) + AD (`b1996c7`: 4 files) to develop. Then completed: Trips Redesign QA, CHAT-IMAGE-SEND prod deploy, `manage.py migrate` 0066-0068 on prod.

---

## Session #256 — 2026-07-21
SEAT-AVAILABILITY-CHECKER-REBUILD — BE station-mapping feature was never committed (migration existed, model/views/serializer lost). Rebuilt from scratch: `OperatorStationMapping` model + CRUD viewset + `check-seat-availability` @action on `ContractDetailViewSet`. Wired n8n webhook (`https://n8n.smartenplus.co.th/webhook/search`). Added `seat_availability_api_url` field to Operator + Contract models (migrations 0067+0068) with priority chain: contract > operator. Fixed `seatStatus` parsing bug (`== 'Available'` exact match → `!= 'Sold Out'` logic). Added API URL fields in AD: OperatorForm + ContractFormFields + useContractFormData + contractUtils. All uncommitted (BE 4 files + 3 migrations; AD 4 files).

---

## Session #255 — 2026-07-20
STATION-MAPPING + SUPABASE-ERROR-LOGGING — Diagnosed Supabase 406 (transient outage, not code bug). Added HTTPError body logging to `_fetch_schema`. Committed + merged BE fix (`fix/cs-supabase-error-logging` → develop). Committed + merged AD station-mapping feature (`feat/station-mapping` → develop): SeatAvailabilityChecker, station-mapping page, nav entry, CRUD API endpoints.

---

## Session #254 — 2026-07-20
BRANCH-CLEANUP + CHAT-DESIGN-TOKENS — Pruned 45 merged branches across all 3 repos. Fixed ScrollTop overlap. Added CHAT design tokens. Refactored ChatBubble + ChatPanel to use tokens. Commit `4957f22b` → develop.

---

## Session #253 — 2026-07-19
TRIPS-PAGE-REDESIGN — `/trips` index redesigned via 3-agent team (UX auditor → designer → frontend implementer). `pages/trips/index.js` rewritten 733→162 lines: `getStaticProps` + ISR revalidate:3600, `PageSeo`, reuses `components/locations/{SearchBar,FilterControls,StatsDisplay,EmptyState}` unchanged. New: `components/trips/RouteCard.js` (image-forward, `TouristTrip` schema, gradient overlay, `departure → arrival` text), `hooks/useTripsFiltering.js` (memoised search+sort on joined route string), `hooks/useTripsStructuredData.js` (`ItemList` of `TouristTrip` + `BreadcrumbList` + `CollectionPage` with `speakable`). First page in codebase with `hreflang="en"` + `hreflang="x-default"`. Projected SEO 8.5 / AEO 8.5 / GEO 7.0. **Status: COMMITTED `db5982be`, not yet pushed.** Branch `feat/trips-page-redesign`.

---

## Session #252 — 2026-07-18
LOCATIONS-PAGE-REDESIGN — visual redesign of `/locations` index page on branch `feat/locations-page-redesign`. Mirror of destinations redesign: image-forward `LocationCard`, hero with H1 "Where in Thailand Do You Want to Travel?", back+share overlay (`top-2 z-40 pointer-events-none/auto`), `SearchBar` + `FilterControls` + `StatsDisplay` extracted into `components/locations/`. Two new hooks: `useLocationsFiltering(allLocations, searchTerm, sortOption)` (memoised filter+sort) and `useLocationsStructuredData(allLocations, domainURL, lastReviewedTimestamp)` (returns `seo`, `itemListElements` for `ItemList` JSON-LD `TouristDestination`, `breadcrumbItems`, `organizationSchema`, `CollectionPage` schema with `lastReviewed`). `pages/locations/index.js` reduced to composition. Status at session end: UNCOMMITTED on `feat/locations-page-redesign` (`354889f1`); later merged → develop `a25ff23d`. Workspace: backend `main` `06423c5` · admin `main` `21d03eb` · content `master` `3756e5b` — clean. Resume was: commit + push + verify locations JSON-LD/OG + mobile QA 375/768/1280 + parity vs destinations redesign.

---

## Session #251 — 2026-07-18
DESTINATIONS-PAGE-REDESIGN — full visual redesign of `/destinations` index shipped → develop. 3-agent team (design-review auditor → designer w/ 12Go/Booking/GYG/Klook research → react-specialist impl). Image-forward overlay cards (`location.image || DEFAULT_ROUTE_IMAGE`), go-TO intent H1 "Where in Thailand Do You Want to Go?", full a11y pass. 2-agent mobile debate (verdict YES-WITH-FIXES) → sticky FilterControls (`top-0 md:top-20`), mobile SearchBar moved hero→sticky bar, responsive MUI select widths, Book CTA pinned card-bottom (`mt-auto`). 4 commits → merge `354889f1` → develop (pushed): `943deb7d` redesign · `6d89c875` CTA pin · `24c92257` mobile sticky · `1e4f2f46` hero pill buttons 36→44px sitewide (16 non-destinations files). 22 files total. Lint clean. Build skipped (trivial touch-target change). Full design+debate record: `01-projects/destinations-page-redesign.md`. Workspace: frontend `develop` `354889f1` clean; `feat/destinations-page-redesign` kept on remote. Resume: (1) destinations live test (grid/card interactions, search/filter/expand/CTA) — local dev backend returned 0 locations; (2) carry-forward prod-deploy queue: TRIP-CARD-V2 (ISR cache flush + ENV.md row), REC-PRICE-FIX (Redis `recommendations:*` flush + `manage.py migrate` operators/0064), CHAT-IMAGE-SEND (Supabase SQL 003 + Pillow bump + deploy BE→AD→FE + smoke).

---

## Session #250 — 2026-07-15
TRIP-CARD-V2 — built flight-OTA style card from scratch (`TripCardV2.js` + `TripItemLayoutV2.js`). Env flag `NEXT_PUBLIC_TRIP_CARD_V2` (unset=V2, `false`=V1 rollback). 2-agent UX/Design audit → scorecard V2 7/7 vs V1 4.5/5. P1 batch: stops text under arrow, JOIN chip, amenity icons, station `line-clamp-2`, `max-w-[560px]`, 44px chevron. `SkeletonSection` rewritten to V2 anatomy; `TripSearchResults` inline skeleton replaced. Mobile compact legs breakpoint-split (`hidden sm:flex` full / `flex sm:hidden` compact). 8 commits → develop, pushed `f70dbe5d`. `NEXT_PUBLIC_TRIP_CARD_V2` row still needs adding to ENV.md (docs/ permission denied this session). VAULT AUDIT — `01-projects/trip-card-v2-flight-style-audit.md` created; `index.md` + `log.md` updated. Workspace: frontend `main` `f70dbe5d` · backend `main` `06423c5` · admin `main` `21d03eb` · content `master` `3756e5b` — all clean. Resume: (1) TRIP-CARD-V2 prod deploy — ISR cache clear (`smartenplus_next_cache` Docker volume) + add `NEXT_PUBLIC_TRIP_CARD_V2` to ENV.md; (2) REC-PRICE-FIX prod — BE main has `06423c5`, deploy + MANDATORY Redis flush `redis-cli --scan --pattern "recommendations:*" | xargs redis-cli del` + `manage.py migrate` (operators/0064); (3) CHAT-IMAGE-SEND prod — Supabase SQL 003 + `pip install -r requirements.txt` (Pillow bump) + deploy BE→AD→FE + smoke.

---

## Session #249 — 2026-07-15
BE-HOMEPAGE-PRICE FIXED — all 8 `Min(selling_rate)` finder annotations in `products/services.py` now filter `contract_ratecard__is_active=True` (inactive ratecards could win Min → unbookable "From" prices on rec cards). Branch `fix/rec-price-active-filter` → develop `06423c5`, pushed to origin. 4-agent audit (BD/UX/BE/FE) confirmed fix complete; other price paths already `is_active`-filtered. DEPLOY GOTCHA: Redis `recommendations:*` flush mandatory post-deploy (skip-if-fresh guard `tasks.py:66-75` serves stale prices up to 24h). REC-SLOT-WASTE closed DO-NOTHING per 4-agent audit — near-zero incidence, `checkout_recommendation_empty` GTM monitors it. Vault: `01-projects/rec-engine-report-audit.md` created, atom extracted `[[precompute-cache-stale-after-logic-fix]]`. Vault commit `eea2c7f` pushed.

---

## Session #248 — 2026-07-15
REC ENGINE — 5 phases shipped across FE + BE, all → develop. Phase 1 (`fix/rec-quick-wins`): 2s timeout on recommendationsApi · `recommendation_modal_open` GTM · `chidren` typo fix · sessionStorage Safari guard. Phase 2 (`feat/rec-purchase-event`): purchase attribution — `markRecSourcedContract` + `fireRecommendationPurchaseEvents` in `helpers/gtmUtils.js`; wired in `RecommendationBookingModal.js` + `hooks/useOmisePayment.js`. Funnel complete: view→click→modal→add_cart→purchase. Phase 3 (`fix/rec-checkout-filter`): `filterValidRecommendations` applied at checkout rec list. Phase 4 (`chore/rec-remove-ratecard-hook`): deleted `hooks/useRecommendationRatecards.js` (−138 lines). Phase 5 (`feat/rec-never-empty-fallback`): `find_global_fallback()` in `products/services.py`; hybrid dedupe; `booked_count` default 10→0; migration `operators/0064` applied locally. 28/29 BE tests pass (1 pre-existing failure `test_find_similar_contracts`). FE develop: `9fd5b0a5` · BE develop: `f0aea8c`.

---
