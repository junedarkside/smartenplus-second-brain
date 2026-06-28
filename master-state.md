# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-28 (session #185 — CS Guide staff help: Thai + Mermaid diagrams)

**Achieved (#185) — Admin-dashboard CS Guide staff help (Phase 4) BUILT:**
- ✅ Verified (vault): Phase 4 "Admin Help & Documentation" was planned but unbuilt — guide HTML existed (`public/help/cs-centralization-admin-guide.html`, 10.9KB, 2026-06-27) but NO sidebar nav wired it (unreachable by staff).
- ✅ Wired CS Guide nav: `menuData.js` (CS Guide item + `HelpOutlineOutlined` icon + `external:true` flag) + `SideBarListMenu.js` (new `MenuLink` helper → `<a target="_blank">` when external, else next/link; DRY, regression-free — other items unaffected).
- ✅ Fixed 404 bug: file lives in `public/help/` subdir → nav path needed `/help/` prefix. Verified 200.
- ✅ Created Thai guide `public/help/cs-centralization-admin-guide-th.html` (lang=th, full Thai, system labels stay English/code, 3 Mermaid diagrams w/ Thai labels, `🌐 English version` toggle). Nav → Thai primary.
- ✅ Upgraded English guide: Mermaid CDN + 3 diagrams (EN labels) + `🌐 เวอร์ชันภาษาไทย` toggle.
- ✅ 3 diagrams each: Request Lifecycle (LR), Resolve-Block Guard (TD), Ticket Status Flow (TD).
- ✅ Created `docs/operations/CS_CENTRALIZATION_E2E.md` — full staff manual E2E (9 sections; CS Guide Thai + toggle + diagram checks; backend BE-B1..B5 flagged expected-non-functional).
- ✅ Verified live: TH + EN both HTTP 200, Mermaid script+init present, 3 flowcharts each, toggle links present, nav→TH confirmed.

**Workspace (#185):**
- admin-dashboard: `feat/cs-workflow-revised-gaps` (`d9413aa`) — **4 uncommitted (PENDING TEST)**: `M SideBarListMenu.js`, `M menuData.js`, `?? docs/operations/CS_CENTRALIZATION_E2E.md`, `?? public/help/` (en + th).
- frontend: `feat/cs-ticket-status-banner` (`ca64776`) — pre-existing #183 leftovers uncommitted (`D OtaRequestCard.js`, `M my-trip/index.js`). NOT this session.
- backend: `feat/cs-centralization-blockers` (`60176c5`) — clean, ready for PR.
- vault: master · content: master (`3756e5b`) clean.

**Resume point (EXACT) — "we will test later":**
1. **Test CS Guide** per `docs/operations/CS_CENTRALIZATION_E2E.md` §6 (admin-dashboard): reload → sidebar **CS Guide** → Thai page in new tab → 3 Mermaid diagrams render (need internet/CDN) → toggle EN↔TH → other nav unaffected.
2. **Commit admin-dashboard CS Guide work** on `feat/cs-workflow-revised-gaps` after test passes: `menuData.js` + `SideBarListMenu.js` + `public/help/` + `CS_CENTRALIZATION_E2E.md`.
3. **Update vault Phase 4 status → BUILT** (after commit): `admin-dashboard-cs-centralization-plan.md` Phase 4 + `cs-centralization-gap-report-2026-06-27.md` Layer 3 ADMIN-CS-CENTRALIZATION row.
4. *(Carry-forward #184)* post-merge follow-up branches, BE migration 0007, BE+admin PRs, OQ-3 SLA, Admin Phase 2-3.

_(Session #184 archived → `07-logs/session-history.md`.)_

---

## Section 2 — Loose Ends (Open)

### Deploy Queue — merged → develop, needs main deploy + verify

| Item | What's pending | Where |
|------|----------------|-------|
| **FULL-DEPLOY** | ✅ **DEPLOYED 2026-06-26** — all 3 repos develop→main. FE `43299da` · BE `ebbb044` · admin `3d5a3a4`. Includes G8, P3a/P3b, CS chat Steps 5-7, CS-CHAT-PERF, r12 SEO. | ✅ Done |
| **CS-CHAT-PERF** | ✅ **CODE DEPLOYED 2026-06-26**. ⚠️ Widget still hidden — must seed `cs_chat=True` FeatureFlag row in prod DB via Django admin or SQL to activate FAB. | `hooks/useChatPolling.js`, `hooks/useFeatureFlag.js`, `cs/views.py`, `cs/models.py` · [[cs-guest-storm-investigation]] |
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
| **SEO-P1-BACKLOG** | r6-r12 all DONE + prod-verified. **r11 prod** (`dbdc097`): soft-404, /activities schema+title, llms.txt, TAT identifier, aggregateRating removed, Penang MY, desc 152 chars. **r12 prod** (`43299da`): `numberOfItems:6`, desc 140 chars, ISR 3600s, S3 preconnect, `currenciesAccepted:THB`. **r10 audit** (post r11): SEO 9.0·AEO 9.5·GEO 9.0·CWV 7.0·SD 7.0. **r11 audit** (post r12): GEO/CWV 10.0, SD 9.0. **r13 open:** `/about` TravelAgency schema parity — missing `priceRange`, `openingHours`, `contactPoint`, `geo`, `image`, `logo` vs homepage (P1); `/about` missing BreadcrumbList+WebPage (P2); `og:locale th_TH` alternate (P2). `/help/faqs` FAQPage still ops-blocked (WP/GraphQL). | **r13 open** | [[r9-live-prod-2026-06-26]] · [[r10-live-prod-2026-06-26]] |
| **SEO-P2-FIXES** | twitter:image:alt (`_app.js` + `Seo.js`); og:locale policy unify; meta desc ≤155 chars; blog robots dup. From r6: help relative `og:image`→abs prefix (`pages/help/[...slug].js:89,109`); **lint** `structured-data-schema-patterns.md` item 7 `availableLanguage:["Thai","English"]` contradicts en-only policy → `["English"]`. `#15 og:url` CLOSED `0aa748c`. | OPEN — low | `pages/_app.js`, `components/FrontPage/Seo.js`, `utils/blog/seoHelper.js`, `03-knowledge/structured-data-schema-patterns.md` |
| **SEARCH-UI-POLISH** | Deferred nits from #138 (NOT regressions). SearchModeTabs ARIA (arrow-key nav, role=tabpanel); `seach-button` typo (also `TransportationSearch.js:248`); SearchDialog close icon red vs grey; comment inverts nav order; mobile tab-switch height jump. | OPEN #138 — low | `components/search/SearchModeTabs.js`, `SearchDialog.js`, `TabbedSearchPanel.js` |
| **DURATION-DAYS-CARDS** | Day-tour browse cards omit duration: LIST `ContractSerializer` doesn't expose `tour_duration_days`. Option B: add to list serializer fields. One-line, low risk (read-only int); needs BE deploy + ISR cache clear. | OPEN #130 — optional low | `operators/serializers.py` (ContractSerializer) · [[category-aware-duration-formatter]] |
| **CROSS-SELL-BD-INVENTORY** | BD creates Koh Lipe inventory to activate cross-sell. Needs: return route Koh Lipe→Hat Yai Airport, DAY_TOUR + SPA_WELLNESS contracts at Koh Lipe. All 4 FE surfaces live 2026-06-13. Sole open eng item: multi-item post-booking (`bookingContext.js:33`, Sprint 2). | BD action | [[cross-sell-integration-status-2026-06-13]] |
| **ADMIN-CS-CENTRALIZATION** | **Phase 1 SHIPPED** (`feat/cs-workflow-revised-gaps`): VALID_TRANSITIONS extended, SupabaseSyncBanner, SLA display, emergency toggle, resolution_note, admin_initiated, Resend Email. **Phase 4 (Admin Help & Documentation) BUILT (#185)** — Thai + EN guide + 3 Mermaid diagrams + sidebar nav wired (`MenuLink` external-anchor helper); uncommitted on `feat/cs-workflow-revised-gaps`, PENDING manual test. Admin FE buttons non-functional until BE gaps resolved (see CS-BE-GAPS below). Phase 2-3 pending. | **Phase 1 done · Phase 4 help BUILT (uncommitted, pending test) · Phase 2-3 pending** | [[admin-dashboard-cs-centralization-plan]] · [[cs-centralization-gap-report-2026-06-27]] |
| **CS-BE-GAPS** | ✅ All 5 gaps closed `feat/cs-centralization-blockers` (`3576edc`): magic_token+supabase_row_id fields+migration, POST ota/sync/, POST ota/resend-magic-link/, RequestStatusViewSet admin fields, OtaBookingEvent creation in sync task. 30 tests added (104 total pass). **Pending:** migration 0007 (OtaBookingEvent/TripNotification meta drift) before PR merge. | **DONE — PR ready** | [[cs-centralization-gap-report-2026-06-27]] |
| **CS-FE-OTA-GAPS** | ✅ **RESOLVED** (`835cb69` + `c968ffd`, session #183) — FE-B1 re-submit guard by open-status filter, FE-B2 `pollingInterval:60000` on `getOtaTrip`, FE-B3 `TicketStatusBanner` replaces `OtaRequestCard` in `/my-trip`, FE-B4 conditional `pollingInterval:120s` on `useGetBookingDetailQuery` keyed on `hasActiveTicket`. Branch ahead of main by 3 commits (2 unpushed to origin). **Open follow-ups (non-blocking)**: (a) no RTL/e2e tests for banner or polling/re-submit guard; (b) hard-coded English strings + `'en-GB'` locale in `TicketStatusBanner` + `/my-trip` — no i18n; (c) no analytics events (banner impression, status transition, SLA stage advance, re-submit guard prevent); (d) a11y — `SLAProgress` opacity-only (no shape diff), status pill lacks `role="status"`/`aria-live`, emergency lacks `role="alert"`, `<time dateTime>` missing, color-as-primary-signal; (e) no runtime guards on BE contract fields (`resolution_stage`, `operator_deadline`, `ota_deadline`, `admin_contacted_ota_at/_note`, `admin_initiated`, `resolution_note`, `is_emergency`); (f) `CS_BLOCKERS_IMPLEMENTATION_PLAN.md` at repo root — should move to `docs/features/`. | **RESOLVED · follow-up gaps tracked** | [[cs-centralization-gap-report-2026-06-27]] |

### Low-priority backlog

→ [[low-priority-backlog]] — 27 deferred nits (IMG-ALT-DEBUG-1, F11×2, RR-1, GSC-1, CMA-1, FAQ-1, AT-1/2, numbered 1/2/3/8/15, Nav, Explore, HD-2/3/6, GAP-3/5/6/7, SILAPHAT-DESC, BOOKING-24H, SORT-VOCAB, BE-GIT-DIVERGE).

---

**See also:** [[vault-protocol]] (API contract) · [[vault-guardrails]] (architecture) · [[session-history]] (#38+) · [[closed-items]] (resolved) · [[low-priority-backlog]] (deferred nits)
