# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-30 (session #192 — CS dialog redesign + manual-test bug fixes)

**Achieved this session (#192):**
- ✅ **Redesigned command-centre ActionDialog** (admin `4af50b1`): tone-grouped zones (hero Resolve green / Reject red destructive / No Action Needed blue neutral / Awaiting OTA orange) + 2-step reused `ConfirmDialog` for terminal transitions (resolved/rejected/closed_no_action) w/ `resolution_note` (required reject/closed_no_action per BE `clean()`; optional resolved). Copy Email → utility row. `ConfirmDialog` +children/+confirmDisabled (backward-safe). Conformance-checked vs `cs-workflow-revised-2026-06-27` + audit.
- ✅ **Hid emergency toggle for direct bookings** (admin `1a3ef2a`) — OTA-only bypass.
- ✅ **Fixed `resolution_note` transmit bug** (admin `9ac7089`) — `updateRequestStatus` mutation dropped it (body `{request_status}` only) → ConfirmDialog note was cosmetic + `closed_no_action` unreachable via FE.
- ✅ **3-agent team** (FE-UI + admin-UI + BE/data) traced real components → click-by-click manual-test guide saved `[[cs-manual-test-flows-b7-e-2026-06-30]]`.
- ✅ **FE TicketStatusBanner shows submitted request** (FE `36aab76`) — `requested_value` was stored but never surfaced; customer now sees "Your request: …". Verified.
- ✅ **BE Account.get_full_name fix** (BE `f675ddc`) — `Account(AbstractBaseUser)` lacked `get_full_name()` → `cs/serializers.py:31` AttributeError → 500 on `/api/cs/conversations/list/` (Flow D chat inbox). Added `get_full_name`/`get_short_name` (Django convention).
- ✅ **Reassessed CS-Centralization** (Section 2 REASSESSMENT note): Tier-1 criticals verified LANDED on develop (master-state "BLOCKED until Tier-1" stale); `check_sla_breaches` NameError fixed; `cs_chat` fail-open (no seed); B-7 emergency bypass already works (`clean()` Blocker 3).
- ✅ **Manual test:** B-8 (cancellation→Canceled) PASSED + resolution_note fix validated; date-change status flow passed (date-apply = System A gap → follow-up); FE banner note verified.

**Workspace (#192):**
- vault: master — committed + pushed through session
- backend: develop (`f675ddc`) — **2 files uncommitted** (`cs/views.py`, `tickets/views.py` = #191 DRF error conversion)
- frontend: develop (`36aab76`) — `RequestChangeModal.js` uncommitted + `CS_CENTRALIZATION_MANUAL_TEST_GUIDE.md` untracked (#191)
- admin-dashboard: develop (`9ac7089`) — **clean**
- content: master (`3756e5b`) — clean

**Resume point (EXACT):**
1. **Commit #191 uncommitted** (BE `cs/views.py`+`tickets/views.py`; FE `RequestChangeModal.js`+test guide) on feature branches → develop. **Fix `NEXTAUTH_SECRET`** — admin `.env.local` = frontend value `548d665db327c717e607eed1cc7d12e6ec151bfec69b4cc218de9a9272fb5e7c`; restart admin + clear cookies.
2. **Restart BE + re-verify Flow D chat** — `Account.get_full_name` fix shipped (`f675ddc`); restart BE → admin chat inbox `/api/cs/conversations/list/` should 200 (no AttributeError). Complete Flow D (Chrome FAB → Safari inbox reply).
3. **Finish manual test:** Flow C (OTA `/my-trip` — targeted Django-shell `CsOtaBooking.update_or_create`, NOT destructive `seed_ota_fake_data`), Flow E (OTA sync — Celery worker or `manage.py sync_ota_bookings`), B-7 emergency bypass (needs OTA ticket in `awaiting_ota_update`).
4. **Follow-up features:** inline date-apply in command-centre (vault rec #2, `[[command-centre-ticket-booking-flow]]` — resolve is status-only; UpdateTrip redirect too many steps); FE-M1 `InfoUpdateNotice`; admin Phase 2-3.
5. **3 go-live blockers (product-owned):** NEW-1 resolve-block visibility, OQ-3 SLA (unbuilt), Emergency path (NEW-4 fast-track + NEW-10 manifest + `trip_id`).
6. **Deploy CS → main** (all 3 repos develop→main) once manual test + blockers clear. Run BE migrations `0005`–`0009` + Celery beat (already in `celery.py`).

_(Sessions #191 + #186 archived → `07-logs/session-history.md`.)_

---

## Section 2 — Loose Ends (Open)

> **REASSESSMENT 2026-06-30** — Tier-1 criticals FIXED on BE develop (`58872d5`, spot-verified #1/#3/#7/#8). Admin dialog redesign shipped (`4af50b1`). So the "BLOCKED until Tier-1 land" notes in Deploy Queue + CS-CENTRALIZATION row below are **STALE — Tier-1 landed**. Remaining for main deploy: **(A)** commit #191 uncommitted (BE `cs/views.py`+`tickets/views.py`, FE `RequestChangeModal.js`+test guide) + `NEXTAUTH_SECRET` fix; **(B)** finish manual test B-7/B-8/C/D/E (B-7b needs OTA seed); **(C)** Tier-2/3 + 3 workflow blockers (NEW-1 visibility, OQ-3 SLA unbuilt, Emergency partial); **(D)** admin Phase 2-3. Stale Tier-2 also resolved: `check_sla_breaches` NameError FIXED (`ticket_numbers` plural); `cs_chat` FeatureFlag fail-open True (`FeatureFlagView get_or_create defaults enabled=True`) → chat ON by default, no seed needed (kill-switch-inert only). **B-7 emergency bypass already works** (`tickets/models.py:119-123` clean() Blocker 3) — no FE fix. Full remaining-work map → `~/.claude/plans/check-vaault-and-continue-witty-lake.md`.


### Deploy Queue — merged → develop, needs main deploy + verify

| Item | What's pending | Where |
|------|----------------|-------|
| **CS-CENTRALIZATION-DEPLOY** | ⏳ **merged → develop 2026-06-28 (NOT yet main)** — BE `424f72a` · admin `69bde06` · FE `4c0df60`. **⚠️ BLOCKED — audit 2026-06-29 found 10 Tier-1 criticals. Fix before deploying to main.** When unblocked: deploy all 3 develop→main + run BE migrations `0005`-`0009` + schedule Celery beat `sync_ota_bookings` (15min) + `check_sla_breaches`. Priority fixes first: signals `ready()` (tickets/apps.py), beat schedule (celery.py), resend token (cs/views.py:595). | `tickets/apps.py`, `Smartenplus/celery.py`, `cs/views.py` · [[cs-centralization-audit-2026-06-29]] |
| **FULL-DEPLOY** | ✅ **DEPLOYED 2026-06-26** — all 3 repos develop→main. FE `43299da` · BE `ebbb044` · admin `3d5a3a4`. Includes G8, P3a/P3b, CS chat Steps 5-7, CS-CHAT-PERF, r12 SEO. | ✅ Done |
| **CS-CHAT-PERF** | ✅ **CODE DEPLOYED 2026-06-26**. ⚠️ Widget still hidden — must seed `cs_chat=True` FeatureFlag row in prod DB via Django admin or SQL to activate FAB. | `hooks/useChatPolling.js`, `hooks/useFeatureFlag.js`, `cs/views.py`, `cs/models.py` · [[cs-guest-storm-investigation]] |
| **P2-OTA-SYNC** | run migrations on prod (`0003_csotabooking`, `0004_csotabooking_extra_fields`) + schedule Celery beat `cs.tasks.sync_ota_bookings`. 563 rows synced idempotent. | `cs/tasks.py`, `cs/supabase_client.py` · [[ota-sync-supabase-mirror]] |
| **ISR-REVALIDATE-GAP** | verify prod env vars set (`FRONTEND_URL=https://www.smartenplus.co.th`, non-empty `REVALIDATION_SECRET`) + worker recreated (stale worker = unregistered task). Smoke-test: admin contract edit → `/activities/detail` updates <60s. | `operators/signals.py`, `operators/tasks.py`, FE `pages/api/revalidate.js` · [[celery-unregistered-task-stale-worker]] |
| **TASK-1VCPU-MONITOR** | verify #139 prod incident resolved: CloudWatch CPU-credit stops draining, no `:00`/2 AM spike. | CloudWatch, `products/tasks.py` |

### Active

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **CS-GUEST-EMAIL-GATE** | Guest can type any email before OTP — no verification on conv creation. Risk LOW now (no booking data shown). MUST add OTP gate before Phase 4 OTA data shown to CS agents. | **OPEN — Phase 4 prereq** | `cs/views.py` `ConversationCreateView` |
| **CS-CENTRALIZATION** | RESCOPED 2026-06-23 → Unified Booking Command Centre. P0 chat + P1 direct + P2 OTA-sync SHIPPED. **P3a/P3b/G2/G8 SHIPPED.** All branches merged → develop. **#186: CS-BE gaps + 4 critical fixes + admin/FE work all → develop** (BE `424f72a`, admin `69bde06`, FE `4c0df60`). **⚠️ AUDIT 2026-06-29: NOT PRODUCTION-READY — 10 Tier-1 criticals found (see [[cs-centralization-audit-2026-06-29]]). Must fix before deploy to main.** Remaining: Tier-1 #1–#10 (signals dead, beat absent, resend dead token, no one-open-ticket guard, magic-link TTL, resolution side-effect, trip_id missing, closed_no_action, OTP JWT, requested_value). Plus FE-M1 (InfoUpdateNotice). | **BLOCKED — do NOT deploy to main until Tier-1 fixes land** | [[cs-centralization-audit-2026-06-29]] · [[ota-link-delivery-and-p3b-plan]] · [[booking-command-centre-decision]] |
| **BE-HOMEPAGE-PRICE** | REC-engine `get_contract_price` (`services.py:74`), `RecommendationSerializer.get_lowest_price` (`serializers.py:~1105`), 6 finder `Min(selling_rate)` annotations — all still unfiltered. Homepage "From" price shipped #136, same-class bug remains. | **OPEN — REC-engine price bug** | `products/services.py`, `products/serializers.py:~1105` |
| **REC-SLOT-WASTE** | ESSENTIAL zone renders short (1 not 2) when cart item overlaps backend rec: FE excludes cart ids AFTER backend applied per-zone caps. Fix: API `exclude_ids` param threaded into finders before cap slice; cache key includes sorted exclude set. | OPEN #133 — deferred | `products/services.py` get_recommendations · [[recommendation-engine-completion-roadmap]] |
| **BE-IMAGE-DEDUP** | BE image-processing duplication (moderate). WebP resize/compress ~2-3× (`operators/utils.py`, `dialogue/utils.py`, `operators/admin.py`); upload validation copy-pasted across 5 files. Consolidate → one `core/image_utils.py`: `process_image_to_webp()` + `validate_upload()`. High blast radius, dedicated refactor session. | OPEN #126 | `operators/utils.py`, `dialogue/utils.py` |
| **SEO-P1-BACKLOG** | r6-r12 all DONE + prod-verified. **r13 open:** `/about` TravelAgency schema parity — missing `priceRange`, `openingHours`, `contactPoint`, `geo`, `image`, `logo` vs homepage (P1); `/about` missing BreadcrumbList+WebPage (P2); `og:locale th_TH` alternate (P2). `/help/faqs` FAQPage still ops-blocked (WP/GraphQL). | **r13 open** | [[r9-live-prod-2026-06-26]] · [[r10-live-prod-2026-06-26]] |
| **SEO-P2-FIXES** | twitter:image:alt (`_app.js` + `Seo.js`); og:locale policy unify; meta desc ≤155 chars; blog robots dup. From r6: help relative `og:image`→abs prefix (`pages/help/[...slug].js:89,109`); **lint** `structured-data-schema-patterns.md` item 7 `availableLanguage:["Thai","English"]` contradicts en-only policy → `["English"]`. `#15 og:url` CLOSED `0aa748c`. | OPEN — low | `pages/_app.js`, `components/FrontPage/Seo.js`, `utils/blog/seoHelper.js`, `03-knowledge/structured-data-schema-patterns.md` |
| **SEARCH-UI-POLISH** | Deferred nits from #138 (NOT regressions). SearchModeTabs ARIA (arrow-key nav, role=tabpanel); `seach-button` typo (also `TransportationSearch.js:248`); SearchDialog close icon red vs grey; comment inverts nav order; mobile tab-switch height jump. | OPEN #138 — low | `components/search/SearchModeTabs.js`, `SearchDialog.js`, `TabbedSearchPanel.js` |
| **DURATION-DAYS-CARDS** | Day-tour browse cards omit duration: LIST `ContractSerializer` doesn't expose `tour_duration_days`. Option B: add to list serializer fields. One-line, low risk (read-only int); needs BE deploy + ISR cache clear. | OPEN #130 — optional low | `operators/serializers.py` (ContractSerializer) · [[category-aware-duration-formatter]] |
| **CROSS-SELL-BD-INVENTORY** | BD creates Koh Lipe inventory to activate cross-sell. Needs: return route Koh Lipe→Hat Yai Airport, DAY_TOUR + SPA_WELLNESS contracts at Koh Lipe. All 4 FE surfaces live 2026-06-13. Sole open eng item: multi-item post-booking (`bookingContext.js:33`, Sprint 2). | BD action | [[cross-sell-integration-status-2026-06-13]] |
| **ADMIN-CS-CENTRALIZATION** | **Phase 1 + Phase 4 SHIPPED → develop `69bde06` (#186)** incl. API conformance fixes (resend `{booking_id,source}`, emergency toggle → `request-status/`). VALID_TRANSITIONS extended, SupabaseSyncBanner, SLA display, emergency toggle, resolution_note, admin_initiated, Resend Email all on develop. Phase 4 (CS Guide Thai+EN help + Mermaid + sidebar nav) committed + merged. **Phase 2-3 pending.** Admin buttons now backed by BE (BE-B2/B4 on develop). | **Phase 1+4 on develop (deploy pending) · Phase 2-3 pending** | [[admin-dashboard-cs-centralization-plan]] · [[cs-centralization-gap-report-2026-06-27]] |
| **CS-BE-GAPS** | ✅ **All 5 gaps closed + merged → develop `424f72a` (#186)** incl. resolve-block guard wired to API + emergency path + field-only PATCH. magic_token+supabase_row_id, POST ota/sync/, POST ota/resend-magic-link/, RequestStatusViewSet admin fields, OtaBookingEvent creation in sync task. 33 gap tests. **🟡 Remaining:** BE-B1 (add `magic_token_generated_at`/`auto_send_magic_link`/`is_magic_link_valid` — no link expiry), BE-B3 (resend doesn't regen token / send SES). | **on develop — deploy + 🟡 remaining** | [[cs-centralization-gap-report-2026-06-27]] |
| **CS-FE-OTA-GAPS** | ✅ **RESOLVED + fully → develop `4c0df60` (#186)** — FE-B1..B5 + stranded FE-B3 `OtaRequestCard` delete + `/my-trip` conditional-poll (parity w/ FE-B4). All FE CS work on develop. **Open follow-ups (non-blocking):** (a) no RTL/e2e tests; (b) hard-coded EN strings in `TicketStatusBanner` + `/my-trip` — no i18n; (c) no analytics events; (d) a11y gaps (SLAProgress opacity-only, status pill lacks `role="status"`/`aria-live`, emergency lacks `role="alert"`); (e) `CS_BLOCKERS_IMPLEMENTATION_PLAN.md` at repo root → move to `docs/features/`. | **RESOLVED · on develop** | [[cs-centralization-gap-report-2026-06-27]] |
| **PRODUCTS-LIVE-CATALOG-AUDIT** | **PHASE 1 FINAL 2026-06-28 · Public API Snapshot.** 1224 contracts · 176 stations · 7/10 service categories empty (TRANSFER · MULTI_DAY_TOUR · EVENT_TICKET · ATTRACTION_TICKET · FOOD_DINING · ACCOMMODATION · OTHER). Only 6 charter routes live (4 unique — Chiang Mai + Khao Lak only). SPA_WELLNESS = 100% Salisa Resort (single-operator risk). DAY_TOUR northern bias (5/5 ops in Chiang Rai/Chiang Mai/Hat Yai; Andaman islands absent). **10 BD gaps logged** (`business-development/products-live-catalog/gap-inventory.md`): gap-001 charter routes near-zero · gap-002 transfer empty · gap-003 MULTI_DAY_TOUR empty [Experiences lens 100% uncovered] · gap-004/005/006/007/010 service_categories empty · gap-008 day-tour geographic skew · gap-009 SPA concentration risk. **Django shell deferred (Phase 1.5)** — API filters `?is_actived=false`/`?end_date__gte=` silently ignored, no station FK IDs exposed via public API. **Next:** Phase 2 = `grill` skill × 10 gaps → BD-ready question docs. | **PHASE 1 FINAL · Phase 2 next** | [[products-live-catalog-audit]] · `business-development/products-live-catalog/snapshots-2026-06-28.md` |

### Low-priority backlog

→ [[low-priority-backlog]] — 27 deferred nits (IMG-ALT-DEBUG-1, F11×2, RR-1, GSC-1, CMA-1, FAQ-1, AT-1/2, numbered 1/2/3/8/15, Nav, Explore, HD-2/3/6, GAP-3/5/6/7, SILAPHAT-DESC, BOOKING-24H, SORT-VOCAB, BE-GIT-DIVERGE).

---

**See also:** [[vault-protocol]] (API contract) · [[vault-guardrails]] (architecture) · [[session-history]] (#38+) · [[closed-items]] (resolved) · [[low-priority-backlog]] (deferred nits)
