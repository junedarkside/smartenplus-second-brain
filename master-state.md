# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-22 (session #149 END)

**Achieved this session (#149) — og:image + CSP Google TLD fixes:**

- Fixed activity detail og:image for FB/social sharing: corrected image field (`image` singular matches API), absolute fallback URL, moved product namespace tags to `additionalMetaTags` (next-seo was silently dropping `product:` nested key in `openGraph`). Also fixed `generateProductJsonLd` images field (`images`→`image`).
- Fixed activity card showing default placeholder: `getDayTripCoverImage` had wrong `images` (plural) → reverted to `image` (singular, matches API `ContractSerializer`).
- Fixed CSP blocking Google Ads remarketing pixel: added 23 Google country TLDs to nginx `img-src` + `connect-src` (Europe: .co.uk .de .fr .it .es .nl .se .pl; Americas: .com.br .com.mx .com.ar .com.co .cl .ca; Asia-Pacific: .com.au .com.sg .co.jp .co.kr .co.in .com.hk .com.my .co.id .com.ph).
- All shipped to production: frontend `0026784`, nginx reloaded.

**Resume point (EXACT) — next session:**
1. **CS BUILD STEP 1** — Django `cs/` app: `Conversation` + `Message` + `CSOtp` models + composite index `(conversation_id, created_at)` + migration. Reference: [[cs-gap-debate-verdicts]] Build Order Step 1.
2. **CS BUILD STEP 2** — 7 API endpoints. Reference: [[cs-api-contract]].
3. **SEARCH-DIALOG-UI-TEST** — manual verify pre-deploy (pending from #138).
4. **ISR prod activation (#129)** — deploy BE develop→main + `FRONTEND_URL=www` + `REVALIDATION_SECRET` + restart worker.
5. **OWNER DECISIONS gate P0:** P0 ×5 ([[cs-p0-measurement-protocol]]); metric+MDE pre-commitment before pilot send.

_(Session #148 block archived → `07-logs/session-history.md`.)_

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **CS-CENTRALIZATION** | Reuse-first stack. **Channel map (final):** customer chat = website widget (polls Django ~5-10s); trip reminders = AWS SNS SMS; confirmations = SES (live); CS team = Telegram internal alert. WhatsApp deferred. Email-OTP `pyotp`+SES+PostgreSQL. Channels dormant. **ARCH DECIDED 2026-06-21:** both-sides-poll-Django, Supabase OUT of message path. Net-new dep: `pyotp` only. **Supabase source-verified 2026-06-22:** 561 total (gmail12go 58 + gmailklook 503, 100% email). All data gaps closed. **Gap debate 2026-06-22 ([[cs-gap-debate-verdicts]]):** poll safe=30 widgets (not 150, 5-10s interval); OTP=PostgreSQL `CSOtp` table (Redis allkeys-lru evicts); server-side `cursor` id not client `since` timestamp; `reopen_count` rate-limit on auto-reopen. **cs-api-contract.md updated** (4 corrections). P0 sample=~450 Klook Confirmed (not ~35). **READY TO BUILD** — Step 1: Django `cs/` app + models. Owner still needed for P0 ×5 decisions before pilot send. | **BUILD READY — Step 1 next session. P0 blocked on owner decisions (×5).** | [[cs-gap-debate-verdicts]] · [[cs-architecture-decision]] · [[cs-api-contract]] · [[cs-centralization-design-concept]] · [[supabase-ota-booking-store]] · [[cs-p0-measurement-protocol]] · [[smarten-customer-os-thesis]] |
| **SEARCH-DIALOG-UI-TEST** | Unified search dialog now shows Transportation + Experiences tabs in all 3 hosts. MERGED develop `ceaa003` (#138). **NOT yet manually UI-tested** — verify PRE-DEPLOY: open each dialog (StickySearchBar / HeaderSearchSummary / SearchCover), transport tab unchanged (→ `/trips` + close), experiences tab → `/activities?search=&category=` + dialog closes, mobile full-screen Slide transition. Extracted `TabbedSearchPanel` (`components/search/`); `SearchDialog` static-imports it. | **PRE-DEPLOY verify** #138 | `components/search/TabbedSearchPanel.js`, `SearchDialog.js`, `ExperiencesSearch.js` |
| **SEARCH-UI-POLISH** | Deferred pre-existing nits surfaced by #138 review (NOT regressions). (1) `SearchModeTabs.js` ARIA: no arrow-key nav, no `aria-controls`/`role=tabpanel` association. (2) `seach-button` typo — also in `TransportationSearch.js:248`. (3) `SearchDialog.js` close icon `text-red-500` vs grey theme. (4) `SearchDialog.js` comment "close first then navigate" inverts actual nav-then-close order. (5) Mobile tab-switch height jump (`md:min-h-[120px]` desktop-only, now in `TabbedSearchPanel.js:48`). Low priority. | OPEN #138 — low | `components/search/SearchModeTabs.js`, `SearchDialog.js`, `TabbedSearchPanel.js` |
| **BE-HOMEPAGE-PRICE** | Homepage "From" prices computed BE-side. **Experiences + airport-routes FIXED #136** (`get_min_price` ADULT+fallback; airport `lowest_price` type-aware via new `route_lowest_price_annotation` helper shared with HomeViewSet). Merged BE develop `cff26b3`. **NEEDS DEPLOY + front-page cache bust.** Remaining OPEN (same bug class, out of scope #136): REC-engine `get_contract_price` (`services.py:74`), `RecommendationSerializer.get_lowest_price` (`serializers.py:~1105`), 6 finder `Min(selling_rate)` annotations — all still unfiltered. | **PARTIAL-CLOSE #136** — homepage DONE (needs deploy); REC-engine OPEN | `products/services.py` (REC), `products/serializers.py:~1105` |
| **REC-CHECKOUT-ZONES** | Checkout "Complete your trip" recommendation engine: P0 hybrid fix + zones (ESSENTIAL/POPULAR/SIMILAR) + matrix + transport finder + per-zone caps + price-bug + experience-first anchor + recType-follows-anchor + card-count tuning + add_cart GTM + mobile cap + seed command. **MERGED to develop #133** (BE `ae31f1f`, FE `0877d23`), branches pruned. | **MERGED, NEEDS DEPLOY** develop→main both repos. Then prod seed cleanup. | `products/services.py`, `components/recommendations/*`, [[recommendation-engine-completion-roadmap]] |
| **REC-SLOT-WASTE** | ESSENTIAL zone renders short (1 not 2) when a cart item overlaps a backend rec: FE excludes cart ids AFTER backend applied per-zone caps. Fix: API `exclude_ids` param threaded into finders before cap slice; cache key includes sorted exclude set. Medium. | OPEN #133 — deferred, tracked. | `smartenplus-backend/products/services.py` get_recommendations, [[recommendation-engine-completion-roadmap]] |
| **REC-PRECOMPUTE-CACHEKEY** | ~~Low. precompute 4-part cache key vs runtime 5-part `:none`.~~ **CLOSED #139** — this was the prod-incident root cause (NOT low). Fixed `7b6a9f8` (`:none` align + cache list not dict) + skip-if-fresh + cadence tuning. Merged develop `e983c3e`, deployed, admin schedule set. | **CLOSED #139** → `07-logs/closed-items.md` | `products/tasks.py` |
| **TASK-1VCPU-MONITOR** | Verify prod incident resolved after #139 deploy: CloudWatch CPU-credit balance stops draining, no `:00`/2 AM spike. Plus 2 deferred (NOT fixed #139, low pri): `update_route_query_counts` no retry + no index on `QueryLog.query_time` (see [[update-route-query-counts-audit]]); `daily_counter`/`reset_daily_counter` registered in prod DB only, not in `celery.py` (code/prod drift). | **MONITOR #139** — verify tomorrow AM | CloudWatch, `products/tasks.py`, `Smartenplus/celery.py` |
| **ISR-REVALIDATE-GAP** | Admin contract edit not reaching prod `/activities/detail` (revalidate 3600) + `/trips/detail` (revalidate 300). Backend busts Redis correctly (`operators/signals.py:33`); Next.js Pages-Router ISR HTML never told to regen + no `/api/revalidate` route → stale, forever on cold pages (persistent `next_cache` volume). Fix (4 steps, build order in plan): (1) BE `daily_counter`→`.update(F+1)` enabler stops per-view post_save, (2) FE `pages/api/revalidate.js` POSTs `{slug}` owns path map, (3) BE `revalidate_frontend_isr` Celery task + `_trigger_revalidate` signal helper, (4) `REVALIDATION_SECRET` both repos incl GH Actions runtime path. Task no-ops on empty secret. | **IMPLEMENTED #129 → develop** (BE `4eaaf8d`, FE `66d896e`). All 4 steps done + verified (29 tests, manage.py check, ESLint, no-storm proof). **Prod root cause found:** `FRONTEND_URL` was apex → 301→www dropped the POST; fixed default→www (`d37dee3`). **FE SHIPPED #130** (main `35c524d` carries ISR route). **BE ACTIVATION PENDING:** deploy BE develop→main + set prod `FRONTEND_URL=www` + non-empty `REVALIDATION_SECRET` + **restart/recreate worker** (#134: stale worker = `unregistered task`, msgs discarded — [[celery-unregistered-task-stale-worker]]), then smoke-test (see Section 1 resume). | `operators/signals.py`, `operators/tasks.py`, `products/views.py:884`, `Smartenplus/settings.py:373`, FE `pages/api/revalidate.js`, `deploy-ghcr.sh` |
| **DURATION-DAYS-CARDS** | Day-tour browse cards omit duration: public LIST `ContractSerializer` doesn't expose `tour_duration_days`, so cards can't show "N Days" (detail page works, uses `__all__`). FE-only fix #130 chose omission over false "1 Day". Option B: add `tour_duration_days` to list serializer `fields`. One-line, low risk (read-only int); needs BE deploy + ISR cache clear. | OPEN #130 — optional follow-up, low priority. FE helper unchanged either way. | `smartenplus-backend/operators/serializers.py` (ContractSerializer), [[category-aware-duration-formatter]] |
| **BE-IMAGE-DEDUP** | BE image-processing duplication (moderate, pre-existing). Cluster 1: WebP resize/compress algorithm duplicated ~2-3× — `operators/utils.py:process_operator_image` (now parametrized #126b), `dialogue/utils.py:process_review_image` (120KB hardcoded), plus WebP/thumbnail code in `operators/admin.py`. Cluster 2: upload validation (ext whitelist + size) copy-pasted across 5 files (`stations/views.py`, `operators/utils.py`, `operators/views.py`, `pages_info/models.py`, `dialogue/utils.py`) each with own constants → drift risk. Consolidate → one `core/image_utils.py`: `process_image_to_webp(file, *, max_output_size, max_dimensions)` + `validate_upload(file, *, allowed_ext, max_size)`, migrate all callers. | OPEN #126 — dedicated refactor session. High blast radius (operators/dialogue/stations/pages_info), zero user value, all spots work. Do NOT bolt onto feature work. | `operators/utils.py`, `dialogue/utils.py` |
| **SEO-P2-FIXES** | Remaining P2 SEO fixes from [[seo-audit-reconciliation-2026-06-21]]: (1) twitter:image:alt — add to `pages/_app.js` DefaultSeo + `components/FrontPage/Seo.js` via additionalMetaTags; (2) og:locale policy — document or unify (_app.js:41 th_TH vs blog en_US); (3) meta desc length cap ≤155 chars — `pages/blog/index.js:112`, `utils/blog/seoHelper.js:136`; (4) blog robots dup — DefaultSeo + page both emit robots tag. **#15 og:url CLOSED** (`0aa748c` — Head→NextSeo, clean single tag). | OPEN — optional, low priority | `pages/_app.js`, `components/FrontPage/Seo.js`, `utils/blog/seoHelper.js` |
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
