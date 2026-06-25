# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-25 (session #169)

**Achieved this session (#169) — G8 OTA PDPA consent gate:**
- **Debate**: 4-agent team (uxui/design/bd/frontend) debated G8 consent + OTA CS service access. Grill audit confirmed: chat widget already on `/my-trip` (`_app.js:88`); HMAC bypass not built yet; 1.5-day estimate low (2–3 days realistic); passive disclosure insufficient for Thai PDPA.
- **Decision**: OTA user must accept PDPA before ANY trip content shown. Consent stored once per token in localStorage. Covers service features only (trip view, requests, CS chat). Marketing requires separate consent + contract gate.
- **FE `feat/g8-ota-pdpa-gate`**: 3 files — `helpers/otaConsent.js` (localStorage read/write, SSR-safe), `components/bookings/OtaPdpaGate.js` (full-screen PDPA notice: controller, purpose, retention, rights, withdraw), `pages/my-trip/index.js` (early-return gate + `consentChecked` flag prevents flash-of-gate on return visits). `79bdd43` + `d0d2069`. Branch ready to merge → develop.

**Achieved this session (#167) — G2 admin copy-link SHIPPED:**
- **G2 SHIPPED** — admin-dashboard command-centre OTA Bookings tab + Copy Link button. BE `f714ba8`. Admin-dashboard `f7cc7ee`.

**Achieved this session (#166) — P3a OTA trip view SHIPPED + gap audit + next plan:**
- **Shipped P3 prereqs + P3a** (BE `feat/p3-prereq-ticket-guest-ota-trip` → develop `df13268`; FE `feat/p3a-ota-trip-view` → develop `9a99ab6`): `Ticket.guest_email`+nullable `created_by` (migration `0005`); `cs/tokens.py` parametrized + `make/load_ota_trip_token`; `OtaTripView` GET `/api/cs/ota/trip/`; FE `otaApi.js` slice + `/my-trip?token=` page (status-only, full UX pass, design-system tokens).
- **Fixed** missing `/api/` prefix on otaApi endpoint (was 500 in browser).
- **Big-view gap audit** (OTA-user + BD role-play): P3a = "window, no door". 7 gaps found; G1 (no link delivery) + G2 (no admin copy-link button) = blockers for real use. G2 designed nowhere.
- **Created** [[ota-link-delivery-and-p3b-plan]]: Phase 1 admin copy-link (ungated keystone) → Phase 2 P3b request-submit (prereqs cleared). Updated [[ota-portal-overview]] gap table + phase status.

---

**Updated:** 2026-06-24 (session #165)

**Achieved this session (#165) — CS-centralization vault audit + P1 status correction:**
- **Vault audit** — asked "what's left for CS-centralization." Initial draft of `p1-direct-slice-impl-plan.md` framed P1 as future work. **Two `/scrutinize` passes vs live code proved P1 already SHIPPED in #164** (migration `0004`, `CustomerTicketViewSet`/`RequestStatusViewSet`, wired `RequestChangeModal`+`ChangeRequestsSection`, admin command-centre queue).
- **Corrected** `p1-direct-slice-impl-plan.md` → now a STATUS NOTE (`status: shipped`) with file:line evidence + real open items (SES notify=P4, reopen guard=P4, nullable FK=P3 — none block P1).
- **Corrected** resume point #5 (was "build P1, start BE migrations" → would rebuild shipped code).
- **No code written** — vault-only session.

**Previous session (#164) — admin-dashboard command-centre UX + ticket lifecycle:**
- Command-centre confirm dialog, status filter fix, Booking Ref column, View order button, ticket lifecycle auto-sync, ticket editor locked on Completed. 6 commits.

**Workspace:**
- `smartenplus-backend` `fix/ticket-status-sync-on-terminal` → `e7d2e03`
- `smartenplus-frontend` `develop` → `46e4550`
- `admin-dashboard` `feat/command-centre-confirm-dialog` → `8c2ee63`
- `smartenplus-content` `master` → `3756e5b`

**Resume point (EXACT):**
1. **MERGE G8 branch**: `feat/g8-ota-pdpa-gate` → develop (FE only, no BE changes).
2. **VERIFY /my-trip end-to-end**: restart Django, hard-reload `/my-trip?token=...` → PDPA gate first visit → accept → both ticket cards visible (Cancellation/Approved + Other/Pending).
3. **DEPLOY develop→main** — Order: BE first → FE → admin-dashboard. No migrations needed for P3b/G2/G8.
4. **SEED FeatureFlag** — `INSERT INTO cs_featureflag (name, enabled) VALUES ('cs_chat', true);` in prod DB.
5. **RUN P2 migrations** — `0003_csotabooking` + `0004_csotabooking_extra_fields` on prod.
6. **SCHEDULE Celery beat** — `cs.tasks.sync_ota_bookings` in Django admin beat schedule.

_(Sessions #153-#163 archived → `07-logs/session-history.md`.)_

---

## Section 2 — Loose Ends (Open)

### Deploy Queue — merged → develop, needs main deploy + verify

| Item | What's pending | Where |
|------|----------------|-------|
| **FULL-DEPLOY** | Merge FE `feat/g8-ota-pdpa-gate` → develop. Then deploy develop→main all 3 repos (BE first, no migrations for P3b/G2/G8). Verify: PDPA gate on `/my-trip`, OTA Bookings tab + Copy Link in prod, ticket cards visible after accept. | All 3 repos on develop |
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
| **SEO-P1-BACKLOG** | **P0-A DONE** — live robots.txt 2026-06-25 shows 11 AI UAs `Allow: /` (CF toggle off + explicit allowlist landed). **r7 DONE 2026-06-26** (`fix/seo-r7`→develop `5156f2e`): sitemap `/ref/article/*` excluded (41 dead URLs gone from sitemap-0); Yoast `@graph` dropped from `BlogPostSchemaGenerator.js` (BlogPosting 2→1, 0 `blog.smartenplus.co.th` in JSON-LD, verified clean recompile); og:locale `th_TH→en_US` 6 files. Net-new from r6 reconcile: (1) `help/[...slug].js` getServerSideProps `notFound` — 53×500→404 (`pages/help/[...slug].js:311-352`); (2) `destinations/[slug].js:172` **fallback landed `fix/seo-r6`** (stops "undefined"); ROOT CAUSE = ISR stale cache + deleted backend stations (koh-lipe/bangkok API 404) + koh-samui prod mystery (API-good, page-undefined) — NOT a missing field. **Still open: ISR rebuild + backend deleted-station cleanup + koh-samui investigation.** (3) `public/manifest.json` Thai→EN (`lang:"th"`); (4) `availableLanguage:["en","th"]`→`["en"]` (`homepagev2.js:244`); (5) `/activities` NextSeo+canonical (`pages/activities/index.js:27-45`, apex fallback `:36`). Carried: FAQPage activity detail; `FilterTripsSEO.js:41-55` faqMainEntity; ~~og:locale th_TH→en_US 6 files~~ DONE r7; TravelAgency schema on About; `help/[...slug].js:82` canonical collapse. **REJECTED (r6 false-positive): `/operators` canonical — already present `operators/index.js:26`, do NOT add.** | **OPEN — SEO P1** | full scorecard: [[r6-external-reconciliation-2026-06-25]] |
| **SEO-P2-FIXES** | twitter:image:alt (`_app.js` + `Seo.js`); og:locale policy unify; meta desc ≤155 chars; blog robots dup. From r6: help relative `og:image`→abs prefix (`pages/help/[...slug].js:89,109`); **lint** `structured-data-schema-patterns.md` item 7 `availableLanguage:["Thai","English"]` contradicts en-only policy → `["English"]`. `#15 og:url` CLOSED `0aa748c`. | OPEN — low | `pages/_app.js`, `components/FrontPage/Seo.js`, `utils/blog/seoHelper.js`, `03-knowledge/structured-data-schema-patterns.md` |
| **SEARCH-UI-POLISH** | Deferred nits from #138 (NOT regressions). SearchModeTabs ARIA (arrow-key nav, role=tabpanel); `seach-button` typo (also `TransportationSearch.js:248`); SearchDialog close icon red vs grey; comment inverts nav order; mobile tab-switch height jump. | OPEN #138 — low | `components/search/SearchModeTabs.js`, `SearchDialog.js`, `TabbedSearchPanel.js` |
| **DURATION-DAYS-CARDS** | Day-tour browse cards omit duration: LIST `ContractSerializer` doesn't expose `tour_duration_days`. Option B: add to list serializer fields. One-line, low risk (read-only int); needs BE deploy + ISR cache clear. | OPEN #130 — optional low | `operators/serializers.py` (ContractSerializer) · [[category-aware-duration-formatter]] |
| **CROSS-SELL-BD-INVENTORY** | BD creates Koh Lipe inventory to activate cross-sell. Needs: return route Koh Lipe→Hat Yai Airport, DAY_TOUR + SPA_WELLNESS contracts at Koh Lipe. All 4 FE surfaces live 2026-06-13. Sole open eng item: multi-item post-booking (`bookingContext.js:33`, Sprint 2). | BD action | [[cross-sell-integration-status-2026-06-13]] |

### Low-priority backlog

→ [[low-priority-backlog]] — 27 deferred nits (IMG-ALT-DEBUG-1, F11×2, RR-1, GSC-1, CMA-1, FAQ-1, AT-1/2, numbered 1/2/3/8/15, Nav, Explore, HD-2/3/6, GAP-3/5/6/7, SILAPHAT-DESC, BOOKING-24H, SORT-VOCAB, BE-GIT-DIVERGE).

---

**See also:** [[vault-protocol]] (API contract) · [[vault-guardrails]] (architecture) · [[session-history]] (#38+) · [[closed-items]] (resolved) · [[low-priority-backlog]] (deferred nits)
