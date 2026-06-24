# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-24 (session #164)

**Achieved this session (#164) — admin-dashboard command-centre UX + ticket lifecycle:**
- **Command-centre confirm dialog** — replaced inline resolve/reject chips with `ActionDialog`. All statuses show Review/View button. Terminal tickets read-only dialog. 6 commits on `feat/command-centre-confirm-dialog`.
- **Status filter fix** — backend `TicketViewSet.get_queryset` ignored `?request_status=` param. 1-line fix. Branch `fix/command-centre-status-filter` · `c6ab62d`.
- **Booking Ref column** — was showing ticket UUID (`79161858…`), now shows `content_object.slug` (`PSF9498724`). Commit `371d61d`.
- **View order button** — dialog now has "View order" → `/orders/[order_id]` for cancel/refund workflow. Backend: exposed `order_id` on `BookingItemSerializer` (tickets app). Commits `ae90d5f` (BE) · `2276449` (FE).
- **Ticket lifecycle auto-sync** — `resolved/rejected` on command-centre now atomically sets `ticket_status=Completed` + `is_resolved=True`. Backend branch `fix/ticket-status-sync-on-terminal` · `e7d2e03`.
- **Ticket editor locked on Completed** — `SelectAction` + action panels greyed (`pointer-events:none`). `request_status` chip in header. "Reopen ticket" button. Commit `8c2ee63`.
- 4-agent debate (UX/UI + BizDev + Frontend + Ops) — unanimous Option A for lifecycle design.

**Workspace:**
- `smartenplus-backend` `fix/ticket-status-sync-on-terminal` → `e7d2e03`
- `smartenplus-frontend` `develop` → `46e4550`
- `admin-dashboard` `feat/command-centre-confirm-dialog` → `8c2ee63`
- `smartenplus-content` `master` → `3756e5b`

**Resume point (EXACT):**
1. **OPEN PRs** — browser only (gh not installed): admin-dashboard `feat/command-centre-confirm-dialog` → develop; BE `fix/command-centre-status-filter` → develop; BE `fix/ticket-status-sync-on-terminal` → develop.
2. **DEPLOY develop→main** — Order: BE first (run migrations) → FE → admin-dashboard.
3. **SEED FeatureFlag** — `INSERT INTO cs_featureflag (name, enabled) VALUES ('cs_chat', true);`
4. **SCHEDULE Celery beat** — `cs.tasks.sync_ota_bookings` in Django admin beat schedule.
5. **Phase 2 OTA** — `CustomerTicketViewSet.create()` seam already marked. Add `CsOtaBooking` branch when contract ready.
6. *(Optional)* **UX-03** — rate-review 5-star default (P2).

_(Sessions #153-#163 archived → `07-logs/session-history.md`.)_

---

## Section 2 — Loose Ends (Open)

### Deploy Queue — merged → develop, needs main deploy + verify

| Item | What's pending | Where |
|------|----------------|-------|
| **CS-CHAT-PERF** | main deploy + seed `cs_chat` FeatureFlag row in prod DB. Storm mitigation (5-layer) built + merged all 3 repos 2026-06-23. | `hooks/useChatPolling.js`, `hooks/useFeatureFlag.js`, `cs/views.py`, `cs/models.py` · [[cs-guest-storm-investigation]] |
| **P2-OTA-SYNC** | run migrations on prod (`0003_csotabooking`, `0004_csotabooking_extra_fields`) + schedule Celery beat `cs.tasks.sync_ota_bookings`. 563 rows synced idempotent. | `cs/tasks.py`, `cs/supabase_client.py` · [[ota-sync-supabase-mirror]] |
| **ISR-REVALIDATE-GAP** | verify prod env vars set (`FRONTEND_URL=https://www.smartenplus.co.th`, non-empty `REVALIDATION_SECRET`) + worker recreated (stale worker = unregistered task). Smoke-test: admin contract edit → `/activities/detail` updates <60s. | `operators/signals.py`, `operators/tasks.py`, FE `pages/api/revalidate.js` · [[celery-unregistered-task-stale-worker]] |
| **TASK-1VCPU-MONITOR** | verify #139 prod incident resolved: CloudWatch CPU-credit stops draining, no `:00`/2 AM spike. | CloudWatch, `products/tasks.py` |

### Active

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **CS-GUEST-EMAIL-GATE** | Guest can type any email before OTP — no verification on conv creation. Risk LOW now (no booking data shown). MUST add OTP gate before Phase 4 OTA data shown to CS agents. | **OPEN — Phase 4 prereq** | `cs/views.py` `ConversationCreateView` |
| **CS-CENTRALIZATION** | RESCOPED 2026-06-23 → Unified Booking Command Centre. CS chat built (deploy pending). Phase 1 direct-slice = next build. P3 OTA outbound gated on contract check; Tier-3 marketing gated on P0. | **RESCOPED** | [[booking-command-centre-decision]] · [[cs-gap-debate-verdicts]] · [[cs-architecture-decision]] · [[cs-api-contract]] · [[cs-centralization-design-concept]] · [[supabase-ota-booking-store]] · [[cs-p0-measurement-protocol]] · [[smarten-customer-os-thesis]] |
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
