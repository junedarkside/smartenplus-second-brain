# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-29 (session #190 — BD Report v2 + vault stray cleanup wrap-up)

**Achieved since #186 (sessions #187-#190):**

- **#187 (catalog audit Phase 0+1)** — Created 4 atomic notes (`live-catalog-discovery-protocol`, `thailand-location-coverage-framework`, `three-layer-gap-coverage-matrix`, `operator-outreach-question-template`) + 1 project page (`01-projects/products-live-catalog-audit.md`). Phase 1 Public API Snapshot: 13 API fetches + 3 sitemap fetches → 1224 contracts, 176 stations, 7/10 categories empty, 6 charter routes, SPA single-operator. 10 BD gaps logged. **Commit `dfc581a`.**
- **#188 (catalog audit Phase 2 + atomize)** — 10 BD-ready grill question docs at `business-development/products-live-catalog/grill-questions/`. 5 new atoms atomized: `public-api-filter-silent-ignore`, `grill-skill-efficient-batch-pattern`, `api-smartenplus-co-th-endpoint-inventory`, `bd-commission-tier-framework`, `live-catalog-audit-public-api-limitations`. **Commit `9cd1988`.**
- **#189 (vault stray cleanup)** — Read-only scan found 16 strays (1 orphan + 15 broken wikilinks). Fixed: 1 stub for `customer-os-thesis-r2-skeptic-review.md`, 4 stubs in `01-projects/customer-os-thesis/`, 4 alias map entries in `vault-broken-links-repair.py`, 3 code-style ref conversions, 1 orphan back-link. Re-scan: 0 strays. **Commit `e18efa5`.**
- **#190 (BD Report v1 + v2 + Thai translation)** — Created BD-readable report from Phase 1+2 findings (executive summary + 5 prioritized gaps + outreach playbook + revenue opportunity + Monday action plan). Extended with 4 Thai-specific sections (Thai Operator Landscape, Competitive Analysis, Outreach Scripts, Business Culture). Translated to Thai. User feedback round applied via 6 parallel agents (revenue formulas, competitive matrix restructure, supplier categorization, operational feasibility tables, exec summary rewrite, Thai naturalness) → v2. **Files in `business-development/` only — no vault commits.**

