# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-30 (session #198 — Path A ✅ + admin/FE UX fixes)

**Achieved this session (#198):**
- ✅ **BE fix** — `POST /api/cs/ota/change-request/` 400 on blank description. `cs/views.py:588`. BE `259c0d8`.
- ✅ **Admin: `awaiting_ota_update` orange → grey + View Order hidden for OTA** — `06dc0ff`.
- ✅ **Admin: "Processing with OTA" → "Mark In Review"** — unified label, dead ternary removed. `7b73650`.
- ✅ **Admin: Thai button guide** — `extraContent` table in OTA dialog (ความหมายของปุ่ม). `830cfec`.
- ✅ **FE: OTA banner shows correct provider name** — `TicketStatusBanner` `source` prop → "We've contacted 12Go" not hardcoded "Klook/12Go". FE `80714750`.
- ✅ **Manual tests C1–C5 PASS**, **B7-4 PASS**, **Path A (TEST-12GO-0004 + 0007) PASS** — full cancellation E2E confirmed. `booking_status=canceled`, ticket `resolved`, sync event guard working.
- ⏳ **UX gap (not fixed)** — `my-trip:238` hides ticket section when `booking.status=canceled` → customer misses "Cancellation Confirmed" banner.
- ⏳ **Remaining tests** — C6 (poll 60s), C8 (bad token), B7-5 (emergency bypass), Flow E (idempotent sync).
- ⏳ **Bug 4 deferred** — `OtaTripView` missing SLA fields in ticket serialization.

**Workspace (#198):**
- vault: master — updating now
- backend: develop (`259c0d8`) — clean
- frontend: develop (`80714750`) — clean, OTA source label fix merged
- admin-dashboard: develop (`830cfec`) — clean, Thai guide + label fixes merged
- content: master (`3756e5b`) — clean

**Resume point (EXACT):**
1. **Remaining manual tests**:
   - C6: DevTools Network → poll fires every 60s while ticket open
   - C8: `http://localhost:3000/my-trip?token=invalid` → error state, no crash
   - B7-5: ticket `awaiting_ota_update` → Emergency ON → resolve succeeds (bypass `tickets/models.py:122`)
   - Flow E: `python manage.py sync_ota_bookings --source 12go` → events created → run again → no duplicates
2. **Deploy CS-CENTRALIZATION → main** — BE migrations `0005`–`0009` + Celery beat `sync_ota_bookings` (15min) + `check_sla_breaches`. All 3 repos develop→main.
3. **Fix `otaConsent.js:3`** — 8-char token prefix → full token key (1-line security fix).
4. **Fix `my-trip:238` UX gap** — show "Cancellation Confirmed" banner even when `booking.status=canceled`.
5. **Fix Bug 4** — `OtaTripView` add SLA fields to serializer.
6. **FE-M1 `InfoUpdateNotice`** + admin Phase 2-3 — still deferred.

_(Sessions #195 + #194 + #193 + #192 + #191 + #186 archived → `07-logs/session-history.md`.)_

---

## Section 2 — Loose Ends (Open)

> **REASSESSMENT 2026-06-30** — Tier-1 criticals FIXED on BE develop (`58872d5`, spot-verified #1/#3/#7/#8). Admin dialog redesign shipped (`4af50b1`). So the "BLOCKED until Tier-1 land" notes in Deploy Queue + CS-CENTRALIZATION row below are **STALE — Tier-1 landed**. Remaining for main deploy: **(A)** commit #191 uncommitted (BE `cs/views.py`+`tickets/views.py`, FE `RequestChangeModal.js`+test guide) + `NEXTAUTH_SECRET` fix; **(B)** finish manual test B-7/B-8/C/D/E (B-7b needs OTA seed); **(C)** Tier-2/3 + 3 workflow blockers (NEW-1 visibility, OQ-3 SLA unbuilt, Emergency partial); **(D)** admin Phase 2-3. Stale Tier-2 also resolved: `check_sla_breaches` NameError FIXED (`ticket_numbers` plural); `cs_chat` FeatureFlag fail-open True (`FeatureFlagView get_or_create defaults enabled=True`) → chat ON by default, no seed needed (kill-switch-inert only). **B-7 emergency bypass already works** (`tickets/models.py:119-123` clean() Blocker 3) — no FE fix. Full remaining-work map → `~/.claude/plans/check-vaault-and-continue-witty-lake.md`.

> **UPDATE 2026-06-30 (#193):** CS chat UX polish shipped → develop — sender attribution (ownership-gated widget `sender:'customer'` hint, spoof→403), role labels (FE You/Support/System + admin Customer/Support/System), unread badge read-on-open + active-conv auto-read (BE `Conversation.cs_last_read_at` + migration `0008` + `POST /conversations/<pk>/mark-read/`). Flow D chat verified live (200). `NEXTAUTH_SECRET` matched admin=FE. No new Section-2 items opened; CS-CENTRALIZATION deploy queue unchanged (develop-only; manual test C/E + B-7 + 3 go-live blockers still pending).


### Deploy Queue — merged → develop, needs main deploy + verify

| Item | What's pending | Where |
|------|----------------|-------|
| **OTA-FLOW-BUGS** | ✅ **MERGED → develop `413eb41e`.** 3 commits shipped. 3 commits: `c96b1724` (COLORS crash + image guard) · `09e3f955` (polling anti-pattern) · `0657c6fb` (TDZ crash). Merge → develop first, then include in OTA deploy. 2 BE bugs deferred (Bug 4 SLA fields + Bug 5 duplicate guard). 1 security deferred (`otaConsent.js:3` 8-char prefix → full token). | `components/bookings/TicketStatusBanner.js`, `BookingDetail/TripRoute.js`, `ChangeRequestsSection.js`, `pages/my-trip/index.js` · [[ota-flow-e2e-scan-2026-06-30]] |
| **CS-CENTRALIZATION-DEPLOY** | ⏳ **merged → develop. Tier-1 criticals FIXED (#194). Direct flows tested ✅ (#195). OTA manual test C1-C5/B7-4/Path A ✅ (#198). READY for main deploy.** Deploy all 3 develop→main + run BE migrations `0005`–`0009` + schedule Celery beat `sync_ota_bookings` (15min) + `check_sla_breaches`. BE `259c0d8` · admin `830cfec` · FE `80714750` current develop tips. | `tickets/apps.py`, `Smartenplus/celery.py`, `cs/views.py` · [[cs-centralization-audit-2026-06-29]] |
| **FULL-DEPLOY** | ✅ **DEPLOYED 2026-06-26** — all 3 repos develop→main. FE `43299da` · BE `ebbb044` · admin `3d5a3a4`. Includes G8, P3a/P3b, CS chat Steps 5-7, CS-CHAT-PERF, r12 SEO. | ✅ Done |
| **CS-CHAT-PERF** | ✅ **CODE DEPLOYED 2026-06-26**. ⚠️ Widget still hidden — must seed `cs_chat=True` FeatureFlag row in prod DB via Django admin or SQL to activate FAB. | `hooks/useChatPolling.js`, `hooks/useFeatureFlag.js`, `cs/views.py`, `cs/models.py` · [[cs-guest-storm-investigation]] |
| **P2-OTA-SYNC** | run migrations on prod (`0003_csotabooking`, `0004_csotabooking_extra_fields`) + schedule Celery beat `cs.tasks.sync_ota_bookings`. 563 rows synced idempotent. | `cs/tasks.py`, `cs/supabase_client.py` · [[ota-sync-supabase-mirror]] |
| **ISR-REVALIDATE-GAP** | verify prod env vars set (`FRONTEND_URL=https://www.smartenplus.co.th`, non-empty `REVALIDATION_SECRET`) + worker recreated (stale worker = unregistered task). Smoke-test: admin contract edit → `/activities/detail` updates <60s. | `operators/signals.py`, `operators/tasks.py`, FE `pages/api/revalidate.js` · [[celery-unregistered-task-stale-worker]] |
| **TASK-1VCPU-MONITOR** | verify #139 prod incident resolved: CloudWatch CPU-credit stops draining, no `:00`/2 AM spike. | CloudWatch, `products/tasks.py` |

### Active

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **CS-GUEST-EMAIL-GATE** | Guest can type any email before OTP — no verification on conv creation. Risk LOW now (no booking data shown). MUST add OTP gate before Phase 4 OTA data shown to CS agents. | **OPEN — Phase 4 prereq** | `cs/views.py` `ConversationCreateView` |
| **CS-CENTRALIZATION** | RESCOPED 2026-06-23 → Unified Booking Command Centre. P0 chat + P1 direct + P2 OTA-sync SHIPPED. **P3a/P3b/G2/G8 SHIPPED.** Tier-1 criticals FIXED (#194). Direct booking flows (date_change ✅ cancellation ✅ pax_change ✅) tested (#195). **READY for main deploy.** Remaining open: FE-M1 (InfoUpdateNotice) + admin Phase 2-3 + OTA manual tests (C/E/B-7). | **READY — deploy develop→main** | [[cs-centralization-audit-2026-06-29]] · [[ota-link-delivery-and-p3b-plan]] · [[booking-command-centre-decision]] |
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
