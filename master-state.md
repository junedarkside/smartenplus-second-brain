# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-24 (session #163)

**Achieved this session (#163) — vault optimization (vault-only, no code repos touched):**
- **Cost optimization** — master-state Section 2 pruned (79→62 lines: CLOSED #139 → closed-items, deploy-pending cluster consolidated, 27 low-pri nits → new [[low-priority-backlog]]); root `log.md` rotated (752→355 lines, 160 May entries → `07-logs/log-2026-05.md`); 9 atoms extracted from 6 over-cap notes + 7 deferred 2026-06-22 parent back-refs finished; fixed leaked skill-output corruption in experience-detail-page-redesign.
- **Orphan + stale cleanup** — revealed "71 orphans" was a `vault-stats.py` artifact (65 `.original.md` backups); wired 5 pattern orphans into index.md; fixed `r2-skeptic` alias (8 links via repair-script rule); archived 2 superseded trip-detail reviews; fixed `vault-stats.py` exclusions. **Orphans 71→0 (true), broken 37→34, date-prefix 50→1.**
- **Rate-review r1-ux verdict** — KEEP (archived + linked, not stray); full code verification **8/9 findings resolved**; **FE-22 = NOT a bug** (backend `ReviewViewSet.get_object` resolves by `booking_item__slug`, designed with frontend 2024-12-14); **UX-03 (P2, 5-star `useState(5)` default) confirmed still open**; overview status de-staled IN PROGRESS→COMPLETED.
- 4 vault commits: `da58b04` · `bdc3da2` · `9f1f0bc` · `d2b9968`.

**Workspace (unchanged — vault-only session):**
- `smartenplus-backend` `develop` → `6b10123`
- `smartenplus-frontend` `develop` → `46e4550`
- `admin-dashboard` `develop` → `036b55e`
- `smartenplus-content` `master` → `3756e5b`

**Resume point (EXACT):**
1. **DEPLOY develop→main** — user handles. Order: BE first (run migrations) → FE → admin-dashboard.
2. **SEED FeatureFlag** — `INSERT INTO cs_featureflag (name, enabled) VALUES ('cs_chat', true);`
3. **SCHEDULE Celery beat** — `cs.tasks.sync_ota_bookings` in Django admin beat schedule.
4. **Phase 2 OTA** — `CustomerTicketViewSet.create()` seam already marked. Add `CsOtaBooking` branch when contract ready.
5. **Phase 3 OTA portal** — gated on 12Go/Klook contract check.
6. *(Optional)* **UX-03** — rate-review 5-star default (P2): force explicit selection (`useState(0)` + `rating===0` submit gate + "Tap to rate" helper). Frontend branch task — fix or accept.

_(Sessions #153-#162 archived → `07-logs/session-history.md`.)_

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