**Workspace (#190):**
- vault: master (`e18efa5`) — clean.
- backend: develop (`424f72a`) — clean.
- frontend: develop (`4c0df60`) — clean.
- admin-dashboard: develop (`69bde06`) — clean.
- content: master (`3756e5b`) — clean.

**Resume point (EXACT):**
1. **Validate BD report revenue estimates with Finance** (currently order-of-magnitude only).
2. **BD team begin operator outreach** per gap-001/008/009 priorities (Charter / Andaman Day Tours / Spa Diversification).
3. **Resolve owner decisions** for gap-002 (Airport Transfers intentional?) + gap-007 (Accommodation?) + gap-010 (Other Services?).
4. **Phase 1.5 — Django shell queries** if user provides prod DB access (deferred from Phase 1; would enable station FK pivot + query_count demand signal + sub-gap detection).
5. **Regenerate `products-live-catalog/snapshot-2026-06-28.md`** with Django shell data when available.

_(Sessions #187-#190 detailed in `07-logs/log.md` — see commit references. Session #186 archived → `07-logs/session-history.md`.)_

---

**Achieved (#186) — CS-Centralization: cross-repo conformance fix + ship to develop + branch prune:**
- ✅ Analyzed CS-Centralization across FE/BE/admin vs `cs-workflow-revised-2026-06-27` (3 Explore agents). Found BE "close 5 gaps" partial + dead core (#1 resolve-block guard never fired via API) + 2 admin→BE API breaks. Full report → `~/.claude/plans/noble-watching-waffle.md`.
- ✅ Fixed 4 🔴 critical:
  - **BE** (`feat/cs-centralization-blockers`): resolve-block guard now enforced via API (`RequestStatusViewSet.partial_update` calls `instance.clean()`, `ValidationError`→400); emergency path works (bypass-first `clean()` reorder + `pending→resolved` for emergency + `old_ticket=None` NameError fix); field-only PATCH allowed (transition check gated on `request_status` present); guard Check 1 uses `old_ticket.status_changed_at` (awaiting-entry) so Supabase-event branch works. +3 tests, 1 adjusted. **64/64 green.**
  - **Admin** (`feat/cs-workflow-revised-gaps`): resend sends `{booking_id, source}` (was Django PK `booking.id` → 400); emergency toggle → `request-status/` via new `setEmergencyFlag` mutation (was raw axios to `tickets-set-status/` which ignored `is_emergency`).
- ✅ Merged all 3 repos → develop + pushed: **BE `424f72a`**, **admin `69bde06`**, **FE `4c0df60`** (stranded FE-B3 `OtaRequestCard` delete + `/my-trip` conditional-poll that PR #183 missed).
- ✅ Pruned **12 stale branches** (local + remote): BE 3 (`feat/cs-centralization-blockers`, `fix/birthdate-year-truncation`, `feat/my-trip-show-ticket-status` [superseded by `f8e1f4b`]), admin 1 (`feat/cs-workflow-revised-gaps`), FE 8 (checkout-phone-validation, cs-ticket-status-banner, birthdate-year-truncation/validation, checkout-contact-prefill, phone-normalize-legacy, seo-r11, seo-r12).

**Workspace (#186):**
- backend: `develop` (`424f72a`) — clean.
- admin-dashboard: `develop` (`69bde06`) — clean.
- frontend: `develop` (`4c0df60`) — clean.
- vault: master · content: master (`3756e5b`) clean.
- All CS feature branches pruned (local + remote). Only `develop` + `main` remain per repo.

**Resume point (EXACT):**
1. **DEPLOY CS work → main** (all 3 repos develop→main) + run BE migrations `0005`–`0009` (cs `0005`/`0006`, tickets `0006`–`0009`) on prod + schedule Celery beat `sync_ota_bookings`. See Deploy Queue.
2. **🟡 BE-B1** add 3 magic-link fields (`magic_token_generated_at`, `auto_send_magic_link`, `is_magic_link_valid`) — magic links valid forever (no expiry).
3. **🟡 BE-B3** resend: regenerate `magic_token` + SES send (currently read-only, returns existing link).
4. **🟢 FE-M1** `InfoUpdateNotice` component (surface `TripNotification`) — only remaining FE item.
5. Update vault `cs-centralization-gap-report-2026-06-27.md` Layer status (BE-B1..B5 + admin breaks now resolved on develop; 🟡 remaining).
6. *(Carry-forward)* OQ-3 `awaiting_ota_update` SLA (Product owes timeout + ETA surface); Admin Phase 2-3; post-merge follow-up branches (RTL/i18n/a11y/analytics) per #184.

_(Session #185 archived → `07-logs/session-history.md`.)_

---

## Section 2 — Loose Ends (Open)

### Deploy Queue — merged → develop, needs main deploy + verify

| Item | What's pending | Where |
|------|----------------|-------|
| **CS-CENTRALIZATION-DEPLOY** | ⏳ **merged → develop 2026-06-28 (NOT yet main)** — BE `424f72a` · admin `69bde06` · FE `4c0df60`. Deploy all 3 develop→main + run BE migrations `0005`-`0009` (cs `0005_add_event_and_notification_models`, `0006_add_magic_token_supabase_row_id`; tickets `0006_add_blocker_fields`, `0007`/`0008`/`0009` auto) on prod + schedule Celery beat `sync_ota_bookings` (15min) + `check_sla_breaches`. Verify resolve-block guard + emergency path + Resend Email + emergency toggle end-to-end. | `tickets/views.py`, `tickets/models.py`, `cs/tasks.py` · [[cs-centralization-gap-report-2026-06-27]] |
| **FULL-DEPLOY** | ✅ **DEPLOYED 2026-06-26** — all 3 repos develop→main. FE `43299da` · BE `ebbb044` · admin `3d5a3a4`. Includes G8, P3a/P3b, CS chat Steps 5-7, CS-CHAT-PERF, r12 SEO. | ✅ Done |
| **CS-CHAT-PERF** | ✅ **CODE DEPLOYED 2026-06-26**. ⚠️ Widget still hidden — must seed `cs_chat=True` FeatureFlag row in prod DB via Django admin or SQL to activate FAB. | `hooks/useChatPolling.js`, `hooks/useFeatureFlag.js`, `cs/views.py`, `cs/models.py` · [[cs-guest-storm-investigation]] |
| **P2-OTA-SYNC** | run migrations on prod (`0003_csotabooking`, `0004_csotabooking_extra_fields`) + schedule Celery beat `cs.tasks.sync_ota_bookings`. 563 rows synced idempotent. | `cs/tasks.py`, `cs/supabase_client.py` · [[ota-sync-supabase-mirror]] |
| **ISR-REVALIDATE-GAP** | verify prod env vars set (`FRONTEND_URL=https://www.smartenplus.co.th`, non-empty `REVALIDATION_SECRET`) + worker recreated (stale worker = unregistered task). Smoke-test: admin contract edit → `/activities/detail` updates <60s. | `operators/signals.py`, `operators/tasks.py`, FE `pages/api/revalidate.js` · [[celery-unregistered-task-stale-worker]] |
| **TASK-1VCPU-MONITOR** | verify #139 prod incident resolved: CloudWatch CPU-credit stops draining, no `:00`/2 AM spike. | CloudWatch, `products/tasks.py` |

### Active

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **CS-GUEST-EMAIL-GATE** | Guest can type any email before OTP — no verification on conv creation. Risk LOW now (no booking data shown). MUST add OTP gate before Phase 4 OTA data shown to CS agents. | **OPEN — Phase 4 prereq** | `cs/views.py` `ConversationCreateView` |
| **CS-CENTRALIZATION** | RESCOPED 2026-06-23 → Unified Booking Command Centre. P0 chat + P1 direct + P2 OTA-sync SHIPPED. **P3a/P3b/G2/G8 SHIPPED.** All branches merged → develop. **#186: CS-BE gaps + 4 critical fixes + admin/FE work all → develop** (BE `424f72a`, admin `69bde06`, FE `4c0df60`). Remaining 🟡: BE-B1 (3 magic-link fields), BE-B3 (resend regen+SES), FE-M1 (InfoUpdateNotice). G1 auto-email (P3c), G4 boarding feed, G5 expired-link still open. | **deploy queue — CS work needs main deploy** | [[ota-link-delivery-and-p3b-plan]] · [[ota-portal-overview]] · [[booking-command-centre-decision]] |
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
