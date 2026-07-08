# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-07-08 (session #228)

**Achieved this session (#228):**
- Built staff Web Push notifications for admin-dashboard (BE + AD)
  - BE: `StaffPushSubscription` model + migration `cs.0013` + `cs/push.py` helper + `cs/signals.py` (new conv) + `tickets/signals.py` (new ticket) + `PushSubscriptionView` API + VAPID settings
  - AD: `public/sw.js` service worker + `public/manifest.json` PWA manifest + `hooks/usePushSubscription.js` + Enable banner in `pages/cs/index.js` + background push in `SideList.js` onEvent
  - Error handling: try/catch in subscribe hook, res.ok check, sw showNotification .catch(), logger.warning in push.py
  - Migration applied locally (`cs.0013_staff_push_subscription`)
  - Commits: BE `8c00267` · AD `842752b` → develop
- Added `pywebpush>=2.0.0` to BE `requirements.txt`

**Workspace (#228):**
- vault: master — updated this session
- backend: `develop` (`8c00267`) — clean
- frontend: `develop` (`436499b0`) — clean
- admin-dashboard: `develop` (`842752b`) — clean
- content: master (`3756e5b`) — clean

**Resume point — next session:**
1. **STAFF-PUSH-PROD-SETUP** — generate VAPID keys (`npx web-push generate-vapid-keys`), add `VAPID_PRIVATE_KEY`/`VAPID_PUBLIC_KEY`/`VAPID_CLAIMS_EMAIL` to BE `.env`, add `NEXT_PUBLIC_VAPID_PUBLIC_KEY` to AD `.env.local`, `pip install pywebpush` on server, `python manage.py migrate` on server.
2. **CHAT PROD DEPLOY** — develop→main all 3 repos. Verify OTA comeback + soft-link chip in prod.
3. **DIRECT-BOOKINGS-TAB** — 3 branches uncommitted (BE + admin + FE), review + merge → develop → smoke test.

_(Sessions #221–#224, #226–#227 archived → `07-logs/session-history.md`.)_

---

## Section 2 — Loose Ends (Open)

> **REASSESSMENT 2026-06-30** — Tier-1 criticals FIXED on BE develop (`58872d5`, spot-verified #1/#3/#7/#8). Admin dialog redesign shipped (`4af50b1`). So the "BLOCKED until Tier-1 land" notes in Deploy Queue + CS-CENTRALIZATION row below are **STALE — Tier-1 landed**. Remaining for main deploy: **(A)** commit #191 uncommitted (BE `cs/views.py`+`tickets/views.py`, FE `RequestChangeModal.js`+test guide) + `NEXTAUTH_SECRET` fix; **(B)** finish manual test B-7/B-8/C/D/E (B-7b needs OTA seed); **(C)** Tier-2/3 + 3 workflow blockers (NEW-1 visibility, OQ-3 SLA unbuilt, Emergency partial); **(D)** admin Phase 2-3. Stale Tier-2 also resolved: `check_sla_breaches` NameError FIXED (`ticket_numbers` plural); `cs_chat` FeatureFlag fail-open True (`FeatureFlagView get_or_create defaults enabled=True`) → chat ON by default, no seed needed (kill-switch-inert only). **B-7 emergency bypass already works** (`tickets/models.py:119-123` clean() Blocker 3) — no FE fix. Full remaining-work map → `~/.claude/plans/check-vaault-and-continue-witty-lake.md`.

> **UPDATE 2026-06-30 (#193):** CS chat UX polish shipped → develop — sender attribution (ownership-gated widget `sender:'customer'` hint, spoof→403), role labels (FE You/Support/System + admin Customer/Support/System), unread badge read-on-open + active-conv auto-read (BE `Conversation.cs_last_read_at` + migration `0008` + `POST /conversations/<pk>/mark-read/`). Flow D chat verified live (200). `NEXTAUTH_SECRET` matched admin=FE. No new Section-2 items opened; CS-CENTRALIZATION deploy queue unchanged (develop-only; manual test C/E + B-7 + 3 go-live blockers still pending).


### Deploy Queue — merged → develop, needs main deploy + verify

| Item | What's pending | Where |
|------|----------------|-------|
| **OTA-FLOW-BUGS** | ✅ **DEPLOYED TO PROD 2026-07-03** — 3 commits: `c96b1724` · `09e3f955` · `0657c6fb`. 2 BE bugs deferred (Bug 4 SLA fields + Bug 5 duplicate guard). 1 security deferred (`otaConsent.js:3` 8-char prefix). → closed-items.md | — |
| **CS-CENTRALIZATION-DEPLOY** | ✅ **DEPLOYED TO PROD 2026-07-03** — BE `6cb2328` · FE `5617b137` · admin `0e5727b`. All manual tests PASS. Celery beat scheduled. → closed-items.md | — |
| **FULL-DEPLOY** | ✅ **DEPLOYED 2026-06-26** — all 3 repos develop→main. FE `43299da` · BE `ebbb044` · admin `3d5a3a4`. Includes G8, P3a/P3b, CS chat Steps 5-7, CS-CHAT-PERF, r12 SEO. | ✅ Done |
| **CS-CHAT-PERF** | ✅ **CODE DEPLOYED 2026-06-26**. ⚠️ Widget still hidden — must seed `cs_chat=True` FeatureFlag row in prod DB via Django admin or SQL to activate FAB. | `hooks/useChatPolling.js`, `hooks/useFeatureFlag.js`, `cs/views.py`, `cs/models.py` · [[cs-guest-storm-investigation]] |
| **P2-OTA-SYNC** | run migrations on prod (`0003_csotabooking`, `0004_csotabooking_extra_fields`) + schedule Celery beat `cs.tasks.sync_ota_bookings`. 563 rows synced idempotent. | `cs/tasks.py`, `cs/supabase_client.py` · [[ota-sync-supabase-mirror]] |
| **ISR-REVALIDATE-GAP** | verify prod env vars set (`FRONTEND_URL=https://www.smartenplus.co.th`, non-empty `REVALIDATION_SECRET`) + worker recreated (stale worker = unregistered task). Smoke-test: admin contract edit → `/activities/detail` updates <60s. | `operators/signals.py`, `operators/tasks.py`, FE `pages/api/revalidate.js` · [[celery-unregistered-task-stale-worker]] |
| **TASK-1VCPU-MONITOR** | verify #139 prod incident resolved: CloudWatch CPU-credit stops draining, no `:00`/2 AM spike. | CloudWatch, `products/tasks.py` |

### Active

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **AUTH-SWITCH-BUGS** | ✅ **FIXED** — 3 identity-switch edge cases fixed. (A) Guest→OTA wrong conv — reset effect on `[otaToken]` clears non-OTA conv. (B) Realtime silent fail on auth loss — `refreshToken` 403 now calls `onConversationClosed()`. (C) Stale OTA localStorage key on login — cleared in login-while-chatting RESET. FE `develop` `cd6874d6`. | **CLOSED** | [[ota-chat-auth-switch-analysis-2026-07-08]] |
| **STAFF-PUSH-NOTIFICATIONS** | Web Push built + merged → develop (BE `8c00267` · AD `842752b`). **Pending prod setup:** generate VAPID keys (`npx web-push generate-vapid-keys`), add `VAPID_PRIVATE_KEY`/`VAPID_PUBLIC_KEY`/`VAPID_CLAIMS_EMAIL` to BE `.env`, add `NEXT_PUBLIC_VAPID_PUBLIC_KEY` to AD `.env.local`, `pip install pywebpush` on server, `python manage.py migrate` (cs.0013). Then test Enable banner at `/cs`. | **PROD SETUP PENDING** | `cs/push.py` · `cs/signals.py` · `tickets/signals.py` · `public/sw.js` · `hooks/usePushSubscription.js` |
|---|-------|--------|-------|
| **DIRECT-BOOKINGS-TAB** | Command-centre 3rd tab "Direct Bookings" — notify + admin-initiated request for direct bookings (parity w/ OTA tab). **BUILT (#205) + customer-display fix (#206)** on 3 branches, **UNCOMMITTED**: BE `feat/cs-direct-bookings-tab` (list+ticket endpoints+routes+8 tests + `orders/serializers.py` notifications fix), admin `feat/admin-direct-bookings-tab` (csApi hooks + `NotifyDialog.jsx` + `DirectBookingsTab`), FE `feat/fe-m1-info-update-notice` (banner moved to top + design-system card width). Column "Service" (`contract_name`). Customer page now shows sent notifications. Decision report [[command-centre-direct-notify-redesign]]. | **REVIEW + MERGE develop → manual smoke** | [[command-centre-direct-notify-redesign]] · [[direct-booking-notify-plan]] · [[booking-item-serializer-name-collision]] |
| **INFO-UPDATE-NOTICE-WIDTH** | ✅ **FIXED #208** — added `max-w-[1200px] mx-auto w-full` to banner mount (`BookingDetailMain.js:210`). Also fixed OTA `/my-trip` gap: added `mt-4` to InfoUpdateNotice wrapper (`pages/my-trip/index.js:238`). Both merged → develop `50fb201e`. | **CLOSED** | [[command-centre-direct-notify-redesign]] |
| **CS-GUEST-EMAIL-GATE** | ✅ **FIXED #211** — `ConversationCreateView` now returns 403 `OTP_REQUIRED` when existing open/pending conv found for guest email. No free token without OTP. Merged → develop `4690fcb`. | **CLOSED** | `cs/views.py` `ConversationCreateView` |
| **CS-CENTRALIZATION** | RESCOPED 2026-06-23 → Unified Booking Command Centre. P0 chat + P1 direct + P2 OTA-sync SHIPPED. **P3a/P3b/G2/G8 SHIPPED.** Tier-1 criticals FIXED (#194). Direct flows ✅ (#195). OTA manual tests ALL PASS (#203). **FE-M1 InfoUpdateNotice BUILT (#204)** — `feat/fe-m1-info-update-notice`. **Admin Phase 2 BUILT (#204)** — `feat/admin-phase2-command-centre`. **29/29 BE unit tests pass.** **Remaining:** (1) merge 3 branches → develop, (2) E2E manual test, (3) Admin Phase 3, (4) develop→main deploy. | **MERGE + TEST NEXT** | [[cs-centralization-audit-2026-06-29]] · [[ota-link-delivery-and-p3b-plan]] · [[booking-command-centre-decision]] |
| **CHAT-SUPABASE-OFFLOAD** | ✅ **CLOSED #225** — realtime unread badge verified working. Sidebar icon + inbox row pill + preview + timestamp all update via Supabase payload. Client-authoritative (no Django round-trip). 6 fix branches → admin-dashboard `develop` `9316997`. → closed-items.md | **CLOSED** | [[chat-review-e2e-manual-test-2026-07-07]] |
| **BE-HOMEPAGE-PRICE** | REC-engine `get_contract_price` (`services.py:74`), `RecommendationSerializer.get_lowest_price` (`serializers.py:~1105`), 6 finder `Min(selling_rate)` annotations — all still unfiltered. Homepage "From" price shipped #136, same-class bug remains. | **OPEN — REC-engine price bug** | `products/services.py`, `products/serializers.py:~1105` |
| **REC-SLOT-WASTE** | ESSENTIAL zone renders short (1 not 2) when cart item overlaps backend rec: FE excludes cart ids AFTER backend applied per-zone caps. Fix: API `exclude_ids` param threaded into finders before cap slice; cache key includes sorted exclude set. | OPEN #133 — deferred | `products/services.py` get_recommendations · [[recommendation-engine-completion-roadmap]] |
| **BE-IMAGE-DEDUP** | BE image-processing duplication (moderate). WebP resize/compress ~2-3× (`operators/utils.py`, `dialogue/utils.py`, `operators/admin.py`); upload validation copy-pasted across 5 files. Consolidate → one `core/image_utils.py`: `process_image_to_webp()` + `validate_upload()`. High blast radius, dedicated refactor session. | OPEN #126 | `operators/utils.py`, `dialogue/utils.py` |
| **SEO-P1-BACKLOG** | r6-r13 code DONE. **r13 merged → develop `c2920a81`** — TouristDestination+@id+BreadcrumbList on destinations, /activities LCP, CWV-4, GEO-1, OAI-SearchBot, sitemap. **Pending prod deploy + next-week re-audit.** Post-r13 open: `/about` TravelAgency parity (priceRange/openingHours/geo/contactPoint missing), `/about` BreadcrumbList+WebPage, CWV-5 CF HTML cache (needs cookie bypass), SD-NEW-2/4 ops (Django admin data), `/help/faqs` FAQPage ops-blocked. | **Deploy develop→main, then re-audit next week** | [[seo-aeo-geo-live-audit-2026-06-22/r12-live-prod-2026-07-03]] |
| **SEO-P2-FIXES** | twitter:image:alt (`_app.js` + `Seo.js`); og:locale policy unify; meta desc ≤155 chars; blog robots dup. From r6: help relative `og:image`→abs prefix (`pages/help/[...slug].js:89,109`); **lint** `structured-data-schema-patterns.md` item 7 `availableLanguage:["Thai","English"]` contradicts en-only policy → `["English"]`. `#15 og:url` CLOSED `0aa748c`. | OPEN — low | `pages/_app.js`, `components/FrontPage/Seo.js`, `utils/blog/seoHelper.js`, `03-knowledge/structured-data-schema-patterns.md` |
| **SEARCH-UI-POLISH** | Deferred nits from #138 (NOT regressions). SearchModeTabs ARIA (arrow-key nav, role=tabpanel); `seach-button` typo (also `TransportationSearch.js:248`); SearchDialog close icon red vs grey; comment inverts nav order; mobile tab-switch height jump. | OPEN #138 — low | `components/search/SearchModeTabs.js`, `SearchDialog.js`, `TabbedSearchPanel.js` |
| **DURATION-DAYS-CARDS** | Day-tour browse cards omit duration: LIST `ContractSerializer` doesn't expose `tour_duration_days`. Option B: add to list serializer fields. One-line, low risk (read-only int); needs BE deploy + ISR cache clear. | OPEN #130 — optional low | `operators/serializers.py` (ContractSerializer) · [[category-aware-duration-formatter]] |
| **CROSS-SELL-BD-INVENTORY** | BD creates Koh Lipe inventory to activate cross-sell. Needs: return route Koh Lipe→Hat Yai Airport, DAY_TOUR + SPA_WELLNESS contracts at Koh Lipe. All 4 FE surfaces live 2026-06-13. Sole open eng item: multi-item post-booking (`bookingContext.js:33`, Sprint 2). | BD action | [[cross-sell-integration-status-2026-06-13]] |
| **ADMIN-CS-CENTRALIZATION** | **Phase 1 + Phase 4 SHIPPED → develop `69bde06` (#186)**. **Phase 2 SHIPPED (`ce873f9`)** — UI cleanup + SLA countdown. **Gap fixes SHIPPED (#211)** — H8/H9/C7/C1/C3/C6 all merged develop. **Phase 3 pending** — `ota-booking-detail.js` + `OtaBookingTimeline.js` + `OtaBookingAdminPanel.js`. **OTA Auto-Sync toggle CONFIRMED BUILT** — `pages/dashboard/settings/settings.js:66-91`; `useUpdateFeatureFlagMutation({ key:'ota_sync', enabled })` → BE `cs/tasks.py:75` FeatureFlag gate. Toggle at Admin → Settings. | **Phase 3 pending** | [[admin-dashboard-cs-centralization-plan]] · [[command-centre-gap-audit]] |
| **CS-BE-GAPS** | ✅ **All 5 gaps closed + merged → develop `424f72a` (#186)** incl. resolve-block guard wired to API + emergency path + field-only PATCH. magic_token+supabase_row_id, POST ota/sync/, POST ota/resend-magic-link/, RequestStatusViewSet admin fields, OtaBookingEvent creation in sync task. 33 gap tests. **🟡 Remaining:** BE-B1 (add `magic_token_generated_at`/`auto_send_magic_link`/`is_magic_link_valid` — no link expiry). ✅ BE-B3 FIXED (#215) — `OtaResendMagicLinkView` now calls `send_html_email()` + `magic_link_last_sent_at` tracking. `647f3b5` → develop. | **on develop — deploy + BE-B1 remaining** | [[cs-centralization-gap-report-2026-06-27]] |
| **CS-FE-OTA-GAPS** | ✅ **RESOLVED + fully → develop `4c0df60` (#186)** — FE-B1..B5 + stranded FE-B3 `OtaRequestCard` delete + `/my-trip` conditional-poll (parity w/ FE-B4). All FE CS work on develop. **Open follow-ups (non-blocking):** (a) no RTL/e2e tests; (b) hard-coded EN strings in `TicketStatusBanner` + `/my-trip` — no i18n; (c) no analytics events; (d) a11y gaps (SLAProgress opacity-only, status pill lacks `role="status"`/`aria-live`, emergency lacks `role="alert"`); (e) `CS_BLOCKERS_IMPLEMENTATION_PLAN.md` at repo root → move to `docs/features/`. | **RESOLVED · on develop** | [[cs-centralization-gap-report-2026-06-27]] |
| **PRODUCTS-LIVE-CATALOG-AUDIT** | **PHASE 1 FINAL 2026-06-28 · Public API Snapshot.** 1224 contracts · 176 stations · 7/10 service categories empty (TRANSFER · MULTI_DAY_TOUR · EVENT_TICKET · ATTRACTION_TICKET · FOOD_DINING · ACCOMMODATION · OTHER). Only 6 charter routes live (4 unique — Chiang Mai + Khao Lak only). SPA_WELLNESS = 100% Salisa Resort (single-operator risk). DAY_TOUR northern bias (5/5 ops in Chiang Rai/Chiang Mai/Hat Yai; Andaman islands absent). **10 BD gaps logged** (`business-development/products-live-catalog/gap-inventory.md`): gap-001 charter routes near-zero · gap-002 transfer empty · gap-003 MULTI_DAY_TOUR empty [Experiences lens 100% uncovered] · gap-004/005/006/007/010 service_categories empty · gap-008 day-tour geographic skew · gap-009 SPA concentration risk. **Django shell deferred (Phase 1.5)** — API filters `?is_actived=false`/`?end_date__gte=` silently ignored, no station FK IDs exposed via public API. **Next:** Phase 2 = `grill` skill × 10 gaps → BD-ready question docs. | **PHASE 1 FINAL · Phase 2 next** | [[products-live-catalog-audit]] · `business-development/products-live-catalog/snapshots-2026-06-28.md` |

### Low-priority backlog

→ [[low-priority-backlog]] — 27 deferred nits (IMG-ALT-DEBUG-1, F11×2, RR-1, GSC-1, CMA-1, FAQ-1, AT-1/2, numbered 1/2/3/8/15, Nav, Explore, HD-2/3/6, GAP-3/5/6/7, SILAPHAT-DESC, BOOKING-24H, SORT-VOCAB, BE-GIT-DIVERGE).

---

**See also:** [[vault-protocol]] (API contract) · [[vault-guardrails]] (architecture) · [[session-history]] (#38+) · [[closed-items]] (resolved) · [[low-priority-backlog]] (deferred nits)
