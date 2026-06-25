# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-25 (session #168)

**Achieved this session (#168) — P3b OTA ticket flow: debug + fix /my-trip ticket display:**
- **Root cause found + fixed**: `OtaTripView.get()` was returning no `ticket` field — two Django servers running (old process answering requests). Fixed server state + added ticket lookup code.
- **BE**: `OtaTripView` now returns `tickets[]` array (all tickets for booking, newest first) — `fix/ota-trip-tickets-list` → `f8e1f4b`.
- **FE**: `/my-trip` consumes `tickets[]`, renders all `OtaRequestCard`s stacked, shows form only when no tickets exist — `fix/my-trip-tickets-list` → `d18941e`.
- **FE**: `submitOtaRequest` mutation gets `invalidatesTags: ['OtaTrip']` so card appears immediately after submit without manual refresh.
- **Debug tooling**: added + removed `print` (BE) + `console.log` (FE) debug logs to trace exact data flow.
- **Sort bug debugged**: two tickets had different timestamps (not a tie) — `other/pending` was genuinely newer than `cancellation/resolved`. Fixed by returning all tickets, not just latest.
- **admin-dashboard ticket components**: CancelBooking, UpdatePassenger, UpdateTrip all OTA-guarded; ticket detail has back button, Guest Request card, Resolution row, auto-seeded action dropdown, locked-state banner.

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
1. **MERGE P3b branches → develop**: BE `fix/ota-trip-tickets-list` + FE `fix/my-trip-tickets-list` + admin-dashboard OTA ticket component changes (currently on `develop` directly — audit and clean).
2. **VERIFY /my-trip end-to-end**: restart Django, hard-reload page → both ticket cards visible (Cancellation/Approved + Other/Pending).
3. **DEPLOY develop→main** — Order: BE first (no new migrations) → FE → admin-dashboard.
4. **SEED FeatureFlag** — `INSERT INTO cs_featureflag (name, enabled) VALUES ('cs_chat', true);`
5. **SCHEDULE Celery beat** — `cs.tasks.sync_ota_bookings` in Django admin beat schedule.
6. *(Optional)* **UX-03** — rate-review 5-star default (P2).

_(Sessions #153-#163 archived → `07-logs/session-history.md`.)_

---

## Section 2 — Loose Ends (Open)

### Deploy Queue — merged → develop, needs main deploy + verify

| Item | What's pending | Where |
|------|----------------|-------|
| **G2-OTA-COPY-LINK** | Deploy BE `develop` (no migrations — views/urls only) + admin-dashboard `develop`. Verify: OTA Bookings tab visible, Copy Link returns `https://www.smartenplus.co.th/my-trip?token=...` in prod. | BE `cs/views.py`, `cs/urls.py` · admin-dashboard `command-centre/index.js`, `csApi.js` |
| **CS-CHAT-PERF** | main deploy + seed `cs_chat` FeatureFlag row in prod DB. Storm mitigation (5-layer) built + merged all 3 repos 2026-06-23. | `hooks/useChatPolling.js`, `hooks/useFeatureFlag.js`, `cs/views.py`, `cs/models.py` · [[cs-guest-storm-investigation]] |
| **P2-OTA-SYNC** | run migrations on prod (`0003_csotabooking`, `0004_csotabooking_extra_fields`) + schedule Celery beat `cs.tasks.sync_ota_bookings`. 563 rows synced idempotent. | `cs/tasks.py`, `cs/supabase_client.py` · [[ota-sync-supabase-mirror]] |
| **ISR-REVALIDATE-GAP** | verify prod env vars set (`FRONTEND_URL=https://www.smartenplus.co.th`, non-empty `REVALIDATION_SECRET`) + worker recreated (stale worker = unregistered task). Smoke-test: admin contract edit → `/activities/detail` updates <60s. | `operators/signals.py`, `operators/tasks.py`, FE `pages/api/revalidate.js` · [[celery-unregistered-task-stale-worker]] |
| **TASK-1VCPU-MONITOR** | verify #139 prod incident resolved: CloudWatch CPU-credit stops draining, no `:00`/2 AM spike. | CloudWatch, `products/tasks.py` |

### Active

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **CS-GUEST-EMAIL-GATE** | Guest can type any email before OTP — no verification on conv creation. Risk LOW now (no booking data shown). MUST add OTP gate before Phase 4 OTA data shown to CS agents. | **OPEN — Phase 4 prereq** | `cs/views.py` `ConversationCreateView` |
| **CS-CENTRALIZATION** | RESCOPED 2026-06-23 → Unified Booking Command Centre. P0 chat + P1 direct + P2 OTA-sync SHIPPED (deploy pending). **P3a SHIPPED** (`/my-trip?token=`). **G2 SHIPPED** — admin OTA Bookings tab + Copy Link. **P3b IN PROGRESS 2026-06-25**: admin-dashboard ticket components OTA-guarded (CancelBooking/UpdatePassenger/UpdateTrip); ticket detail back button + Guest Request card + Resolution row + locked banner; BE `OtaTripView` returns `tickets[]`; FE `/my-trip` renders all ticket cards. Branches pushed, pending merge → develop. Remaining: G1 auto-email (P3c), G4 boarding feed, G5 expired-link, G8 consent. | **P3b in-progress — merge + verify** | [[ota-link-delivery-and-p3b-plan]] · [[ota-portal-overview]] · [[booking-command-centre-decision]] |
| **BE-HOMEPAGE-PRICE** | REC-engine `get_contract_price` (`services.py:74`), `RecommendationSerializer.get_lowest_price` (`serializers.py:~1105`), 6 finder `Min(selling_rate)` annotations — all still unfiltered. Homepage "From" price shipped #136, same-class bug remains. | **OPEN — REC-engine price bug** | `products/services.py`, `products/serializers.py:~1105` |
| **REC-SLOT-WASTE** | ESSENTIAL zone renders short (1 not 2) when cart item overlaps backend rec: FE excludes cart ids AFTER backend applied per-zone caps. Fix: API `exclude_ids` param threaded into finders before cap slice; cache key includes sorted exclude set. | OPEN #133 — deferred | `products/services.py` get_recommendations · [[recommendation-engine-completion-roadmap]] |
| **BE-IMAGE-DEDUP** | BE image-processing duplication (moderate). WebP resize/compress ~2-3× (`operators/utils.py`, `dialogue/utils.py`, `operators/admin.py`); upload validation copy-pasted across 5 files. Consolidate → one `core/image_utils.py`: `process_image_to_webp()` + `validate_upload()`. High blast radius, dedicated refactor session. | OPEN #126 | `operators/utils.py`, `dialogue/utils.py` |
| **SEO-P1-BACKLOG** | P0 shipped `6390887`. Follow-ups: OAI-SearchBot in `next-sitemap.config.js` + delete stale `public/robots.txt`; FAQPage on activity detail; `FilterTripsSEO.js:41-55` faqMainEntity; og:locale `th_TH→en_US` in 6 files; TravelAgency schema on About; `help/[...slug].js:82` canonical collapse. | **OPEN — SEO P1** | `next-sitemap.config.js`, `DayTripDetailSEO.js`, `FilterTripsSEO.js` |
| **SEO-P2-FIXES** | twitter:image:alt (`_app.js` + `Seo.js`); og:locale policy unify; meta desc ≤155 chars; blog robots dup. `#15 og:url` CLOSED `0aa748c`. | OPEN — low | `pages/_app.js`, `components/FrontPage/Seo.js`, `utils/blog/seoHelper.js` |
| **SEARCH-UI-POLISH** | Deferred nits from #138 (NOT regressions). SearchModeTabs ARIA (arrow-key nav, role=tabpanel); `seach-button` typo (also `TransportationSearch.js:248`); SearchDialog close icon red vs grey; comment inverts nav order; mobile tab-switch height jump. | OPEN #138 — low | `components/search/SearchModeTabs.js`, `SearchDialog.js`, `TabbedSearchPanel.js` |
| **DURATION-DAYS-CARDS** | Day-tour browse cards omit duration: LIST `ContractSerializer` doesn't expose `tour_duration_days`. Option B: add to list serializer fields. One-line, low risk (read-only int); needs BE deploy + ISR cache clear. | OPEN #130 — optional low | `operators/serializers.py` (ContractSerializer) · [[category-aware-duration-formatter]] |
| **CROSS-SELL-BD-INVENTORY** | BD creates Koh Lipe inventory to activate cross-sell. Needs: return route Koh Lipe→Hat Yai Airport, DAY_TOUR + SPA_WELLNESS contracts at Koh Lipe. All 4 FE surfaces live 2026-06-13. Sole open eng item: multi-item post-booking (`bookingContext.js:33`, Sprint 2). | BD action | [[cross-sell-integration-status-2026-06-13]] |

### Low-priority backlog

→ [[low-priority-backlog]] — 27 deferred nits (IMG-ALT-DEBUG-1, F11×2, RR-1, GSC-1, CMA-1, FAQ-1, AT-1/2, numbered 1/2/3/8/15, Nav, Explore, HD-2/3/6, GAP-3/5/6/7, SILAPHAT-DESC, BOOKING-24H, SORT-VOCAB, BE-GIT-DIVERGE).

---

**See also:** [[vault-protocol]] (API contract) · [[vault-guardrails]] (architecture) · [[session-history]] (#38+) · [[closed-items]] (resolved) · [[low-priority-backlog]] (deferred nits)
