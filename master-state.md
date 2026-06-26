# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-26 (session #173)

**Achieved (#173) — production 500 hotfix: birthDate truncated year:**
- **Bug:** order SRL9043592 crashed `/order-billing/` with `ValueError: time data '202-12-02' does not match format '%Y-%m-%d'`. User typed partial year `202` in MUI DatePicker → `getFullYear()===202` → `parseDateWithoutTimeZone()` emitted `'202-12-02'` (no year zero-padding) → backend `calculate_age()` `strptime` crash.
- **Root cause trigger:** commit `a73b575` (2026-02-23) added `_get_sorted_passengers()` which calls `calculate_age()` on every passenger — previously that code path was never hit, so malformed years went unnoticed.
- **FE fix** (`fix/birthdate-year-truncation` `3e71116`): `String(year).padStart(4,'0')` in `parseDateWithoutTimeZone()` · `helpers/getBillingAndOrder.js`.
- **BE fix** (`fix/birthdate-year-truncation` `ebbb044`): guard in `calculate_age()` — if year segment `< 4` chars, log warning + return `30` (Adult) instead of 500 · `bookings/services.py`.
- Both branches pushed + merged → develop + pushed. Deployed to production.

**Workspace:** frontend main→`3e71116` · backend main→`ebbb044` · admin main→`3d5a3a4` · content master→`3756e5b` · vault master→current

**Resume point (EXACT):**
1. **Monitor prod** — confirm no new `ValueError: time data` errors in `web_1` logs post-deploy.
2. **Deploy queue** — SEO r6-r10 + G8 + CS-CHAT-PERF still pending develop→main (see Section 2).
3. **r11 SEO backlog** — `/help/faqs` FAQPage (WP content), homepage TAT in schema, H5 author E-E-A-T, sameAs, llms.txt enrichment.

_(Session #172 archived → `07-logs/session-history.md`.)_

---

## Section 2 — Loose Ends (Open)

### Deploy Queue — merged → develop, needs main deploy + verify

| Item | What's pending | Where |
|------|----------------|-------|
| **SEO-R6-R9-DEPLOY** | **USER-OWNED deploy** (handoff 2026-06-26, develop `455b094`). ⚠️ develop→main carries **82 FE + 41 BE commits** (G8/P3/CS + BE migrations) — NOT SEO-only. SEO commits: r6 `87e3c15`, r7 `3fa482f`, r8 `961c645`, r9 `b5867c7`, faqpage-fix `bc538ef`, r7-coverage `1fafa5f` (skip build-unblock `3a7748a` — main has no OtaPdpaGate). **SEO-only option**: cherry-pick those 6 off main. Post-deploy prod-verify: `/help/<missing>`→404, `/destinations/koh-samui` no "undefined", `/manifest.json` lang=en, og:locale=en_US, `/activities` canonical, `sitemap-0.xml` 0×`/ref/article/`, blog single BlogPosting, `/about` TravelAgency+TAT, `/activities/detail/<slug>` FAQPage, 0 "Anonymous Traveler"; **re-check title double-brand on prod** (latent in code — /grill found prod mostly single-brand). | `smartenplus-frontend` develop→main (**user**) |
| **FULL-DEPLOY** | G8 (`feat/g8-ota-pdpa-gate`) already merged → develop. Deploy develop→main all 3 repos (BE first, no migrations for P3b/G2/G8). Verify: PDPA gate on `/my-trip`, OTA Bookings tab + Copy Link in prod, ticket cards visible after accept. | All 3 repos on develop |
| **CS-CHAT-PERF** | main deploy + seed `cs_chat` FeatureFlag row in prod DB. Storm mitigation (5-layer) built + merged all 3 repos 2026-06-23. | `hooks/useChatPolling.js`, `hooks/useFeatureFlag.js`, `cs/views.py`, `cs/models.py` · [[cs-guest-storm-investigation]] |
| **P2-OTA-SYNC** | run migrations on prod (`0003_csotabooking`, `0004_csotabooking_extra_fields`) + schedule Celery beat `cs.tasks.sync_ota_bookings`. 563 rows synced idempotent. | `cs/tasks.py`, `cs/supabase_client.py` · [[ota-sync-supabase-mirror]] |
| **ISR-REVALIDATE-GAP** | verify prod env vars set (`FRONTEND_URL=https://www.smartenplus.co.th`, non-empty `REVALIDATION_SECRET`) + worker recreated (stale worker = unregistered task). Smoke-test: admin contract edit → `/activities/detail` updates <60s. | `operators/signals.py`, `operators/tasks.py`, FE `pages/api/revalidate.js` · [[celery-unregistered-task-stale-worker]] |
| **TASK-1VCPU-MONITOR** | verify #139 prod incident resolved: CloudWatch CPU-credit stops draining, no `:00`/2 AM spike. | CloudWatch, `products/tasks.py` |

### Active

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **CS-GUEST-EMAIL-GATE** | Guest can type any email before OTP — no verification on conv creation. Risk LOW now (no booking data shown). MUST add OTP gate before Phase 4 OTA data shown to CS agents. | **OPEN — Phase 4 prereq** | `cs/views.py` `ConversationCreateView` |
| **CS-CENTRALIZATION** | RESCOPED 2026-06-23 → Unified Booking Command Centre. P0 chat + P1 direct + P2 OTA-sync SHIPPED (deploy pending). **P3a SHIPPED** (`/my-trip?token=`). **G2 SHIPPED** — admin OTA Bookings tab + Copy Link. **P3b SHIPPED** — BE `tickets[]` array + FE renders all ticket cards + admin-dashboard OTA-guarded ticket components. **G8 SHIPPED** — PDPA consent gate on `/my-trip` (once per token, localStorage, Thai PDPA compliant). All branches merged → develop or ready to merge. Remaining: G1 auto-email (P3c), G4 boarding feed, G5 expired-link. G8 consent done. | **deploy queue — merge G8 + deploy all** | [[ota-link-delivery-and-p3b-plan]] · [[ota-portal-overview]] · [[booking-command-centre-decision]] |
| **BE-HOMEPAGE-PRICE** | REC-engine `get_contract_price` (`services.py:74`), `RecommendationSerializer.get_lowest_price` (`serializers.py:~1105`), 6 finder `Min(selling_rate)` annotations — all still unfiltered. Homepage "From" price shipped #136, same-class bug remains. | **OPEN — REC-engine price bug** | `products/services.py`, `products/serializers.py:~1105` |
| **REC-SLOT-WASTE** | ESSENTIAL zone renders short (1 not 2) when cart item overlaps backend rec: FE excludes cart ids AFTER backend applied per-zone caps. Fix: API `exclude_ids` param threaded into finders before cap slice; cache key includes sorted exclude set. | OPEN #133 — deferred | `products/services.py` get_recommendations · [[recommendation-engine-completion-roadmap]] |
| **BE-IMAGE-DEDUP** | BE image-processing duplication (moderate). WebP resize/compress ~2-3× (`operators/utils.py`, `dialogue/utils.py`, `operators/admin.py`); upload validation copy-pasted across 5 files. Consolidate → one `core/image_utils.py`: `process_image_to_webp()` + `validate_upload()`. High blast radius, dedicated refactor session. | OPEN #126 | `operators/utils.py`, `dialogue/utils.py` |
| **SEO-P1-BACKLOG** | r6-r9 all DONE (develop). **r10a DONE 2026-06-26** (`fix/seo-r10a`→develop `153ea1f`): `availableLanguage ['English']`→`['en']` on trip routes (`useRouteSeo.js:76`); `BlogPosting` JSON-LD stripped from `components/trips/BlogPost.js` (entity mismatch on product pages). **r10b DONE 2026-06-26** (`fix/seo-r10b`→develop `50925b7`): 404 title `"Page Not Found - SmartEnPlus"`→`"Page Not Found"` (titleTemplate de-dup); `rate-review/[reviewSlug].js` adds `openGraph.url`. **NOT CODE (carry as ops):** aggregateRating guard already on real API data (no change); blog meta description handled in `BlogPostHeader.js` (no change); C2 destinations `notFound:true` already in code — ISR cache flush needed (ops). **Pending r11:** `/help/faqs` FAQPage (WP content), homepage TAT in schema, H5 author E-E-A-T, sameAs, llms.txt enrichment, Yoast @graph __NEXT_DATA__ bloat, polish. **All fixes develop-only — deploy→main then PM re-audits prod.** | **OPEN — deploy pending** | [[r6-external-reconciliation-2026-06-25]] · [[r7-code-review-2026-06-26]] · [[r8-live-prod-2026-06-26]] |
| **SEO-P2-FIXES** | twitter:image:alt (`_app.js` + `Seo.js`); og:locale policy unify; meta desc ≤155 chars; blog robots dup. From r6: help relative `og:image`→abs prefix (`pages/help/[...slug].js:89,109`); **lint** `structured-data-schema-patterns.md` item 7 `availableLanguage:["Thai","English"]` contradicts en-only policy → `["English"]`. `#15 og:url` CLOSED `0aa748c`. | OPEN — low | `pages/_app.js`, `components/FrontPage/Seo.js`, `utils/blog/seoHelper.js`, `03-knowledge/structured-data-schema-patterns.md` |
| **SEARCH-UI-POLISH** | Deferred nits from #138 (NOT regressions). SearchModeTabs ARIA (arrow-key nav, role=tabpanel); `seach-button` typo (also `TransportationSearch.js:248`); SearchDialog close icon red vs grey; comment inverts nav order; mobile tab-switch height jump. | OPEN #138 — low | `components/search/SearchModeTabs.js`, `SearchDialog.js`, `TabbedSearchPanel.js` |
| **DURATION-DAYS-CARDS** | Day-tour browse cards omit duration: LIST `ContractSerializer` doesn't expose `tour_duration_days`. Option B: add to list serializer fields. One-line, low risk (read-only int); needs BE deploy + ISR cache clear. | OPEN #130 — optional low | `operators/serializers.py` (ContractSerializer) · [[category-aware-duration-formatter]] |
| **CROSS-SELL-BD-INVENTORY** | BD creates Koh Lipe inventory to activate cross-sell. Needs: return route Koh Lipe→Hat Yai Airport, DAY_TOUR + SPA_WELLNESS contracts at Koh Lipe. All 4 FE surfaces live 2026-06-13. Sole open eng item: multi-item post-booking (`bookingContext.js:33`, Sprint 2). | BD action | [[cross-sell-integration-status-2026-06-13]] |

### Low-priority backlog

→ [[low-priority-backlog]] — 27 deferred nits (IMG-ALT-DEBUG-1, F11×2, RR-1, GSC-1, CMA-1, FAQ-1, AT-1/2, numbered 1/2/3/8/15, Nav, Explore, HD-2/3/6, GAP-3/5/6/7, SILAPHAT-DESC, BOOKING-24H, SORT-VOCAB, BE-GIT-DIVERGE).

---

**See also:** [[vault-protocol]] (API contract) · [[vault-guardrails]] (architecture) · [[session-history]] (#38+) · [[closed-items]] (resolved) · [[low-priority-backlog]] (deferred nits)
