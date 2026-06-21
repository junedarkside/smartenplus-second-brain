# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-21 (session #145 END)

**Achieved this session (#145) — Git branch policy enforced in CLAUDE.md + vault-guardrails.**

- Added "Git Branch Policy — MANDATORY" to `smartenplus-frontend/CLAUDE.md` and `vault-guardrails.md`: never commit to `main`/`develop` directly, always branch from `develop`. `1c14d72` main (meta-only, skipped per user).
- Note: sessions #143–#144 committed directly to main — rule now locked to prevent repeat.

**Resume point (EXACT):**
1. **OWNER DECISIONS gate CS everything:** consent/GDPR ×9 ([[cs-consent-gdpr-model]]); P0 ×5 ([[cs-p0-measurement-protocol]]).
2. **SEARCH-DIALOG-UI-TEST** — manual verify pre-deploy: open each dialog host, transport tab → /trips, experiences tab → /activities, mobile Slide transition.
3. **ISR prod activation (#129)** — deploy BE develop→main + set `FRONTEND_URL=www` + non-empty `REVALIDATION_SECRET` + restart worker.
4. **P2 SEO fixes (optional):** twitter:image:alt, og:locale policy, meta desc cap, blog robots dup. See [[seo-audit-reconciliation-2026-06-21]].
5. **P0 test run (no code)** — ~35 Supabase travelers. Blocked on OTA-messaging owner decision.
6. **Eng carry-forward:** REC-engine min-price bug; TASK-1VCPU-MONITOR (CloudWatch).

_(Session #144 block archived → `07-logs/session-history.md`.)_

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **CS-CENTRALIZATION** | Reuse-first stack. **Channel map (final):** customer chat = website widget (polls Django ~5s, reuse `useQRPolling`); trip reminders = AWS SNS SMS; confirmations = SES (live); CS team = Telegram internal alert. WhatsApp deferred. Email-OTP `pyotp`+SES. Channels dormant. **ARCH DECIDED 2026-06-21 ([[cs-architecture-decision]]): both-sides-poll-Django, Supabase OUT of message path.** Reverses Option B — polling-ceiling math killed the "deadlock" premise; both-poll kills R1(Celery starvation)/R2(silent-ghost)/R3(anon-PII). **Prod compose CONFIRMED** (`docker-compose-rds.yml` = production; uwsgi run.sh dead): `--workers 1 --threads 2` + 256MB web cap + celery `--concurrency=1` = small box. Small box is WHY both-poll wins — short-poll releases slot in ~20ms (5 staff = ~1.6 req/s); WebSocket dies on 256MB, Supabase two-write dies on single celery worker. Real EC2 fix = instance-size up, not config flag. **No `cs` schema, no chat queue, no `sync_status`, no `@supabase/supabase-js`.** Net-new dep: **`pyotp` only**. Supabase keeps gmail12go OTA-store read-sync role only. **Gaps CLOSED:** API contract ([[cs-api-contract]] 7 endpoints, explicit fields) · consent/GDPR ([[cs-consent-gdpr-model]] two-store, 9 owner Qs) · P0 protocol ([[cs-p0-measurement-protocol]] ~35 contacts, 5 owner Qs). Token-WCAG = separate platform issue (Approach A, 3 text-tokens). 103 `__all__` serializers — pin Ticket+Order before P1a migration. **Conversion thesis REOPENED.** | **DOCS COMPLETE — awaiting owner decisions (consent legal ×9, P0 ×5) + P0 run; not scheduled for dev** | [[cs-architecture-decision]] · [[cs-api-contract]] · [[cs-consent-gdpr-model]] · [[cs-p0-measurement-protocol]] · [[smarten-customer-os-thesis]] · [[cs-centralization-stack]] · [[cs-centralization-design-concept]] |
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
