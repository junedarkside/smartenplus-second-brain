# Session History

Archived from master-state.md. Latest session stays in master-state.md Section 1.

---

## Session #137 — 2026-06-19 (END)

**Achieved (#137) — Vault optimization pass (4 phases). No code/deploy — vault-only.**

- **Phase 0 (safety net)**: committed 3 loose #136 carry-forward session-end files (master-state, 07-logs/log, session-history). `77e47e5`.
- **Phase 1 (health pass)**: archived 8 audit bundles (47 files) + 15 verified-complete projects + 5 overviews → `08-archive/`. `01-projects/` 91→70 md, flat restored (0 subfolders), 0 broken wikilinks. Held active/ambiguous: not-suitable-for-section, frontend-audit-implementation, profile-dropdown-redesign. `9a3eded`.
- **Phase 2 (atomize)**: vault already well-atomized; 1 superseded archived (payment-manual-test-skip). Aggressive atomize skipped per user (15 >200L justified specs/ADRs/active-work). `a531694`.
- **Phase 3 (#125 CLOSED)**: stripped `-YYYY-MM-DD` from 62 active filenames (61 renamed + 1 archived); ~795 wikilinks rewritten via sed across index/log/master-state + ~140 notes; 2 collision pairs resolved semantically; 0 dated filenames outside archive, 0 broken links. `d235870`.
- 4 commits pushed vault master. All repos clean (BE/FE/admin main, content master).

**Carry-forward (NOT done #137):** deploy FE+BE develop→main (REC engine + ISR + from-price fix), #129 ISR prod activation, REC-engine min-price bug (same class), vault hygiene.

## Session #136 — 2026-06-19 (END)

**Achieved (#136) — BE homepage "From" price type-filter fix + branch hygiene. No deploy.**

- **BE-HOMEPAGE-PRICE fix (experiences + airport routes)**: homepage "From" prices computed BE-side, shipped pre-baked via `/api/pages-info/front-page/`. Two paths picked lowest `selling_rate` across ALL ratecard types → cheapest CHILD/INFANT surfaced as "From":
  - `PopularExperienceSerializer.get_min_price()` (`products/serializers.py:755`) — now filters ADULT (per-person), falls back to any type if no ADULT rate; added `selling_rate__gt=0`.
  - `_fetch_airport_routes_data` `lowest_price` (`pages_info/views.py:355`) — was unfiltered; now type-aware (JOIN→ADULT, PRIVATE/CHARTER→VEHICLE) + sentinel strip.
- **Shared helper extracted**: `route_lowest_price_annotation(today)` + `ROUTE_PRICE_SENTINEL` in `products/services.py`. HomeViewSet + airport-routes share one source (dedup). Dropped orphan imports from `products/views.py`.
- **Tests**: `PopularExperienceMinPriceTestCase` (3) pass. `manage.py check` clean. Suite 29 tests, 2 pre-existing Redis-dependent fails.
- Merged BE develop (`cff26b3`, no-ff), branch pruned.
- FE branch hygiene: pruned 7 merged `fix/activities-*` branches.

**Carry-forward (NOT done in #136):** deploy FE+BE develop→main (REC engine + ISR + from-price fix), #129 ISR prod activation, REC-engine min-price bug (same class), vault hygiene.

_(BE develop `cff26b3`, FE develop `143f9a2`, FE main `143f9a2`, BE main `bb5c199`.)_

---

## Session #135 — 2026-06-19

**Achieved — Activity detail + browse page bug fixes. No deploy. FE-only.**

- **P3 design tokens** (4 components): BookedCounter, IncludedExcluded, MeetingPointCard migrated Tailwind color classes → COLORS token inline styles. DayTripHero same fix but file is dead code (not imported anywhere).
- **AirbnbPhotoGrid image ordering**: `buildImageList()` now trusts backend `contract.image[]` array (already sorted by admin `order` field). `featured_image` is fallback only when gallery empty. `totalCount` fixed to not double-count.
- **Double "From" label**: `DayTripMobileBookingBar` + `PremiumBookingPanel` were prepending own "From" before `PricingDisplay size="compact"` (which renders its own). Removed caller-side duplicates.
- **PricingDisplay `align` prop**: added `align='end'` default (zero callers break). Mobile bar + premium panel pass `align="start"`.
- **`getFromPrice` type-aware**: filters ratecards JOIN→ADULT / other→VEHICLE (fallback: all). Matches `findLowestSellingRate()`.
- **DayTripCard**: replaced inline Math.min block with `getFromPrice(workingContract) ?? 0`.

_(FE develop `143f9a2`, FE main `4c9354b`, BE main `bb5c199`.)_

---

## Session #133 — 2026-06-18

**Achieved — Recommendation zones MERGED to develop (both repos) + 2 product-review fixes + branches pruned. The whole #132 engine arc is now on `develop`, ready to deploy.**

- **Anchor priority FLIPPED (experience-first)** — `ANCHOR_PRIORITY` now DAY_TOUR/activities 100 down to TRANSPORTATION 30 / TRANSFER 20 (was transport-first). Tour anchors → rich cross-sell; transport only anchors a transport-only cart. Retires the obsolete [[recommendation-anchor-first-transport-rule]]. From multi-cart review.
- **Removed `minCartPrice` floor** — it hid recs cheaper than the cheapest cart item, suppressing cheap complementary add-ons (THB 300 ferry). Now only cart-item exclusion. From multi-cart review.
- **recType-follows-anchor fix** (debug-mantra + /grill) — mixed cart (tour+ferry) showed NO recs: anchor was the tour but `recType` still keyed off "any transport in cart" → picked `packages` → needs anchor route → tour has none → empty. Fixed `recType = anchorIsTransport ? 'packages' : 'hybrid'`. Verified tour anchor → 6 recs.
- **MERGED to develop** (no-ff, both repos): BE `ae31f1f`, FE `0877d23`. Brought the full #132 stack (P0 hybrid fix, serializer image/price/logo_url, zones, matrix, seed command, price-bug, card-count tuning). Pre-merge: 15 BE tests (1 pre-existing unrelated fail), `check` clean, FE ESLint 0 errors.
- **Pruned 4 merged branches** (local+remote): BE `feat/checkout-recommendation-zones` + `fix/recommendation-serializer-fields`; FE `feat/checkout-recommendation-zones` + `fix/people-also-book-title-image-price`.
- **3 more vault review addenda** in [[recommendation-engine-completion-roadmap]]: zones best-practice verdict, card-count proposal, multi-cart strategy.

---

## Session #132 (2026-06-18) — Checkout recommendation ENGINE built (committed, branches)

P0 hybrid regression fixed (`841e59f`: non-transport → 0 recs; fallthrough to find_nearby_activities). Seed root cause fixed (17 activities shared dummy trip → cross-destination wrong recs; detached + fixed create_day_tours/create_all_service_tours + new idempotent seed_demo_destination, Phuket anchor 185). Zone system shipped (`feat/checkout-recommendation-zones`): find_transport_at_location (ESSENTIAL via route-station→location bridge) + CATEGORY_MATRIX + find_nearby_activities split POPULAR/SIMILAR; dropped +30 same-cat bonus; ZONE_LIMITS {2/3/1}; FE conditional labeled zones. Price bug: Min(selling_rate) picked free INFANT 0.00 → filtered >0 ×7 finders. Card-count items: add_cart GTM, mobile cap, POPULAR 4→3, render-path empty bug→useEffect. 4 vault review addenda. UPGRADE deferred (needs upgrade_of FK). End #132: branches committed NOT pushed.

---

## Session #131 (2026-06-18) — "People also book" 3 bugs + spec analysis

- 3 prod bugs fixed: title `"to"` (null-route truthy guard), image (BE serializer missing `image` field → `get_image()` reusing `ImageGallerySerializer`), price ("Price on request" — `_lowest_price=0.0`→`None`). + `OperatorSerializer.logo_url`, broken-image `onError`→`CATEGORY_CONFIG` icon fallback.
- Anchor: `SKIP_CATS`→`ANCHOR_PRIORITY` (all 9 cats scored). `recType` `'activity'`→`'hybrid'` for non-transport — later found to be a regression (#132 grill, fixed).
- GTM `checkout_recommendation_empty` added. Context-aware title.
- Spec analysis: ~47% vs 10/10 spec. Gap report → [[recommendation-engine-completion-roadmap]].
- Branches: FE `fix/people-also-book-title-image-price`, BE `fix/recommendation-serializer-fields` (committed + pushed end of #131).

---

## Session #130 (archived from master-state.md)

**Updated:** 2026-06-18 (session #130 END)

**Achieved this session (#130) — category-aware duration fix SHIPPED TO PROD (FE main). Spa "1 Day" bug killed.**
- **Bug (user-reported):** spa product showed duration "1 Day" — impossible. Root cause was category-wide: all activities components read `contract.tour_duration_days` (BE `PositiveIntegerField`, **default 1**, days) and rendered "X Day(s)" regardless of `service_category`. Public LIST serializer omits the field → cards saw `undefined` → ternary always yielded "1 Day". Same inline ternary copy-pasted in **5 sites** (3 components + 2 SEO JSON-LD builders).
- **Fix (FE-only, commit `35c524d` → develop → main):** new `helpers/formatContractDuration.js` single source of truth, returns `string|null`. Gated by existing `SERVICE_CATEGORY_CONFIG.showDuration` + new additive `durationUnit` ('days'|'time'|'nights'). Per-category: spa/dining → "2h 30m" from `duration` (colon string, parsed by reused `customFormatDuration`); event/attraction/OTHER → hidden; accommodation → "N nights"; tours → days (null if absent, no false "1 Day"). Only behavior change: `OTHER.showDuration` true→false. Replaced all 5 ternaries.
- **Verified:** ESLint clean (7 files), 36 serviceCategoryHelper tests pass, BE confirmed `duration` serializes as colon string `"2:30:00"` not ISO8601 → no parser needed.
- **PROD:** FE `main` = `develop` = `35c524d`. Pushed + shipped by user. **Side effect: FE main now also carries ISR route (66d896e) — FE half of #129 ISR-REVALIDATE-GAP is now deployed.**
- New atom: [[category-aware-duration-formatter]].

---

## Session #129 — 2026-06-18 — ISR on-demand revalidation IMPLEMENTED + merged to develop both repos. Prod root cause found (www vs apex).
- **What it fixes:** admin contract content edit (description, tour_highlights, inclusions, route_info, timeline, images, policies + SEO/JSON-LD) now pushes a Next.js ISR regen in seconds. Native `res.revalidate()`, not a workaround. Chosen over lazy-timer because Next 14.2.5 standalone regen is request-triggered → quiet/zero-traffic pages never self-heal. rate stays CSR; counter stays ISR-timer.
- **Backend (`feat/isr-on-demand-revalidate` → develop `b68d201`, commit `0f2d108`):** `revalidate_frontend_isr` Celery task (`operators/tasks.py`); `_trigger_revalidate(slug)` from 2 cache-bust signals (`signals.py:46`, `:95`); `REVALIDATION_SECRET`. Enabler: `products/views.py:884` daily_counter `.update(F+1)` → no post_save storm. Admin update uses `instance.save()` (`views.py:946`).
- **Frontend (`feat/isr-on-demand-revalidate` → develop `66d896e`, commit `898159e`):** new `pages/api/revalidate.js` (secret-guarded, slug→/trips/detail + /activities/detail, 207 partial); deploy runtime-secret wiring; next_cache volume-clear hardening.
- **2 latent bugs fixed same BE commit:** `clear_trip_cache` Trip null-guard (`views.py:1729`); `precompute_contract_on_create` missing `self` — closed #127 carry.
- **PROD ROOT CAUSE (`fix/frontend-url-www` → develop `4eaaf8d`, `d37dee3`):** prod `FRONTEND_URL` = apex; site is canonical www. BE POSTed to apex → 301→www → `requests` drops POST body/auth → revalidation never landed. Fixed default→www (`settings.py:373`).
- **Verified:** `manage.py check`, 29 BE tests, ESLint, no-storm proof. New atoms: [[isr-revalidate-csr-vs-isr-field-matrix]], [[django-update-bypasses-post-save-signal]], [[frontend-url-canonical-www-not-apex]].
- **Carried into #130:** prod activation (deploy develop→main + set prod FRONTEND_URL=www + restart worker).

## Session #128 (2026-06-17) — ISR-REVALIDATE-GAP diagnosis + plan (NO code)
Root-caused admin contract edit not reaching prod activities+trips detail pages. Backend Redis bust works; Next.js Pages-Router ISR HTML never regenerated + no `/api/revalidate` route = the gap. 4-step fix plan approved. Vault ISR notes (`docker-standalone-isr-revalidate-gap`, `on-demand-revalidation-api-route`) extended/corrected. Implemented in #129.

## Session #127 (2026-06-17) — Operator cover_image pipeline upgrade + orphan cleanup, SHIPPED + DEPLOYED
- COVER-PIPELINE (BE `7040f8d`): cover upload runs through parametrized `process_operator_image`; 300KB/1920 hero budget → WebP, HEIC/HEIF/AVIF server-side.
- ADMIN HEIC (admin `874d74d`): shared `isHeic`/`convertHeicToJpeg` in `imageHelpers.js`; OperatorForm decodes iPhone HEIC→JPEG preview.
- ORPHAN CLEANUP (BE `dbbbe97`): `OperatorViewSet.update` deletes replaced logo/cover from S3 via `_safe_delete_storage_file`.
- Deployed to prod (`dcbcd76`). Carry-forward `precompute_contract_on_create` warning → **fixed #129**.

---

**Session #126 — 2026-06-17 — Operator cover-image hero SHIPPED + DEPLOYED (all 3 repos):**
- **OPERATOR-COVER** new feature end-to-end. BE (`28e584a`): `cover_image` ImageField + migration `0062` + serializer + `OperatorViewSet.update` upload. admin-dashboard (`285e83b`): cover upload box in `OperatorForm.js`. FE (`b3ed243`+`1609c38`): hero on `FeaturedImageHeader` w/ `bgDefault` fallback, floating back/share pills, white-on-image, token padding, mobile responsive (logo `w-16 sm:w-20 md:w-28`, `flex-wrap` stats, `hidden sm:block` + `line-clamp-2` description).
- **Bug fixed**: `getServerSideProps` omitted `description` → hero About never rendered. Added `description: operatorData.description`.
- Deployed to prod: `main == develop` all 3 repos.

---

**Session #125 — 2026-06-16 — Operators backend follow-ups SHIPPED to develop:**
- **OPERATOR-TAB-COUNTS** (BE `0d6a3cf`): `OperatorContractsViewSet.list` emits `summary.by_type = {ALL, PRIVATE, JOIN, CHARTER}` for FE tab badges. Counts pre-`?type=` filter, TRANSPORT categories only. Bug caught: `select_related` INNER JOIN under-counted 15→3; fix = aggregate from `Contract.objects` directly. 4 tests added.
- **OPERATOR-DESC** (verify-only): live curl confirmed `Operator.description` returns populated text. No BE change.
- **FE wiring** (FE `f75b411`): `OperatorFilterBar` `byType` prop renders `"Join (10)"` badges. About-operator section wired.
- Both feature branches merged `--no-ff` → develop, pushed. Not deployed to prod.

---

**Session #123 — 2026-06-16 — Soft-delete SHIPPED + contract dashboard cards:**
- **Shipped soft-delete**: pushed `feat/contract-soft-delete` on BE + admin, merged `--no-ff` → `develop` both repos, branch pruned local+remote. BE develop `0e52782`, admin develop `f75d721`.
- **Summary counts bug** (BE `ContractViewSet.list`): cards collapsed when a status card clicked (`status=active` scoped the summary). Fixed — summary computed with `apply_status_filter=False`, Total/Active/Inactive/Deleted stay global. Test pins summary identical across `status=active|inactive|deleted`.
- **`is_deleted` ROOT FIX** (BE `ContractSerializer.Meta.fields`): list payload omitted `is_deleted`+`deleted_at` → grid badge fell back to red "Inactive" for deleted rows AND Restore dead (selected-deleted count always 0). Added both fields. Root cause behind "can't activate 182 / shows inactive".
- **Status-aware Restore** (admin `ContractsActionBar`): bulk-button visibility follows SELECTED rows' `is_deleted` (`getSelectedContracts()` live/deleted split), not active filter.
- **Deleted badge** (`StatusBadgeCell`): id-only label, "Deleted" → hover tooltip. **Dashboard cards** (BE `accounts/views.py` + admin `Main.js`): Contracts status card + Expiry card.
- Deploy develop → prod DONE: BE `0e52782` + admin `f75d721`, migration `0061` run.
- Atoms: [[serializer-field-omission-starves-ui]], [[summary-must-not-scope-by-its-own-selector]].

---

**Session #122 — 2026-06-16 — Contract soft-delete (BE + admin) BUILT:**
- **Feature**: real soft-delete for Contract. New `is_deleted/deleted_at/deleted_by` + `Contract.soft_delete()`/`restore()` methods holding the invariant `is_deleted ⇒ is_actived=False`. `ContractViewSet.destroy()` soft-deletes, new `restore` action, admin `status=deleted` filter + `deleted_contracts` summary, `update_activation` guards `is_deleted=False`. Migration `0061`. BE commit `ce77943` on `feat/contract-soft-delete`.
- **Admin UI**: Deleted chip (`StatusBadgeCell`), Deleted filter card (`ContractsSummaryStrip`), Delete/Restore bulk actions, `deleteContract`/`restoreContract` mutations. Plus responsive labeled bulk-action buttons + tooltips. admin commits `7e3c5a9` + `5915231` on `feat/contract-soft-delete`.
- **Audit caught 3 defects, all fixed**: (1) `is_actived=False`-on-delete REQUIRED — booking guard `carts/utils.py:62` checks only `is_actived`; (2) `stations/views.py` arrival-station viewset (public+unauth) leaked inactive AND would leak deleted — fixed (closes pre-existing inactive leak); (3) ADR citations corrected.
- **Tests**: 7 new (`operators/tests/test_contract_soft_delete.py`) + 46 existing pass.
- **Frontend**: ZERO code change by design — backend public-queryset filter + invariant hide deleted.
- Atoms: [[contract-soft-delete-is-actived-invariant]], [[stations-arrival-viewset-public-leak]]. ADR [[adr-contract-soft-delete]] → accepted.
- **NOT shipped this session** — branches built+tested but not pushed. (Shipped in #123.)

**Session #121 — 2026-06-16 — Prod deploy confirm + admin-dashboard hygiene:**
- **Deploy confirmed**: FE `main` @ `19984f2` + BE `main` @ `21fbdcf` live in prod, both synced with `develop` — no pending-deploy gap.
- **admin-dashboard untracked docs** (5 files: `docs/agent-policy/SYNC.md`, `docs/operations/ENV.md`, `docs/technical/{CATEGORY_MATRIX,IMAGE_FLOW,KEY_FILES}.md`) — verified real, all already linked from `CLAUDE.md`. Committed (`5e5b984`) + pushed.
- **admin-dashboard branch cleanup**: 33 local + 31 remote branches, every one (besides `main`) merged into both `main` and `develop`. Deleted all 32 local + 29 remote stale branches. Only `main`/`develop` remain.

**Session #120 — 2026-06-16 — Build fix + dead-code cleanup + branch hygiene:**
- Debug-mantra root cause: `getOptimalImageQuality is not a function` broke build on 13 activity-detail pages. `helpers/imageOptimization.js` missing export, only existed in 3 stale agent worktrees. Re-added export, grilled module — deleted 4 dead exports (zero callers).
- 2-agent audit (code-reviewer + build-verifier) PASS, surfaced unrelated same-class bug: `pages/help/faqs.js` named-import `{ fetcher }` vs `helpers/fetcher.js` default export. Fixed.
- Committed `19984f2` → develop, pushed. Cleaned up 3 worktrees + 4 branches (1 remote).
- Atom: [[dangling-export-import-bug-pattern]].

---

**Session #119 — 2026-06-16 — Trip-detail SEO/AEO/GEO audit + full implementation:**
- **3-specialist audit** of `/trips/detail/[...slug]` (transport). 25 raw → 18 unique findings, 7 HIGH. Cross-cut root cause: `TripDetailSEO.js` docstring claimed schema it never rendered (Product only). Scrutiny pass corrected malformed-offers HIGH→MED. Vault: `r1-seo`, `r1-aeo`, `r1-geo`, `r2-leader-synthesis`.
- **Grill + implementation plan** locked: mirror day-trip server-side SEO pattern, 7 HIGH only, GEO signal-only, ISR schema price. Plan: `r3-implementation-plan`.
- **3-agent implementation team** (parallel A+B → sequential C): new `helpers/seo/tripDetailSEOUtils.js` (126 lines, 5 exports), `TripDetailContent.js` prose fix, `TripDetailSEO.js` rewritten (67→35 lines), `getStaticProps` wired, `useTripSEO.js` deleted (244 lines). 5 files, +185/-347 net.
- **Merged** `feat/trip-detail-seo-aeo-geo-fix` → develop `ca490ee`, pushed.
- **Re-audit** (3 specialists): 7/7 HIGH PASS. 1 PARTIAL (TouristTrip `@context`/`@type` duplicate key). Fixed immediately → `bddb1c0`.
- **Vault closed**: `r4-re-audit-post-impl`, index CLOSED, log updated. New atom: [[trip-detail-server-side-seo-pattern]].

---

**Session #118 — 2026-06-15 — Min-rate bug investigation + fixes FE+BE:**
- **FE `fix/min-rate-bugs`** merged → `develop` @ `a95a241`. 4 fixes: stale fareCalendar on calendar scroll, off-by-one minFare threshold, allSame false-positive, homepage route filter.
- **BE `fix/popular-routes-lowest-price`** pushed @ `4da0b81`. Root cause: single `lowest_price` subquery had no type/ratecard filter → PRIVATE/CHARTER VEHICLE rates leaked in. Fix: two subqueries + `Least()` + sentinel. **NOT YET MERGED to develop.**
- New atom: [[popular-routes-lowest-price-farecalendar-parity]].

---

## Session #116 (archived 2026-06-15)

**Updated:** 2026-06-15 (trip-page currency-context fix addendum)

**Achieved:**
- CC1 `SlideCalendar2.js:977` hardcoded `฿` → `useFormatPrice()`. CC2 `TripSummary.js:35` `from THB` → `useFormatPrice()`. CC3 JSON-LD priceCurrency intentionally unchanged (merchant offer). CC4 TripDetailSchedule deferred.
- 2 new atoms: [[currency-context-price-rendering-rule]], [[slidecalendar2-farecalendar-prop-pattern]].
- Vault audit docs, index.md, log.md updated. Branch `fix/trip-page-audit-2026-06-15` @ `3a04231` ready for merge.

---

## Session #108 (archived 2026-06-13)

**Updated:** 2026-06-13 (cross-sell audit + carried-item closure verification)

**Achieved:**
- Cross-sell audit COMPLETE — all 4 surfaces live (checkout `index.js:1008`, trip detail `[...slug].js:367`, activity detail `DayTripDetailPage.js:231`, post-booking `BookingDetailMain.js:161`). GTM `item_category` + activity-detail accuracy already shipped (vault was stale). Stale atoms corrected: `cross-sell-integration-status-2026-06-13`, `gtm-purchase-item-category-attribute`, `cross-sell-placement-strategy`.
- Carried items VERIFIED CLOSED: PAYMENT-FIX (both PRs merged — FE `dae26da`, BE `5653b04`), PAYMENT-DEADLOCK (`482cfc6`), DESIGN-SYSTEM-PHASE-1 (`designSystem.js:149-210`). KB-ATOMIZATION-PAYMENT deferred.
- Design system token migration shipped (prev session end): `489de5f`+`b5ce878`+`4b65756`.

**Resume (at session end):**
1. AT-1 — Airport Transfer redesign (P0). Spec: `03-knowledge/transportation-category-audit`.
2. KB atomization — 12 KB gaps, batch with next `/lint-vault`.
3. IMG-ALT-DEBUG-1 — HMR cross-module callback. Low priority.

---

## Session #106 (archived from master-state)

**Updated:** 2026-06-13 (session #106 — payment pending deadlock diagnosed + fixed)

**Achieved (#105–#106):**
- **Payment pending deadlock — diagnosed + FIXED.** Live prod bug order `PLB0229785`: charge PAID at Omise, order stuck `payment_pending` forever. Root cause: `finalize_payment` throws `PaymentAmountMismatchError` on webhook → swallowed → no recovery path.
- **3 BE fixes shipped** (`482cfc6` on `develop`): ExpirePendingChargeView recovery, reconcile_gateway_charge PAID+stuck retry, _handle_existing_charge local-PAID finalize.
- **16 new tests, 278 total pass.** Vault atom [[payment-pending-deadlock]] updated.

---

## Session #104 (archived from master-state)

**Updated:** 2026-06-12 (session #104 wrap — 8/8 E2E automated + webhook gap closed via Tailscale)

**Achieved across #102–#104:**
- **Payment deep review — FULLY AUTOMATED. All 8 previously-skipped UI tests now pass** via `e2e/checkout/payment-auto-qa.spec.ts` + fixture CLI `scripts/e2e_payment_fixtures.py`. No staging deploy needed.
- **Webhook gap closed** — Tailscale funnel `https://macbook-air-2.tailc1dfbd.ts.net/admin-dashboard-orders/payments/webhook/` registered in Omise test dashboard. Real webhook delivery verified locally: forged payload → 400, real PP charge auto-completes, webhook finalizes order with zero FE involvement, dedupe replay → `already_processed`. All 5 steps PASS.
- **New atoms written:** [[omise-webhook-tailscale-local-testing]] (setup guide + repro steps + results)
- **Branches (both `fix/payment-deep-review`):**
  - **BE (7 commits, PUSHED `6937f39`):** `d7af0e9` H3 · `3be676b` H2+M10 · `f1c17b5` H1+M8 · `6a481df` H5+M5+M9 · `67b490a` M17 · `e685fc8` unit tests · `6937f39` test fixes
  - **FE (8 commits, PUSHED `8430805`):** all pushed — H4, M1-M3-M17, jest, E2E, parser fix, CSRF-aware assertions + 8/8 automated UI tests + fixture CLI
- **Test totals (all green):** 20 BE unit + 84 FE jest + 7/7 Playwright API + **8/8 Playwright UI automated (all PASS)** = 119 passing

---

## Session #100 (2026-06-12)

**Achieved:**
- **Payment KB complete (backend + Omise)** — 3-agent parallel scan. 4 new notes: [[omise-client-integration]], [[payment-backend-charge-flow]], [[manual-adjustment-model]], [[celery-beat-payment-scheduling]]. 3 updated. 3 atoms extracted. Vault `125d56a` pushed.

---

**Updated:** 2026-06-11 (session #99)

**Achieved this session (#99):**
- **SEO + SITEMAP WHOLE-SITE AUDIT** — 3-agent team (sitemap infra / on-page meta+schema / technical rendering). Code + live (Cloudflare 403'd live fetches = P0-1 itself). 6 P0, 10 P1, ~16 P2 findings. Key: fabricated review schema ×3 sources (Google manual-action risk), broken `noindex` via nonexistent next-seo `robots` prop, activities canonical malformed, sitemap ships ~20 private URLs, ~480 lines dead JSON-LD pipeline in trip detail. Soft-404 recommendation overruled per [[gsc-crawled-not-indexed-investigation-2026-06-05]] 3-phase plan. Vault note: [[seo-sitemap-whole-site-audit-2026-06-11]]. Audit only — no code changed. Frontend `develop` clean @ `7107516`.

---

**Updated:** 2026-06-11 (session #98)

**Achieved this session (#98):**
- **BOOKING-PAY-REPRO-1 C1+C2 fixed** — `isCartLoaded &&` gate (`checkout/index.js:188`) + `error?.status === 404` guard (`check-and-createcart.js:67`). Grill + scrutinize validated. Commit `cb817d9`.
- **FRONTEND-AUDIT-MANUAL-PRS DROPPED** — all 3 branches confirmed merged via `git branch -r --merged develop`. Retroactive PRs = no value.
- **BRANCH-CLEANUP-REMOTE CLOSED** — 42 stale `origin/2606*` branches deleted. 45 active remain.
- **FRONTEND-AUDIT-FOLLOWUP-1 CLOSED** — 2 exhaustive-deps suppressions in `FormikValuesSync.js`. Scrutinize caught agent's wrong dep-swap proposal; kept `cartitems?.cart_item` (tighter RTK trigger). Commit `7107516`.
- **CROSS-SELL-MERGE CLOSED** — branch already fully merged (confirmed `git merge-base`). Renamed remaining work → `CROSS-SELL-BD-INVENTORY` (BD task).
- **1 atom extracted**: `checkout-formdata-persist-guard-pattern.md`

**Resume point (from #98):**
1. **CROSS-SELL-BD-INVENTORY** — BD task. No eng work. BD creates: return route Koh Lipe→Hatyai Airport + DAY_TOUR contracts at Koh Lipe + SPA_WELLNESS contracts at Koh Lipe. Cross-sell auto-hides until `recommendation_count > 0`.
2. **AT-1** — Airport Transfer redesign (P0 spec in vault). Awaits user direction.
3. **GSC-1 Phase 3** — needs backend `route_exists` field.

---

**Updated:** 2026-06-11 (session #93)

**Achieved this session (#93):**
- **Two-pass verification of [[booking-payment-e2e-audit-2026-06-11]]** — audit-of-audit, all claims hand-checked against code:
  - Pass 1 (direct read): all 4 confirmed bugs + C1/C2 candidates + every backend claim exact. One omission fixed: 3 test files added to Bug 3 stable_id sweep (`useCheckoutAutoSave.test.js`, `savePassengerAssignmentsToCart.test.js`, `checkoutPersistence.test.js`).
  - Pass 2 (debug-mantra falsification): all root causes survived active disproof. Backend emits zero `stable_id` anywhere (double-confirms bugs 1/2); Effect 2 cannot rescue bug 1 (ref-equality early return `useCartSync.js:201-203`); `useCartSync.js:155` is sole `clearTripInfo` site (bug 2 has no alternate pruning path); C1 mount-state assumptions confirmed (`cartId: null` initial, `_persist.rehydrated` selector).
  - Doc amended with falsification notes — verified twice, safe to act on.
- **2 atoms extracted**: [[rtk-lazy-query-tuple-misuse]], [[redux-persist-gate-scope-gap]]

---

**Updated:** 2026-06-11 (session #92)

**Achieved this session (#92):**
- **People Also Book — 3-agent audit + debug-mantra falsification**: Initial 4 bugs → 1 confirmed real bug. Duplicate detection toast never fired (backend 400 ≠ frontend catches 409). Fixed `RecommendationBookingModal.js:177-183` (`a64d280`).
- **People Also Book — 5-agent update-behavior research**: Full trace of how recommendations refresh after cart add. Cart IS live (RTK tag invalidation `api-slice.js:58,119`). Two design flaws found and fixed (`d64adcf`):
  1. Anchor changed from last→first transport — prevents circular recommendations when cross-sell transports added
  2. `visibleRecommendations` now filters `cartContractIds` — already-booked trips no longer ghost in list
- **3 atoms extracted**: [[rtk-cart-tag-invalidation-auto-refetch]], [[recommendation-anchor-first-transport-rule]], [[django-400-vs-409-duplicate-cart-item]]
- **Vault audit updated**: [[people-also-book-checkout-audit]] corrected twice (3 false positives overturned)

---

**Achieved this session (#91):**
- **"People also book" full cross-sell redesign** — frontend `feat/redesign-people-also-book-cards` `3cda359`:
  - `RecommendationCard.js` — horizontal compact card (72px thumbnail left, info right); per-category thumbnail (operator logo for transport, `getDayTripCoverImage` for activities); subtitle = route+duration (transport) or category label+duration (activities); shadow-only card; "Book" button replacing "View →" link
  - `RecommendationSkeleton.js` — compact variant updated to horizontal shape
  - `CheckoutRelatedTrips.js` — count pill in header, `flex flex-col gap-2` grid, `openInNewTab={false}`
  - `findMinVehicleSeat.js` — null guard for undefined `transport_composit`
  - `BookButton.js` — `formatItemName` optional-chain for non-transport; `transport_composit?.map() || []` GTM guard
- **`RecommendationBookingModal.js`** (new) — inline date+passenger picker, books any category without leaving checkout
- **`useDayTripAvailability.js` fixed** — fail-open when `is_actived`/`start_date`/`end_date` undefined
- **Backend availability bug fixed** — `ContractRecommendationSerializer` `62e8755`: 11 missing fields added, N+1 prefetch on all 4 query blocks

---

**Achieved this session (#90):**
- **Checkout Next btn bug FIXED (frontend)** — `FormCard.js` `f7d2956` on `develop`:
  - Root cause: commit `92bf653` ("resolve active contract", 2026-02-27) replaced `isAdvanceBookingError` in `shouldDisableNext` with `!isCurrentStepValid`, accidentally dropping the advance-hour/stop-sale guard. `isAdvanceBookingError` remained computed + used for the warning Alert but never blocked the button.
  - Fix: `(currentStep === 0 && (!isCurrentStepValid || isAdvanceBookingError || isAuthLoading))` — one line.
  - Also added `isAuthLoading` prop — blocks Next while `useSession` resolves (`status === 'loading'`), closing auth-race gap where unauthenticated user could reach step 1.
- **Backend validation gaps CLOSED** — `carts/utils.py` + `carts/serializers.py` `aed70f6` on `develop`:
  - `copy_cartitem_to_bookingitem`: now calls `check_advance_hour()` + `stop_sale_dates` filter before creating BookingItem — previously only `is_actived`/`confirm` checked at booking creation time.
  - `AddCartSerializer.validate`: stop_sale_dates check added alongside existing `is_valid_travel_date` — CartItem creation now also blocked on stop-sale dates (previously only availability endpoint enforced this).
- **2-agent debate** — strict vs permissive reviewers identified 5 gaps total; auth-race selected as high-priority fix. Remaining gaps (stale isFetching, is_actived null, null traveling_date, QR forward nav) logged but deferred.

---

**Updated:** 2026-06-10 (session #89)

**Achieved this session (#89):**
- **Cross-sell system IMPLEMENTED** — all 10 service categories supported, BD validation gate wired:
  - `find_activity_contracts` — new backend function: location-JOIN (`primary_location` + `service_areas` M2M + `.distinct()`) returns DAY_TOUR/SPA/etc at transport arrival location. `'activity'` added as valid rec type. `smartenplus-backend` `4877d65` on `260610-feat/cross-sell-activity-recommendations`
  - `CheckoutRelatedTrips` — full rewrite: category-aware anchor (transport→`packages`, activity→`activity`), sessionKey GTM de-dup (sessionStorage), expanded by default, "People also book" title, price floor filter, 161 lines. `smartenplus-frontend` `61f2ec2` on `260609-feat/cross-sell-gtm-recommendations`
  - `checkout/index.js` — mounted at formStep=0 after ItinerariesStep
  - `RelatedExperiences` — migrated to recommendations API
  - `CheckoutSidebar` — cross-sell removed (abandonment risk at payment step)
  - `RecommendationCard` — service_category chip for non-transport products
- **Cross-sell strategy fully documented** — `03-knowledge/cross-sell-placement-strategy.md`: 10-category matrix, rec type logic, branches, BD gate, GTM clock definition
- **CROSS-SELL-1 OPEN** — blocked by BD inventory gap (no return route + no DAY_TOUR/SPA contracts at Koh Lipe → engine returns 0 → 60-day BD clock cannot start)

---

## Session #88 (archived from 2026-06-10)

**Achieved:**
- **WP Media Library tab SHIPPED** — `admin-dashboard` `99e45b2`: `WordpressImages.js`, `wordpressMediaApi.js` RTK slice, MUI Tabs in `ImageSelection.js`, `/wp-api` rewrite proxy
- **Image URL bug pipeline fixed** — `smartenplus-backend` `b3b8ee0`: `get_image()` verbatim https:// fix, `is_deleted=False` filter on `imagegallery_set`, PK guard for `wp_` prefix
- **WP-IMAGE-1 CLOSED.**

---

## Session #87 (archived from 2026-06-09)

**Achieved:**
- **ProductImages ↔ OperatorImages parity SHIPPED** — 2 repos on `develop`:
  - `admin-dashboard` `c425ff6` — feat(operator-images): bring ProductImages to parity (search/filter, metadata dialog, caption bar)
  - `smartenplus-backend` `e777816` — feat(operators): add alt_text/description/caption to ImageGallery + persist on update
- **Backend schema** — 3 nullable `CharField(250)` on `ImageGallery` (alt_text, description, caption). Migration `0059` applied. Serializer exposes all 3 as writable.
- **Shared module** — `components/Images/shared/` with `ImageMetadataDialog`, `ImageSearchBar`, `useImageSearch`, `DraggableImageCard` (caption bar). OperatorImages + ProductImages both consume it. No duplication.
- **Add-flow carries metadata** — `addImageIfUnique` copies alt_text/description/caption from `OperatorImageGallery` to `ImageGallery` via `imageSelection` payload. No FK, only string refs.
- **Edit-flow reuses contract Save** — click tile → `ImageMetadataDialog` in edit mode → writes to Formik `imageSelection` + provider `useAlert` snackbar → contract Save persists. No separate mutation endpoint. No new save button.
- **Bug fix (debug-mantra)** — `operators/views.py:720-722` `elif` branch only wrote `order` on existing `ImageGallery` rows, dropped metadata. Fix: `else` branch with unconditional metadata sync + operator_image fallback chain. `c185523`.
- **3 atoms extracted** — [[django-partial-update-elif-metadata-drop]], [[image-metadata-formik-state-only-save]], [[add-flow-metadata-helper-pattern]].

---

## Sessions #88/#87 — fuller blocks (moved from master-state 2026-06-11; condensed versions above)

**Achieved this session (#88):**
- **WordPress Media Library tab SHIPPED** — `admin-dashboard` `99e45b2` on `develop`:
  - `WordpressImages.js` — new component: search + debounce + Load More pagination via `X-WP-TotalPages`
  - `ImageSelection.js` — MUI Tabs (Operator Images / WordPress Media), both panels mounted + RTK cached
  - `wordpressMediaApi.js` — RTK Query slice proxied through `/wp-api`, normalises WP response (`wp_` id prefix, `stripHtml` caption)
  - `store/index.js` — registered reducer + middleware, blacklisted from persist
  - `next.config.js` — `/wp-api/:path*` rewrite + `smartenplus-wp-s3` remotePattern
- **Image URL bug pipeline fixed** — `smartenplus-backend` `b3b8ee0` + `f7010d2` on `develop`:
  - `operators/serializers.py` — `get_image()` SerializerMethodField: returns stored `https://` verbatim
  - `operators/views.py` — store full `https://` verbatim; guard PK lookup against `wp_` prefix
  - `products/serializers.py` — `get_image()` fix + `is_deleted=False` filter on `imagegallery_set`
- **Root cause** — id=2881 `is_deleted=True` row with wrong-bucket URL leaking through unfiltered `imagegallery_set`.
- **WP-IMAGE-1 CLOSED.**

**Achieved this session (#87, alt_text + caption — note: Section 2 logs IMG-ALT-1 as closed #86):**
- **Operator image alt_text + caption SHIPPED** — 2 repos on `develop`:
  - `admin-dashboard` `71c2352` — feat(operator-images): edit alt_text + caption alongside description
  - `smartenplus-backend` `08b6593` — feat(operators): add alt_text + caption to OperatorImageGallery
- **Schema** — 2 nullable `CharField(250)` on `OperatorImageGallery` (alt_text, caption). Migration `0058`. Serializer exposes both as writable.
- **Dialog UX** — `pages/routemanagement/operators/images/ImageEditDialog.js` now has 3 `TextField`s (alt/description/caption), each `maxLength=250`. Alt text auto-prefills from `<operatorName> - <filename-slug>` when empty. Grid `alt` chain: `alt_text || description || operator_name || ''`.
- **Debug saga** — symptom "only description persists" survived hard refresh. Five `[DBG-IMG-EDIT]` probes (dialog → page → RTK → network → backend) proved code was correct end-to-end. Root cause: Next.js Pages Router Fast Refresh replaced `ImageEditDialog` module (3 fields visible) but left the parent `index.js` module's `handleDialogSubmit` callback stale → it destructured only OLD keys and dropped alt/caption. Hard refresh after the second `.next` recompile finally replaced the parent module. Probes removed, code clean.
- **IMG-ALT-1 CLOSED.** Atom: [[operator-image-alt-caption-fields]]. Debuggable artifact: [[nextjs-hmr-cross-module-callback-staleness]].

---

## Session #83 (2026-06-08) — FAV-1 FAVORITE HEART SHIPPED (7 commits)
- **FAV-1** — 7 commits merged to develop across 2 repos (5 FE + 2 BE), pushed to origin. Manual smoke on detail page PASSED.
- **Team workflow** (3 parallel specialists → synthesis → skeptic → leader) → 7 vault files in `01-projects/favorite-heart-analysis-2026-06-08/`: `audit.md`, `r1-backend.md`, `r1-frontend.md`, `r1-ux.md`, `r2-skeptic.md`, `r3-leader-synthesis.md`, `migration-0026-runbook.md`.
- **5 BLOCKERs closed:** cross-CT data loss (blog path filter silent corruption), LikeViewSet 405 on DELETE, BookmarkViewSet 405 on DELETE, DayTripCard keyboard race stopPropagation, prod dup audit (DROPPED per user "doint touch rds" — runbook in vault).
- **3 NITs closed:** lru_cache(maxsize=1) on contract ContentType, RTK Query migration supersedes useAuthAxios hook plan (Q5), IntersectionObserver rootMargin 100px→200px.
- **Frontend commits:** `7267ed7` (keyboard race), `23630f3` (RTK Query refactor BookmarkButton + LikeButton), `b003168` (44px a11y + focus ring + scale pulse + IntersectionObserver hydration), `4bc852b` (DEAD CODE on DayTripHero.js — file never imported), `d6c8b8c` (port favorite to actual hero AirbnbPhotoGrid).
- **Backend commits:** `d1cf0b1` (cross-CT filter fix + 2x @action decorator), `15b51b5` (lru_cache contract CT).
- **Grill decisions Q1-Q5:** Q1 prod dup audit first → DROPPED; Q2 IntersectionObserver hydration; Q3 wishlist page defer; Q4 keep 6 agents (~90 min); Q5 RTK Query supersedes useAuthAxios hook.
- **Two-tab race policy (§B):** 409/404 treated as success (unique_together guarantees idempotency).
- **No PR review** (no `gh` CLI installed; user opted for direct merge).
- **Vault updates:** 7 FAV-1 files + 1 log.md entry + 1 master-state FAV-1 row closed.
- **Lint clean** (3 pre-existing warnings unrelated to FAV-1).

**Resume point:**
1. F11-FOLLOWUP content answers — apply 1-line patches if BD/content team answers differ from defaults (Q1.1 FAQ count, Q1.2 tag slugs, Q2.1 source links). Doc: `00-inbox/2026-06-07-content-questions-help-faqs.md`. Deadline 2026-06-09.
2. RDS 0026 migration apply (deferred from this env) — whoever runs prod migrations owns: pre-apply audit SQL → cleanup if dups → apply 0026 → apply 0027 (cascades). Full runbook: `01-projects/favorite-heart-analysis-2026-06-08/migration-0026-runbook.md`.

## Session #71 (2026-06-07) — Visual check session (no code)
- Verified WA-5 fixes render correctly via dev server (localhost:3000).
- All 15 file changes from `781bf7a` intact.
- No new commits. Checkpoint tag `pre-wa5-audit-2026-06-07` still available.

**Resume point:** RR-1 → GYG-IMPL → TSTD-1

## Session #70 (2026-06-07) — WA-5 EXPANDED (comprehensive touch-target audit)
- **Scrutinize #69** found F2 was partial; recommended comprehensive audit
- **WA-5** `781bf7a` — Floor 15+ clickables at 40px (WCAG 2.5.5). 15 files, 52+/30-.
- SearchDialogTrigger (3 variants): mobile 26→40, desktop 32→40, input h-10→h-11
- Footer nav: 9 links → `inline-flex items-center min-h-40`
- 10 IconButton `size=small` → `size=medium`
- 8 single-file fixes (SingleComment, SearchBar, SearchResultsList, PaymentComponent, ReactionTrigger, Coupon, LocationTree)
- e2e test +2 assertions (search trigger mobile, footer privacy)
- Checkpoint tag `pre-wa5-audit-2026-06-07` for rollback
- Lint clean (5 pre-existing warnings unrelated)
- **Deferred:** 5 text-xs onClick spans (TripItem, tripItemv2, TripItemFooter, TripDetailsAttribute, TripDetailInfo) + TripDetailBooking/TripDetail3 role=button — visually risky, need product decision

**Resume point:** RR-1 → GYG-IMPL → TSTD-1

## Session #68 (2026-06-07) — WA-3 F11 SHIPPED (spec mismatch corrected)
- **F11** `d9d1425` — Add visible FAQ section to homepage. 1 file, 18+. `pages/homepagev2.js` insert `<Section id="faq-section">` between TravelThailandBetterSection and LocationsSection. 5 native `<details>/<summary>` from existing `faqsData`. No JS state, no new component. Lint clean. Fast-forward to develop.
- **Spec mismatch noted.** F11 spec said "Add FAQPage schema"; reality: `FAQPageJsonLd` already wired at line 240 (pre-existing). Pre-check: `helpSubcategories` is subcategory metadata, not Q&A. Real Q&A source = `faqsPosts` (line 454, pre-existing). New work = visible content only.
- **WA-3 Sprint 3 CLOSED.** F9 + F10 + F10-followup + F11 all shipped.

**Resume point:** WA-5 → RR-1 → GYG-IMPL → TSTD-1

## Session #67 (2026-06-07) — WA-3 F9 SHIPPED (spec mismatch corrected)
- **F9** `0b30580` — Add `ELEVATION_TOKENS` (`none/sm/md/lg/xl`) to `helpers/designSystem.js`. Extract 2 real boxShadows: `ProfileButton.js:20` → `ELEVATION_TOKENS.lg`; `NavDropdown.js:72` → `ELEVATION_TOKENS.md`. 3 files, 15+/2-. Lint clean. Fast-forward to develop.
- **Spec mismatch noted.** F9 spec listed 5 files for extraction; audit found only 2 boxShadows in entire codebase, in 2 different files. Spec-listed files have only dynamic/ternary styles that correctly stay inline per F9 rule. User accepted "extract the 2 real ones" — no fabrication.

**Resume point:** WA-3 F11 → WA-5 → RR-1 → GYG-IMPL → TSTD-1

## Session #66 (2026-06-07) — WA-3 F10-followup Part 3 SHIPPED
- **F10 Part 3** `324d449` — Replace 5 hardcoded `'SmartEnPlus'` NextSeo `siteName` sites with `siteName` import from `helpers/constants.js`. 5 files, 10+/5-: `components/FrontPage/Seo.js`, `pages/privacy/index.js`, `pages/ref/index.js`, `pages/ref/[type].js`, `pages/blog/index.js`. Fast-forward to develop. Lint clean.
- **F10 + F10-followup fully CLOSED.** No more hardcoded brand name in OG siteName. No `BRAND_NAME`. No typo refs. `siteName` = single source of truth.

**Resume point:** WA-3 F9 → F11 → WA-5 → RR-1 → GYG-IMPL → TSTD-1

## Session #65 (2026-06-07) — WA-3 F10-followup closed (clean state)
- **F10 revert** `cf71511` — Drop `BRAND_NAME`, keep `siteName` (user callout: duplication). 5 files, 9+/14-: `helpers/constants.js` (-1 export), `pages/_app.js` (-1 import + 4 sites), 3 structured data files (-1 import + 5 sites). Fast-forward to develop.
- **F10 typo imports fix** `a2c6d27` — Update 9 imports + 1 URL to renamed `smartenplus-transportation-booking-online.webp`. 10 files, 10+/10-. F10 (#64) renamed file but only updated 1 import; build was broken at 9 import sites. Fast-forward to develop.
- **F10 closed cleanly.** No `BRAND_NAME` in code. No `smartenpus-` typo refs. `siteName` = single source of truth (9 use sites). Typo file rename fully consistent.
- Lint clean both branches.

**Resume point:** WA-3 F10-followup Part 3 (5 hardcoded 'SmartEnPlus' sites in pages/ → siteName import) → WA-3 F9 → WA-3 F11 → WA-5 → TSTD-1

## Session #64 (2026-06-07) — WA-3 F10 closed (spec scope)
- **WA-3 F10** `e3194dc` — Brand name consistency: `BRAND_NAME = 'SmartEnPlus'` constant added to `helpers/constants.js`, 8 hardcoded sites replaced in 4 files (DefaultSeo + 3 structured data components), 1 typo file renamed
- 7 files changed, +15/-10, fast-forward merge to develop
- **Spec under-scoped:** audit found 39 total `'SmartEnPlus'` occurrences; spec listed 9. Shipped spec-faithful 8 sites; 30+ deferred to **F10-followup**
- Lint clean

**Resume point:** WA-3 F10-followup → F9 → F11 → WA-5 → TSTD-1

## Session #63 (2026-06-07) — WA-7 closed
- **WA-7** `f1cbb5d` — Mobile input height parity: `min-h-[44px]` added to From/To labels (lines 228, 257) in `ProductSearchForm2.js` to match Date/Return/Passenger cell pattern
- 1 file, +2/-2, fast-forward merge to develop
- Grill review: passed — no High/Medium issues, F8's `min-w-0` and WA-7's `min-h-[44px]` are independent CSS axes
- All 5 input cells now have `min-h-[44px]` (Date/Return/Passenger + From/To)

**Resume point:** WA-3 → WA-5 → RR-1 Sprint 1 → GYG-IMPL → TSTD-1

## Session #62 (2026-06-07) — WA-2 Sprint 2 CLOSED (F4-F8)
- **F4** `1d2d749` — Inter font self-host via `next/font/google` (no FOUT, GDPR clean)
- **F5** (static) — Carousel `align: 'start'` already in `CardCarouselContainer.js:17-21`; 2 unmerged remotes are ancestors of develop
- **F6** `041f51a` — Nav dedupe: `/locations` label "Routes" → "Locations" in `navConfig.js`
- **F7** `7895695` — OG image 1200×630 WebP (new asset + 4-line `pages/_app.js` edit)
- **F8** `d1fcf47` — `flex-wrap` + `min-w-0` on `ProductSearchForm2.js` row (MH3, High)
- All 5 branches fast-forwarded to develop, pushed
- Code review (grill) on F8 found false positive: desktop 2-line wrap is design intent (search button CTA below 5 inputs)
- WA-7 noted: mobile input height inconsistency between From/To (no min-h) and Date/Return/Passenger (min-h-[44px])

**Resume point:** WA-3 → WA-7 → WA-5 → RR-1 Sprint 1 → GYG-IMPL → TSTD-1

## Session #60 (2026-06-06)
- **F3 — Social icon 40×40 wrapper batch** (Sprint 1 P0 closeout). 1 commit on frontend `develop`:
  - `9472df5` — Wrap isolated social icons in `inline-flex items-center justify-center min-w-[40px] min-h-[40px]` per `icon-button-size-decision` atom. 4 files: `components/UI/ShareButton.js` (WhatsApp `<span>`), `components/layout/footer.js` (4 social `<Link>`s), `components/search/Passenger.js` (3 social `<Link>`s), `components/pages-info/ContactUs.js` (4 social `<Link>`s). Added missing `aria-label`s. **Row-wide consistency rule applied:** when WhatsApp wrapped, all sibling icons in the same row wrapped too (same a11y gap, visual consistency).
- **WA-1 Sprint 1 P0 CLOSED.** F1 (search 16px) + F2 (44→40px dense UI) + F3 (40px wrapper) all shipped.

**Resume point:**
1. WA-2 Sprint 2 P1 (F4-F8) — Inter font self-host, carousel `align: 'start'`, nav dedupe, OG image 1200×630, search form overflow. ~7 hrs.
2. WA-5 — Footer secondary nav + SearchDialogTrigger mobile button touch targets. ~2 hrs.
3. Verify FE-22 API shape — `smartenplus-backend/dialogue/serializers.py` ReviewSerializer POST response.
4. Build production Docker with `libheif-dev` (backend HEIC dependency).
5. TSTD-1 test infra — BLOCKS RELEASE. 6 CRITICAL gaps. Schedule 4-5 day block.

---

## Session #59 (2026-06-06)
- **3 touch-target bug fixes** on frontend `develop`. 3 commits:
  - `1e4c549` — **Swap button re-center** after F2 44px bump. `ProductSearchForm2.js:249` `left: -17px` → `-23px` (re-center 46px wrapping div on From/To boundary).
  - `fbdca15` — **Swap/currency/profile 44→40 revert** (user feedback: 44 too big for dense UI). 4 files: `ProductSearchForm2.js`, `CurrencySelector.js`, `ProfileImage.js`, `e2e/a11y/touch-targets.spec.ts` (3 test thresholds). Swap wrapper `left: -23px` → `-21px` to match 4px shrink.
  - `e782c41` — **Mobile drawer English/currency center** fix. `components/layout/layout.js:204-206` 3 className edits: parent `items-start` → `items-center`, both cells `text-center` → `flex justify-center items-center`, English cell `py-2` for 40px pill visual parity.
- **1 atom extracted** to `03-knowledge/` — `icon-button-size-decision` (40px default for icon buttons in dense UI, 44px reserved for primary CTAs).

**Resume point:**
1. F3 — WhatsApp 20×20 → 44×44 wrapper (`components/review/ShareButton.js`, footer, `Passenger.js`, `ContactUs.js`) ~1 hr.
2. Sprint 2 P1 (F4-F8) — Inter font self-host, carousel `align: 'start'`, nav dedupe, OG image 1200×630, search form overflow. ~7 hrs.
3. Verify FE-22 API shape — `smartenplus-backend/dialogue/serializers.py` ReviewSerializer POST response.
4. Build production Docker with `libheif-dev` (backend HEIC dependency).
5. WA-5 — Footer secondary nav + SearchDialogTrigger mobile button touch targets.

---

## Session #58 (2026-06-06)
- **Sprint 1 P0 — F1 + F2 SHIPPED** (website audit). 4 commits on frontend `develop`:
  - `40c01e2` **F1** — Search input font 14→16px (iOS zoom fix). 6 inputs across `ProductSearchForm2.js` + `SearchDialogTrigger.js`.
  - `0f9df12` **F2** — 44×44px touch targets (WCAG 2.5.5). 5 component files: `CurrencySelector.js`, `ProfileImage.js`, `CartButton.js`, `ProductSearchForm2.js` (3 buttons), `CarouselArrowButtons.js`. New regression spec `e2e/a11y/touch-targets.spec.ts` (8 assertions × 4 viewport projects).
- **ProfileMenu UX consolidation** (3 commits):
  - `44e209d` — Post-F2 regression fix: desktop `<Menu>` Paper had no `maxHeight`/`overflowY`; F2's `ProfileImage` 36→44 height pushed the anchored menu 8px past viewport edge. Added `MenuListProps` + `PaperProps` with `maxHeight: calc(100vh - 120px)`, `overflowY: auto`.
  - `40b0a36` — Combine Ask Away + Explore More into expandable `<ExpandableMenuRow>` parent + 2 `<SubMenuRow>` children (both → `/forum`).
  - `f4d581f` — Group Edit Profile + Family & Friends + Change Password into "Account" expandable. Newly surfaces `/account/editPassword` route.
  - `314020c` — Group My Bookings + My Orders + Rate & Reviews into "My Activity" expandable.
  - **Cumulative menu height savings: −240px** (default collapsed). Desktop menu now fits fully on 1280×720 with all 3 expandables open.
- **3 atoms extracted to `03-knowledge/`** — `mui-menu-paper-overflow-guard`, `expandable-menu-row-mui-collapse`, `wcag-touch-target-enforcement`.

**Resume point:**
1. F3 — WhatsApp 20×20 → 44×44 wrapper (`components/review/ShareButton.js`, footer, `Passenger.js`, `ContactUs.js`) ~1 hr.
2. Sprint 2 P1 (F4-F8) — Inter font self-host, carousel `align: 'start'`, nav dedupe, OG image 1200×630, search form overflow. ~7 hrs.
3. Verify FE-22 API shape — `smartenplus-backend/dialogue/serializers.py` ReviewSerializer POST response.
4. Build production Docker with `libheif-dev` (backend HEIC dependency).
5. WA-5 — Footer secondary nav + SearchDialogTrigger mobile button touch targets.

---

## Session #54 (2026-06-06)
- **HEIC-1 CLOSED** — Client-side HEIC preview fixed. `heic2any` added (`^0.0.4`). `RateAndReviewForm.js` `onChange` async-converts HEIC/HEIF → JPEG via dynamic import. Committed `6c10137` on `develop`.

**Resume point:** Verify FE-22 API shape → Sprint 1 (P1-3→P1-9) → Docker libheif-dev build.

---

## Session #52 (2026-06-06)
- **Rate-review UX/UI audit COMPLETE** — 6-agent team (r1-ux, r1-visual, r1-frontend, r2-skeptic, r3-leader-synthesis, r4-scrutinize). 52 raw findings → 34 unique. 3 P0 confirmed.
- **Scrutiny pass** — 4 corrections applied to r3. r5-implementation-plan written.
- **Release 1 SHIPPED** — 5 fixes: XSS DOMPurify, parseISO null guard, star ARIA radiogroup, router import + leading slashes, email masking. Branch: `260606-fix/heic-review-upload`.

**Resume point:**
1. Verify FE-22 API shape — check backend ReviewSerializer POST response (`slug` vs `booking_item_slug`).
2. Lint + test Release 1. Merge `260606-fix/heic-review-upload` → develop.

---

## Session #51 (2026-06-06)
- **HEIC review upload — IMPLEMENTATED, local deps ready** — pillow-heif 0.15.0 + libheif 1.23.0 installed locally. Backend restarted with HEIC opener registered. Code committed: backend `f82b182`, frontend `0a4e6d4`. Branch: `260606-fix/heic-review-upload`.
- **Multi-agent debate** — 2 agents evaluated base64 proxy vs pillow-heif. Chose server-side (5 lines, 33% less payload, no memory spike).
- **Test deferred** — User to test HEIC upload later, then merge to production.

**Resume point:**
1. **Test HEIC upload locally** — Upload HEIC file via review form, verify WebP conversion ≤120KB.
2. **Merge `260606-fix/heic-review-upload`** → main (backend) + develop (frontend).
3. **Build production Docker** with libheif-dev.

---

## Session #50 (2026-06-05)
- **DOMAIN-1 closed** — deploy + cache clear confirmed. `NEXT_PUBLIC_DOMAIN` propagated.
- **GYG-THUMB Review Images — DONE (unmerged)** — Full image support across 2 repos: ReviewImage model + WebP ≤120KB conversion + lightbox thumbnails + file upload form + profile menu + review detail page + CSR refetch. 7 bugs found+fixed. Backend `3d1d91a`, frontend `e73fc23`, both pushed.
- **Vault optimized** — extracted dead weight to `vault-protocol.md`, `vault-guardrails.md`, `session-history.md`, `closed-items.md`. 78% reduction in master-state.md size. Report: [[vault-wrapup-optimization-report]].

**Resume point:**
1. Merge `260605-feat/review-images` → develop (frontend) + main (backend). Run migration on production.
2. GYG-THUMB follow-up: Review edit mode (RateAndReviewForm dual-mode). Backend `partial_update`.

---

## Session #49 (2026-06-05)
- **Activities /activities default category — FIXED + SHIPPED** — `hooks/useDayTripFilters.js` `DEFAULT_FILTERS.category`: DAY_TOUR → null. `filtersFromQuery` `|| null` fallback. Commit `3a4db81` → frontend develop → pushed.
- **Activities pagination reset bug — ROOT CAUSE FOUND + FIXED + SHIPPED** — StrictMode + didMountRef. No-op guard in `useDayTripFilters.js:67-75`. `scroll: false` on `router.push`. Commit `01b3708` → frontend develop → pushed.
- 3 atoms: [[react-strictmode-useref-persistence]], [[react-state-no-op-guard-side-effect-prevention]], [[nextjs-shallow-router-push-scroll-false]]

## Session #48 (2026-06-05)
- **GSC-1 Phase 1 + Phase 2 — SHIPPED** — `seoConfig.js:41` noindex fix + station-sitemap removal. Branch `effdc49` → develop `0eaf9b2`.
- **NEXT_PUBLIC_DOMAIN leading-space bug — FOUND + USER FIXED**
- Multi-agent review: SEO + frontend + /scrutinize + /debug-mantra.

## Session #47 (2026-06-05)
- **GSC 52,400 "Crawled Not Indexed" — RESEARCH COMPLETE, NO CODE** — 3-team review. Primary cause: empty ISR trip pages. Three-tier plan designed.

## Session #46 (2026-06-04)
- **Blog canonical URL bug — FIXED + SHIPPED** — WP subdomain rewrite fix. Commits `3d30407` + `b0fce4f` → develop.

## Session #45 (2026-06-04)
- **Homepage terminology audit — DONE** — Nav labels fixed. Branch `36e2786` → develop `aef5548`.
- **Production SEO phase 2 — DONE** — /locations + /destinations confirmed different products.
- 3 atoms extracted.

## Session #44 (2026-06-04)
- **GYG P1 not-suitable badges — DONE** — `IncludedExcluded.js` + `DayTripDetailPage.js`. Branch `3f12f52` → develop.
- **GYG P2 review filter — DONE** — `ReviewListByProduct.js` filter chips. Branch `d5d7482` → develop.

## Session #43 (2026-06-03)
- **CMA-1 HOTEL_PICKUP invariant — DONE** — `ContractDetailSerializer.validate()`. Commit `3a59a41` → backend main.
- **Admin-dashboard HOTEL_PICKUP validation — DONE** — Yup schema. Commits `c2e8e4e` + `5f068ef` → admin main.

## Session #42 (2026-06-03)
- **CMA-1 casing ADR — DONE** — 6 inline comments. Frontend `375e501` → develop.
- **CMA-2 meeting_point_details — FIXED** — 2 lines in `AdminBookingSummarySerializer`. Commit `09d6f3a` → backend main.

## Session #41 (2026-06-03)
- **CMA-1 partial — 2 of 6 shipped** — `showStations` deleted `ff8006e`. Admin PATCH guard `22dc045`.

## Session #40 (2026-06-03)
- **Timeline stop deletion bug — FIXED + SHIPPED** — 5 changes across 3 repos. Migration 0028.

## Session #39 (2026-06-03)
- **Contract model ambiguity audit** — 4-round debate. 6 overlaps confirmed. Vault: [[contract-model-ambiguity-audit]]
- **Contract location help text fix (P0)** — admin form 4 strings. Commit `fa2f16a` → main.

## Session #38 (2026-06-03)
- **booking-summary 500 fix** — trip=None guard. Commit `4bec691` → backend main.
- **Frontend test infrastructure audit** — 54% pass rate, 6 CRITICAL. Vault: [[frontend-test-infrastructure-audit]]
