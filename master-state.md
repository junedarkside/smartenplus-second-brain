# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-26 (session #170)

**Achieved (#170) — SEO/AEO/GEO audit reconciliation + r6-r9 fixes (LOCAL/dev-verified, NOT prod-deployed):**
- **r6 reconcile**: 3-specialist team reconciled external Hermes audit (`~/Desktop/SmartEnPlus/seo/seo-aeo-geo-audit-smartenplus.md`) vs live code + vault r1-r5. ~70% findings real bugs, ~50% wrong root-cause/fix (audit assumed App Router; repo is Pages Router). Caught `/operators` canonical false-positive. Vault: `01-projects/seo-aeo-geo-live-audit-2026-06-22/r6-external-reconciliation-2026-06-25.md` + project README (was missing) + r3-synthesis correction banner.
- **r6** (`fix/seo-r6`→develop `5bdcec1`): `help/[...slug]` 500→404 (notFound), destinations `arrivalStation` fallback (kills "undefined"), manifest Thai→EN, `availableLanguage` `["en","th"]`→`["en"]`, `/activities` NextSeo+canonical, help absolute og:image.
- **Build unblock** (`fix/ota-gate-unescaped-quote`→develop `3589c6a`): pre-existing `OtaPdpaGate.js` apostrophe blocked `next build` (not SEO).
- **r7** (`fix/seo-r7`→develop `5156f2e`): sitemap `/ref/article/*` excluded (41 dead URLs), Yoast `@graph` dropped from `BlogPostSchemaGenerator` (BlogPosting 2→1, 0 bad-domain refs), og:locale th_TH→en_US 6 files.
- **r8** (`fix/seo-r8`→develop `6a7e9a1`): synthetic reviews removed (filter real comment+author; 0 "Anonymous Traveler"), About TravelAgency JSON-LD + shared `@id` merge with homepage + TAT license `11/06622`.
- **r9** (`fix/seo-r9`→develop `63fd2b5`): FAQPage wiring — `FilterTripsSEO` renders `FaqJsonLd` (SSR faqMainEntity); activity detail `generateFAQSchema({contract})` → `DayTripDetailSEO`.
- **Verified on live**: help canonical collapse + P0-A AI crawlers already-done.

**⚠️ Report = LIVE PROD; fixes = LOCAL (develop, not main/prod). Deploy + prod-verify required — see SEO-R6-R9-DEPLOY (Section 2).**

**Workspace:** frontend develop→`63fd2b5` · backend develop→`f6eaf42` (unchanged) · admin develop→`3d5a3a4` (unchanged) · content master→`3756e5b` (unchanged) · vault master→`1c1763a`

**Resume point (EXACT):**
1. **DEPLOY r6-r9 → main/prod** (FE only; no BE/migrations) + post-deploy prod-verify (SEO-R6-R9-DEPLOY checklist).
2. **Destinations root cause** (split out): ISR cache flush + backend deleted-station cleanup + koh-samui prod mystery (API-good, page-undefined).
3. **Remaining SEO** (backend/content): C1-B server-sitemap deleted-entity filtering, M3 `/help/faqs` FAQ (WP), homepage FAQPage (content), H4 meta desc, H5 author page, H6 internal links, polish (apple-touch-icon/security.txt/llms.txt creds).

_(Sessions #165-#169 archived → `07-logs/session-history.md`.)_

---

## Section 2 — Loose Ends (Open)

### Deploy Queue — merged → develop, needs main deploy + verify

| Item | What's pending | Where |
|------|----------------|-------|
| **SEO-R6-R9-DEPLOY** | Deploy FE develop→main (`5bdcec1`, `3589c6a`, `5156f2e`, `6a7e9a1`, `63fd2b5`). No BE/migrations. Report was PROD; fixes dev-verified only. Post-deploy prod-verify: `/help/<missing>`→404; `/destinations/koh-samui` no "undefined" (needs ISR flush/redeploy); `/manifest.json` lang=en; `/` availableLanguage=`["en"]`; og:locale=en_US; `/activities` canonical; `sitemap-0.xml` 0×`/ref/article/`; blog single BlogPosting + 0 `blog.smartenplus.co.th`; `/about` TravelAgency + TAT; `/activities/detail/<slug>` FAQPage; 0 "Anonymous Traveler". | `smartenplus-frontend` develop→main |
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
| **SEO-P1-BACKLOG** | **P0-A DONE** — live robots.txt 2026-06-25 shows 11 AI UAs `Allow: /` (CF toggle off + explicit allowlist landed). **r7 DONE 2026-06-26** (`fix/seo-r7`→develop `5156f2e`): sitemap `/ref/article/*` excluded (41 dead URLs gone from sitemap-0); Yoast `@graph` dropped from `BlogPostSchemaGenerator.js` (BlogPosting 2→1, 0 `blog.smartenplus.co.th` in JSON-LD, verified clean recompile); og:locale `th_TH→en_US` 6 files. **r8 DONE 2026-06-26** (`fix/seo-r8`→develop `6a7e9a1`): synthetic reviews removed (`ReviewsStructuredData.js` filter → 0 "Anonymous Traveler"/"Great travel experience" on /, aggregateRating kept as real API data); About TravelAgency JSON-LD added + merged with homepage via shared `@id …/#organization` + TAT license `11/06622` as identifier; help canonical collapse confirmed already-fixed (live www canonical + og:url=/help). **r9 DONE 2026-06-26** (`fix/seo-r9`→develop `63fd2b5`): FAQPage wired — `FilterTripsSEO` renders `FaqJsonLd` from SSR `faqMainEntity`; activity detail calls `generateFAQSchema({contract})` in getStaticProps → `DayTripDetailSEO`. Full render-verify pending deploy (local dev has no backend; test route has no FAQs). Net-new from r6 reconcile: (1) `help/[...slug].js` getServerSideProps `notFound` — 53×500→404 (`pages/help/[...slug].js:311-352`); (2) `destinations/[slug].js:172` **fallback landed `fix/seo-r6`** (stops "undefined"); ROOT CAUSE = ISR stale cache + deleted backend stations (koh-lipe/bangkok API 404) + koh-samui prod mystery (API-good, page-undefined) — NOT a missing field. **Still open: ISR rebuild + backend deleted-station cleanup + koh-samui investigation.** (3) `public/manifest.json` Thai→EN (`lang:"th"`); (4) `availableLanguage:["en","th"]`→`["en"]` (`homepagev2.js:244`); (5) `/activities` NextSeo+canonical (`pages/activities/index.js:27-45`, apex fallback `:36`). Carried: ~~FAQPage activity detail + FilterTripsSEO faqMainEntity~~ DONE r9; ~~og:locale th_TH→en_US 6 files~~ DONE r7; ~~TravelAgency schema on About~~ DONE r8; ~~help canonical collapse~~ DONE (verified live www + og:url=/help). **REJECTED (r6 false-positive): `/operators` canonical — already present `operators/index.js:26`, do NOT add.** | **OPEN — SEO P1** | full scorecard: [[r6-external-reconciliation-2026-06-25]] |
| **SEO-P2-FIXES** | twitter:image:alt (`_app.js` + `Seo.js`); og:locale policy unify; meta desc ≤155 chars; blog robots dup. From r6: help relative `og:image`→abs prefix (`pages/help/[...slug].js:89,109`); **lint** `structured-data-schema-patterns.md` item 7 `availableLanguage:["Thai","English"]` contradicts en-only policy → `["English"]`. `#15 og:url` CLOSED `0aa748c`. | OPEN — low | `pages/_app.js`, `components/FrontPage/Seo.js`, `utils/blog/seoHelper.js`, `03-knowledge/structured-data-schema-patterns.md` |
| **SEARCH-UI-POLISH** | Deferred nits from #138 (NOT regressions). SearchModeTabs ARIA (arrow-key nav, role=tabpanel); `seach-button` typo (also `TransportationSearch.js:248`); SearchDialog close icon red vs grey; comment inverts nav order; mobile tab-switch height jump. | OPEN #138 — low | `components/search/SearchModeTabs.js`, `SearchDialog.js`, `TabbedSearchPanel.js` |
| **DURATION-DAYS-CARDS** | Day-tour browse cards omit duration: LIST `ContractSerializer` doesn't expose `tour_duration_days`. Option B: add to list serializer fields. One-line, low risk (read-only int); needs BE deploy + ISR cache clear. | OPEN #130 — optional low | `operators/serializers.py` (ContractSerializer) · [[category-aware-duration-formatter]] |
| **CROSS-SELL-BD-INVENTORY** | BD creates Koh Lipe inventory to activate cross-sell. Needs: return route Koh Lipe→Hat Yai Airport, DAY_TOUR + SPA_WELLNESS contracts at Koh Lipe. All 4 FE surfaces live 2026-06-13. Sole open eng item: multi-item post-booking (`bookingContext.js:33`, Sprint 2). | BD action | [[cross-sell-integration-status-2026-06-13]] |

### Low-priority backlog

→ [[low-priority-backlog]] — 27 deferred nits (IMG-ALT-DEBUG-1, F11×2, RR-1, GSC-1, CMA-1, FAQ-1, AT-1/2, numbered 1/2/3/8/15, Nav, Explore, HD-2/3/6, GAP-3/5/6/7, SILAPHAT-DESC, BOOKING-24H, SORT-VOCAB, BE-GIT-DIVERGE).

---

**See also:** [[vault-protocol]] (API contract) · [[vault-guardrails]] (architecture) · [[session-history]] (#38+) · [[closed-items]] (resolved) · [[low-priority-backlog]] (deferred nits)
