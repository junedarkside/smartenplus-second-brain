# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-20 (session #138 END)

**Achieved this session (#138) — Unified search dialog w/ homepage tabbed search (FE-only, no deploy).**

- **Extracted `TabbedSearchPanel`** (`components/search/TabbedSearchPanel.js`, NEW): shared shell — Transportation + Experiences tabs (`SearchModeTabs`), owns `mode` (UI-only local state, no Redux), dynamic-imports both forms (`ssr:false`). Surface-agnostic (no card wrapper).
- **`SearchDialog`**: now renders panel → all 3 dialog hosts (`StickySearchBar`, `HeaderSearchSummary`, `SearchCover`) show both tabs. Static-imports panel (no nested dynamic). **Transport path unchanged** (`handleSearch` → host `handleFindTrips` → `/trips` + close). Experiences tab self-navigates `/activities?search=&category=` + `onNavigate={onClose}` closes dialog.
- **`ExperiencesSearch`**: added optional `onNavigate` prop (post-nav close). `isSearching` reset fix — `if(isSearching) return` guard + `setTimeout(()=>setIsSearching(false),3000)` fallback, mirrors `TransportationSearch.js:86-89`. Guards stuck "SEARCHING…" on rejected/slow nav.
- **`DiscoverySection`** (`lib/homepage/components/`): inner card delegates to `<TabbedSearchPanel>`; dropped `useState`/`dynamic`/`SearchModeTabs`/`Spinner` imports.
- **2-agent review** (code-reviewer + react-specialist, report-only): zero regressions. Verified state isolation clean (no Redux contamination of transport fields), transport path intact, `ProductSearchForm2` alias still consumed by `AirportTransferHeader`+`destinations/[slug]`+`airport-transfer/[slug]` (left intact). Review's "double-divider" finding was a false alarm — `theme.js` has no `MuiDialog`/border override, `DialogTitle` borderless (MUI default).
- Merged develop (`ceaa003`, --no-ff, no conflicts), feat branch pruned (local+remote). FE main @ `ceaa003`, clean.

**Resume point (EXACT)** — eng deploy queue unchanged; this feature joins it:
1. **Deploy FE develop→main** — now carries search-dialog-tabbed (`ceaa003`) ON TOP of REC engine (zones, P0, image/price/logo_url), ISR activation, duration fix, + #136 homepage from-price fix. **Manual UI test FIRST** (see SEARCH-DIALOG-UI-TEST, Section 2). After BE deploy: bust front-page cache (`pages_info/views.py:326`, timeout 3600) else corrected prices stale 1h.
2. **#129 ISR PROD ACTIVATION** (folds into step 1): BE develop→main + prod `FRONTEND_URL=www` + non-empty `REVALIDATION_SECRET` + **restart/recreate worker** (#134 stale-worker = `unregistered task`, msgs discarded — [[celery-unregistered-task-stale-worker]]). Smoke-test: edit contract → worker log `ISR revalidated slug=... status=200`.
3. **REC-engine min-price bug** (same class, OUT OF SCOPE #136): `get_contract_price` (`services.py:74`), `RecommendationSerializer.get_lowest_price` (`serializers.py:~1105`), 6 finder annotations — all lack type filter. Reuse `route_lowest_price_annotation` pattern.
4. **Vault hygiene (deferred from #136)**: mark anchor-flip + price-floor DONE in roadmap note; retire stale [[recommendation-anchor-first-transport-rule]].
5. **Next eng (deferred, tracked)**: slot-waste `exclude_ids` API, `recommendation_purchase` GTM, UPGRADE zone (`upgrade_of` FK), multi-destination 2-anchor, weekly trending.

_(Session #137 block archived → `07-logs/session-history.md`. All repos clean: BE `cff26b3`, FE `ceaa003`, admin `bdf85ff`, content `3756e5b`. Live git: `bash vault-wrapup.sh`.)_

---


_(Session-end cleanup + carry-forward state archived to `07-logs/session-history.md`. Live git state for next session: run `bash vault-wrapup.sh`.)_

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **SEARCH-DIALOG-UI-TEST** | Unified search dialog now shows Transportation + Experiences tabs in all 3 hosts. MERGED develop `ceaa003` (#138). **NOT yet manually UI-tested** — verify PRE-DEPLOY: open each dialog (StickySearchBar / HeaderSearchSummary / SearchCover), transport tab unchanged (→ `/trips` + close), experiences tab → `/activities?search=&category=` + dialog closes, mobile full-screen Slide transition. Extracted `TabbedSearchPanel` (`components/search/`); `SearchDialog` static-imports it. | **PRE-DEPLOY verify** #138 | `components/search/TabbedSearchPanel.js`, `SearchDialog.js`, `ExperiencesSearch.js` |
| **SEARCH-UI-POLISH** | Deferred pre-existing nits surfaced by #138 review (NOT regressions). (1) `SearchModeTabs.js` ARIA: no arrow-key nav, no `aria-controls`/`role=tabpanel` association. (2) `seach-button` typo — also in `TransportationSearch.js:248`. (3) `SearchDialog.js` close icon `text-red-500` vs grey theme. (4) `SearchDialog.js` comment "close first then navigate" inverts actual nav-then-close order. (5) Mobile tab-switch height jump (`md:min-h-[120px]` desktop-only, now in `TabbedSearchPanel.js:48`). Low priority. | OPEN #138 — low | `components/search/SearchModeTabs.js`, `SearchDialog.js`, `TabbedSearchPanel.js` |
| **BE-HOMEPAGE-PRICE** | Homepage "From" prices computed BE-side. **Experiences + airport-routes FIXED #136** (`get_min_price` ADULT+fallback; airport `lowest_price` type-aware via new `route_lowest_price_annotation` helper shared with HomeViewSet). Merged BE develop `cff26b3`. **NEEDS DEPLOY + front-page cache bust.** Remaining OPEN (same bug class, out of scope #136): REC-engine `get_contract_price` (`services.py:74`), `RecommendationSerializer.get_lowest_price` (`serializers.py:~1105`), 6 finder `Min(selling_rate)` annotations — all still unfiltered. | **PARTIAL-CLOSE #136** — homepage DONE (needs deploy); REC-engine OPEN | `products/services.py` (REC), `products/serializers.py:~1105` |
| **REC-CHECKOUT-ZONES** | Checkout "Complete your trip" recommendation engine: P0 hybrid fix + zones (ESSENTIAL/POPULAR/SIMILAR) + matrix + transport finder + per-zone caps + price-bug + experience-first anchor + recType-follows-anchor + card-count tuning + add_cart GTM + mobile cap + seed command. **MERGED to develop #133** (BE `ae31f1f`, FE `0877d23`), branches pruned. | **MERGED, NEEDS DEPLOY** develop→main both repos. Then prod seed cleanup. | `products/services.py`, `components/recommendations/*`, [[recommendation-engine-completion-roadmap]] |
| **REC-SLOT-WASTE** | ESSENTIAL zone renders short (1 not 2) when a cart item overlaps a backend rec: FE excludes cart ids AFTER backend applied per-zone caps. Fix: API `exclude_ids` param threaded into finders before cap slice; cache key includes sorted exclude set. Medium. | OPEN #133 — deferred, tracked. | `smartenplus-backend/products/services.py` get_recommendations, [[recommendation-engine-completion-roadmap]] |
| **REC-PRECOMPUTE-CACHEKEY** | Low. `products/tasks.py:67` precompute builds cache key `recommendations:{id}:{type}:{limit}` (4-part) but `get_recommendations:667` runtime key is 5-part (`:{rate_date or 'none'}`). Precompute writes never hit at runtime → wasted warm. Pre-existing, found in #132 verify. | OPEN #132 — out of scope of P0 fix. | `smartenplus-backend/products/tasks.py:67` |
| **ISR-REVALIDATE-GAP** | Admin contract edit not reaching prod `/activities/detail` (revalidate 3600) + `/trips/detail` (revalidate 300). Backend busts Redis correctly (`operators/signals.py:33`); Next.js Pages-Router ISR HTML never told to regen + no `/api/revalidate` route → stale, forever on cold pages (persistent `next_cache` volume). Fix (4 steps, build order in plan): (1) BE `daily_counter`→`.update(F+1)` enabler stops per-view post_save, (2) FE `pages/api/revalidate.js` POSTs `{slug}` owns path map, (3) BE `revalidate_frontend_isr` Celery task + `_trigger_revalidate` signal helper, (4) `REVALIDATION_SECRET` both repos incl GH Actions runtime path. Task no-ops on empty secret. | **IMPLEMENTED #129 → develop** (BE `4eaaf8d`, FE `66d896e`). All 4 steps done + verified (29 tests, manage.py check, ESLint, no-storm proof). **Prod root cause found:** `FRONTEND_URL` was apex → 301→www dropped the POST; fixed default→www (`d37dee3`). **FE SHIPPED #130** (main `35c524d` carries ISR route). **BE ACTIVATION PENDING:** deploy BE develop→main + set prod `FRONTEND_URL=www` + non-empty `REVALIDATION_SECRET` + **restart/recreate worker** (#134: stale worker = `unregistered task`, msgs discarded — [[celery-unregistered-task-stale-worker]]), then smoke-test (see Section 1 resume). | `operators/signals.py`, `operators/tasks.py`, `products/views.py:884`, `Smartenplus/settings.py:373`, FE `pages/api/revalidate.js`, `deploy-ghcr.sh` |
| **DURATION-DAYS-CARDS** | Day-tour browse cards omit duration: public LIST `ContractSerializer` doesn't expose `tour_duration_days`, so cards can't show "N Days" (detail page works, uses `__all__`). FE-only fix #130 chose omission over false "1 Day". Option B: add `tour_duration_days` to list serializer `fields`. One-line, low risk (read-only int); needs BE deploy + ISR cache clear. | OPEN #130 — optional follow-up, low priority. FE helper unchanged either way. | `smartenplus-backend/operators/serializers.py` (ContractSerializer), [[category-aware-duration-formatter]] |
| **BE-IMAGE-DEDUP** | BE image-processing duplication (moderate, pre-existing). Cluster 1: WebP resize/compress algorithm duplicated ~2-3× — `operators/utils.py:process_operator_image` (now parametrized #126b), `dialogue/utils.py:process_review_image` (120KB hardcoded), plus WebP/thumbnail code in `operators/admin.py`. Cluster 2: upload validation (ext whitelist + size) copy-pasted across 5 files (`stations/views.py`, `operators/utils.py`, `operators/views.py`, `pages_info/models.py`, `dialogue/utils.py`) each with own constants → drift risk. Consolidate → one `core/image_utils.py`: `process_image_to_webp(file, *, max_output_size, max_dimensions)` + `validate_upload(file, *, allowed_ext, max_size)`, migrate all callers. | OPEN #126 — dedicated refactor session. High blast radius (operators/dialogue/stations/pages_info), zero user value, all spots work. Do NOT bolt onto feature work. | `operators/utils.py`, `dialogue/utils.py` || **SEO-SITEMAP-FIX** | Implement fixes from whole-site SEO+sitemap audit | MERGED 2026-06-12. P0+P1+P2 `1f3f7a2` merged → develop `d88f50b`, pushed. Fake reviews ×4 deleted, sitemap 128→86 URLs, noindex fixed ×5 pages, dead JSON-LD pipeline removed. Build exit 0, greps clean. **Remaining:** deploy to prod, GSC Googlebot/WAF verify (manual), nginx 301s (infra), P3 dead-code sweep. Soft-404 stays with GSC-1. | develop `d88f50b`, [[seo-sitemap-whole-site-audit-2026-06-11]] |
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
| SILAPHAT-DESC | `Operator.description` holds route notes, not real about-copy — data quality | OPEN #127 — BD/copy task | `operators/models.py` |
| BOOKING-24H | `booking_count_yesterday` is rolling 24h not calendar yesterday (mislabeled) | OPEN #127 — rename or relabel | `products/serializers.py:353-363` |
| SORT-VOCAB | Dual sort vocab: QuickSortPills PascalCase vs SortDropDown `-booked_count` | OPEN #127 — pick one, propagate | `components/UI/` |
| BE-GIT-DIVERGE | Prod backend git history diverged from origin (merge-noise) — pulls merge not FF | OPEN #127 — cosmetic | `smartenplus-backend` |

---

**See also:** [[vault-protocol]] (API contract) · [[vault-guardrails]] (architecture) · [[session-history]] (#38+) · [[closed-items]] (resolved)
