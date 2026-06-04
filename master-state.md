I'll compress the markdown text you provided directly, following the compression rules.

# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-04 (session #43)

**Achieved this session (#43):**
- **CMA-1 HOTEL_PICKUP invariant — DONE** — `ContractDetailSerializer.validate()` added to `operators/serializers.py`. Rejects `HOTEL_PICKUP` + empty `meeting_point_details` on API PATCH. Handles partial PATCH via instance fallback. Commit `3a59a41` → backend main. Verified: 3 shell tests pass.
- **Admin-dashboard HOTEL_PICKUP frontend validation — DONE** — Yup `.when('meetingPointType')` + `.trim()` in `schemas/index.js`. Helper text in `DayTripDetails.js`. Commits `c2e8e4e` + `5f068ef` (whitespace bypass fix) → admin-dashboard main.
- **Activity detail MeetingPointCard reviewed** — working correctly, no changes needed.

**Achieved this session (#42):**
- **CMA-1 casing ADR — DONE** — vault ADR `04-decisions/adr-info-fields-casing.md` written. 6 inline comments across `checkoutPersistence.js`, `Passengers.js`, `BookingDetail/index.js`, `Information.js`, `PdfViewImproved.js`, `PdfView.js`. Frontend commit `375e501` → develop. Vault commit `6a35014` → master.
- **CMA-2 meeting_point_details — FIXED** — 3-specialist debate (backend + frontend + skeptic). Skeptic’s “no UI consumer” claim overturned: admin sets field, activity detail shows it, booking confirmation was broken end. Fix: 2 lines in `AdminBookingSummarySerializer.get_contract()` (`bookings/serializers.py`). Commit `09d6f3a` → backend main.
- **`get_translated_meeting_point_details` — DEFERRED** — English-only version. `ProductDetailSerializer` already exposes raw `meeting_point_details` via `fields = '__all__'`. Frontend `DayTripDetailPage.js:211` fallback `translated_X || X` handles it. No action until translation UI ships.

**Achieved this session (#41):**
- **CMA-1 partial — 2 of 6 items shipped** — 4-agent debate team (backend + frontend + domain + skeptic) reviewed all deferred items. Key overturns: `Contract.clean()` mis-scoped (model layer never fires on API PATCH; must be `ContractDetailSerializer.validate()`), new CMA-2 gap found (`ServiceDetail.js:35` zero i18n fallback).
  - **`showStations` dead flag deleted** — `helpers/serviceCategoryHelper.js` (-9 lines). Write-only property, zero callers across all 3 repos. Branch `260604-fix/cma1-dead-code-cleanup` → develop (`ff8006e`). Verified grep clean.
  - **Admin PATCH guard fixed** — `operators/views.py:807` `pass` → `return Response(400)` for bad `primary_location`. `service_areas.set()` wrapped try/except ValueError → 400. Branch `260604-fix/cma1-admin-patch-guard` → main (`22dc045`). Verified: 3 shell tests pass (bad primary_location 400 ✓, bad service_areas 400 ✓, null clear 200 ✓).

**Achieved this session (#40):**
- **Timeline stop deletion bug — FIXED + SHIPPED** — root cause: Django `update_timeline()` had `continue` in create branch for stops without a Place, silently skipping them from `existing_place_ids`. Delete sweep then wiped all DB stops. Fix: 5 changes across 3 repos.
  - `stations/models.py` — `TimeLinePlace.place` FK `CASCADE → SET_NULL null=True blank=True`
  - `stations/migrations/0028_timelineplace_place_nullable` — applied ✓
  - `operators/views.py` — `id=null` guard → DoesNotExist; removed `continue`; dropped `id=` from create; guarded delete sweep (`if existing_place_ids`); guarded `place_id` in update branch
  - `admin-dashboard/TimeLine.js` — `id: null` sentinel + `_clientKey: Date.now()` for React key
  - `smartenplus-frontend/TimeLineDisplay.js` — `place?.name`, `place?.image_gallery?.length` null-safe
  - Branch `fix/timeline-stop-deletion-bug` → develop → main all 3 repos
  - Atoms: [[django-nested-delete-sweep-pattern]], [[django-nullable-fk-migration-pattern]], [[react-client-key-null-id-pattern]]

**Achieved this session (#39):**
- **Contract model ambiguity audit** — 4-round multi-agent team (R1 backend/frontend/domain, R2 cross-exam, R3 skeptic, R4 synthesizer). 6 conceptual overlaps confirmed; 1 customer-visible (i18n on `meeting_point_details`), 5 staff-side or dormant. Skeptic overturned 2 dead-code claims (S-1: `Trip.route` 25+ call sites alive; S-2: `meeting_point_place` active in admin/tests/serializer). Recommendation: document + 1 small backend fix, no model consolidation. Vault: [[contract-model-ambiguity-audit-2026-06-03]] (117 lines)
- **Contract location help text fix (P0)** — admin form `ContractFormFields.js:179, 184, 222, 227` updated to match OR-search behavior (products/views.py:462-475). 4 strings: Primary Location tooltip + help, Service Areas tooltip + help. `service_areas` = pickup zones (per user). `primary_location` = main destination/operating area.
  - File: `admin-dashboard/components/contracts/ContractFormFields.js` (+4/-4)
  - Branch `260603-fix/contract-location-help-text` → develop → main
  - Commit `fa2f16a` on origin/main
- **Resolved session #38 carryover** — booking-summary fix `4bec691` confirmed on backend main; the "NOT yet merged" note in #38 was stale.

**Achieved this session (#38):**
- **booking-summary 500 fix** — `AdminBookingSummarySerializer.get_contract()` crashed when `contract.trip=None`. Guarded `trip` before accessing `.route` and `.departure_time`.
  - File: `bookings/serializers.py` (~5 lines)
  - Branch `260603-fix/booking-summary-trip-none-guard` committed + pushed to backend
  - **Now on main: `4bec691`** (verified session #39)
- **Frontend test infrastructure audit** — 5-agent team ran Jest (719 tests) + Playwright (260 tests). 54% pass rate, 3.92% coverage. BLOCK RELEASE. 6 CRITICAL issues. 4-5 dev days to fix. Vault: [[frontend-test-infrastructure-audit-2026-06-03]]

**Next session resume point (EXACT):**
1. **CMA-1 remaining:**
   - Data inventory: query `historical_contract` (simple_history) for `primary_location` changes last 90 days
2. Fix CART-1: `DayTripBookingWidget.js:338` — `error.status === 'PARSING_ERROR' || error.originalStatus >= 500`
3. Continue **FAQ-1** deferred: P1 admin-dashboard `ageRestriction` field (4 files)
4. **AT-1** airport transfer redesign
5. **FAV-1** favorite heart (ADR at `04-decisions/adr-activity-card-favorite-button.md`)
6. **TSTD-1** frontend test infrastructure fix (4-5 dev days, vault: [[frontend-test-infrastructure-audit-2026-06-03]])

### Active Branches

| Repo | Branch | Status |
|------|--------|--------|
| `smartenplus-frontend` | `develop` | Latest: `375e501` info_fields casing ADR comments |
| `smartenplus-backend` | `main` | Latest: `3a59a41` HOTEL_PICKUP invariant in ContractDetailSerializer.validate() |
| `admin-dashboard` | `main` | Latest: `5f068ef` HOTEL_PICKUP whitespace fix |
| `smartenplus-content` | `master` | Untracked: `strategy/business-development-thesis.md` (user work) |

---

## Section 2 — Loose Ends

### Open

| # | Issue | Blocker | Where |
|---|-------|---------|-------|
| ~~TL-1~~ | ~~Timeline stop deletion bug~~ | ✓ RESOLVED 2026-06-04. Migration 0028 applied. 3 atoms extracted. | — |
| CMA-1 | **Contract Model Ambiguity — P1/P2 partial** | ✓ P0 done #39. ✓ `showStations` deleted `ff8006e`. ✓ Admin PATCH guard `22dc045`. ✓ Casing ADR `375e501`. ✓ `ContractDetailSerializer.validate()` HOTEL_PICKUP guard `3a59a41`. `get_translated_meeting_point_details` DEFERRED. **Remaining:** data inventory via `historical_contract` (simple_history, `primary_location` changes last 90 days). | `operators/models.py` (simple_history) |
| ~~CMA-2~~ | ~~`ServiceDetail.js:35` zero i18n fallback~~ | ✓ RESOLVED #42. `meeting_point_type` + `meeting_point_details` added to `AdminBookingSummarySerializer.get_contract()` (`09d6f3a`). English-only — no translated fallback needed. | — |
| ~~ACT-7~~ | ~~Phase 1 QA + merge~~ | ✓ Done | — |
| ~~ACT-8~~ | ~~Backend merge~~ | ✓ Done `2d5a6ee` → develop | — |
| ~~ACT-9~~ | ~~Phase 2 pre-flight (backend)~~ | ✓ Done `508949b` | — |
| ~~ACT-10~~ | ~~Phase 2 QA + merge~~ | ✓ Done `b552e55` → develop | — |
| ~~ACT-11~~ | ~~Phase 3 mobile layout~~ | ✓ Done `f93df66` → develop | — |
| ~~ACT-12~~ | ~~Header search~~ | ✓ Done `5eaf8e2` — all bugs resolved, branch ready to merge | — |
| ~~BW-1~~ | ~~Blog index hero `px-4` padding~~ | ✓ Already fixed | — |
| ~~BW-2~~ | ~~Blog index featured section `px-2 md:px-4`~~ | ✓ Already fixed | — |
| ~~BW-3~~ | ~~BlogCard `rounded-lg` + no mx- margins~~ | ✓ Already fixed | — |
| ~~EXP-DETAIL-1~~ | ~~Experience Detail Page premium redesign + tablet/mobile~~ | ✓ DONE (#33) — FAQ, carousel, filter all shipped and merged | — |
| CART-1 | **Fix PARSING_ERROR catch** | `DayTripBookingWidget.js:338` — `error.status >= 500` fails silently when RTK sets string `'PARSING_ERROR'`. Fix: `error.status === 'PARSING_ERROR' \|\| error.originalStatus >= 500`. Deferred from session #34. | `components/activities/detail/DayTripBookingWidget.js:338` |
| FAQ-1 | **ExperienceFAQ single source of truth** | P0+P1+P2 DONE (#33). **DEFERRED:** P1 admin-dashboard `ageRestriction` field (4 files, separate repo). Vault: [[experience-faq-architecture-review-2026-06-02]] | `admin-dashboard/DayTripDetails.js` (deferred) |
| FAV-1 | **Favorite heart on DayTripCard** | ADR designed + scrutinized. 4 files: migration + views.py + BookmarkButton.js + DayTripCard.js. See [[adr-activity-card-favorite-button]] | `dialogue/views.py`, `BookmarkButton.js`, `DayTripCard.js` |
| AT-2 | Airport-transfer post-calendar width mismatch | Root cause: inner margins on StationInformation + GuidesSection + ProductCardContainer. | `components/destinations/StationInformation.js` etc. |
| TSTD-1 | **Frontend test infrastructure** | BLOCK RELEASE: 6 CRITICAL issues (0% BookButton coverage, checkout timeout, mobile 100% fail). 4-5 dev days. Vault: [[frontend-test-infrastructure-audit-2026-06-03]] | `jest.setup.js`, `jest.config.js`, `playwright.config.ts`, `e2e/` |
| AT-1 | **Airport Transfer professional redesign** | P0. Spec: vault `03-knowledge/transportation-category-audit-2026-05-30.md`. | `products/serializers.py`, `components/airport-transfer/AirportTransferRouteCard.js` |
| 15 | `refetchOnMountOrArgChange: 300→true` in useTripData | Separate justification needed | `hooks/useTripData.js:16,24` |
| 1 | `AdminBookingSummaryViewSet` unauthenticated | Needs frontend sign-off | `orders/views.py` |
| 2 | Delete `RefundViewSet` (legacy step 7) | Waiting on zero `DEPRECATED_ENDPOINT_USED` in prod logs | `cards/views.py` |
| 3 | Remove Stripe 410 stub | Waiting on zero prod traffic | `payments/urls.py` |
| 8 | Forex endpoint on admin-dashboard-charge URL | Naming debt | `cards/urls.py` |
| Nav | NavigationSection table empty | Restart backend + populate via admin | `pages_info` |
| Explore Thailand submenu | Needs `location_type` CharField on `Location` model | `stations/models.py` |
| HD-1 | CurrencySelector button too small at tablet | Low | `CurrencySelector.js:55` |
| HD-2 | CartButton dim (70% opacity) | Low — acceptable | `CartButton.js:116` |
| HD-3 | xl padding gap (px-0 vs px-3) | Low | `main-header.js:90` |
| HD-6 | Logo size jump mobile→desktop | P2 | `main-header.js:66,95` |
| GAP-3 | Mobile position flip relative→fixed | P2 | `main-header.js:45–77` |
| GAP-5 | Nav hidden while searching on trip page | P2 — accepted tradeoff | `main-header.js:112` |
| GAP-6 | threshold=0 abrupt snap | P3 | `hooks/useStickyVisibility.js:12` |
| GAP-7 | Wordmark hidden at md–xl when search active | P3 | `main-header.js:95` |
| IDX-1 | Add `experience-detail-ipad-mobile-redesign-2026-06-02` to index.md | Unindexed: file exists in `01-projects/` but absent from index. Cross-referenced from [[experience-faq-architecture-review-2026-06-02]]:151. Add to Active Projects. | `01-projects/experience-detail-ipad-mobile-redesign-2026-06-02.md` |
| IDX-2 | Add `experience-faq-architecture-review-2026-06-02` to index.md | Unindexed: file exists in `01-projects/` but absent from index. Already linked from master-state line 51. Add to Active Projects. | `01-projects/experience-faq-architecture-review-2026-06-02.md` |
| IDX-3 | Reconcile today's planned `content-marketing-strategy-2026-06-03` | NOT in index.md AND no file exists at `03-knowledge/content-marketing-strategy-2026-06-03.md`. Likely a planned-but-not-ingested note. Verify intent, ingest, or remove from roadmap. | `03-knowledge/content-marketing-strategy-2026-06-03.md` (missing) |
| IDX-4 | Resolve duplicate-basename wikilink conflicts | 3 filenames exist in two directories (knowledge + archive or projects + archive), causing ambiguous Obsidian resolution. Pick canonical location, rename the other with suffix `-v1` or move to archive-only. | `og-image-inferred-audit-2026-05-23`, `seo-wave2-audit-2026-05-23`, `homepage-uxui-audit-2026-05-31` |

---

## Section 3 — Cross-Repo API Contract

### Endpoints

**Public:** `GET /contract/` | `GET /product-detail/{slug}/` | `GET /contract/{id}/availability/?date=YYYY-MM-DD&people=N`

**Contract filter params (Phase 2 — session #24):**
- `min_price` / `max_price` — THB decimals
- `duration_type` — `half_day` | `full_day` | `multi_day`
- `contract_type` — `JOIN` | `PRIVATE` | `CHARTER`
- `features` — comma-sep exact Extra item strings (`Free Cancellation`, `Instant Confirmation`, `Hotel Pickup`)
- `min_rating` — float (e.g. `4`)
- `ordering` — accepts `min_rate` / `-min_rate` unconditionally (annotation hoisted, no price filter required)

**Admin:** `POST/PATCH/DELETE /admin-dashboard-operators/contract-details/{slug}/` | `POST .../copy/` | `POST /admin-dashboard-charge/manual-adjustment/`

**Cart & Order:** `POST /api/carts/{id}/cartitems/` | `PATCH .../cartitems/{item_id}/` | `DELETE .../cartitems/{item_id}/` | `POST /api/orders/` | `GET /api/orders/{id}/`

**Payment:** `POST /payments/order-charge/` | `POST /payments/webhook/` | `POST /payments/order-charge/{id}/expire/`

**User:** `GET /api/user/` (self, token) | `GET/PUT /users/{id}/` (admin-only)

**CMS / Nav / Forex / Analytics:** unchanged

### Auth
- Frontend: NextAuth session. Email = `session.user.email` NOT `session.email`
- Admin: `Authorization: Token <key>`
- Logout: CSRF + fetch → `/api/auth/force-logout`

### Data Shape Gotchas

| Gotcha | Detail |
|--------|--------|
| Cart item key | `item.id` |
| Availability param | `people` (not `party_size`) |
| Checkout SSR | Disabled: `dynamic(() => Promise.resolve(Index), { ssr: false })` |
| ISR revalidate | `revalidate: 300` on trip detail pages |
| Contract price params | Always THB. Frontend divides by `currentRate.rate` for display only. |
| Extra features filter | Exact DB strings: `'Free Cancellation'`, `'Instant Confirmation'`, `'Hotel Pickup'` (type=FEATURE) |
| Contract_RateCard ORM | Reverse FK ORM path = `contract_ratecard` not `contract_ratecard_set` (`_set` = Python attr only) |
| `formatCurrency(0)` | Use `value === null \|\| value === undefined` guard — `!value` returns `''` for 0 |
| Navigation API | Returns `[]` if no NavigationSection records |
| Popular Experiences | `/front-page/` → `popular_experiences[]`. 8 items, ordered `-booked_count`. |

---

## Section 4 — Architecture Guardrails

### Payment
- `finalize_payment(order)` — single source of truth. Never duplicate.
- `select_for_update()` + `payment_finalized_at` guard
- `locked_amount` — freezes charge amount after first QR
- `payment_failed` is recoverable — not terminal
- Omise sends NO webhook on PP/MB expiry
- Idempotency: SHA-256(method, amount, currency)

### DB / ORM
- Lock order: Coupon → Order → BookingItem → TimeSlot. Never invert.
- `on_delete=PROTECT` on audit-trail FKs. `db_index=True` on hot fields.
- Reverse FK ORM path: use model's `related_name` or Django default (`<model>` lowercase, no `_set`)

### Celery
- Pass IDs to tasks, not model objects.
- All tasks: `bind=True, max_retries, default_retry_delay`

### Infra
- Memory: web 512MB | celery-worker 384MB | redis 64MB = ~960MB
- `WebhookEvent.get_or_create` outside `atomic()`

### Frontend Patterns
- **Tailwind JIT:** Never interpolate into arbitrary class strings — only static strings scanned at build time
- **Currency:** `useCurrency()` → display only. API always receives THB. Pattern: `formatCurrency(value / rate, currency)`
- **Debounced inputs:** `lodash.debounce` in `useRef`, cancel on unmount. 400ms standard for filter inputs.
- **`formatCurrency(0)`:** Guard = `=== null || === undefined` not `!value`
- **PriceRangeSlider contract:** Internal values THB. Display converts via context. Never pass converted value to API.

### Header Search (2026-06-02, updated session #27)
- `HeaderSearchContext` — single source of truth. Clears only on non-shallow navigation.
- `FilterTripsPage.js` + `homepagev2.js` + `FilterDayTripsPage.js` call `setSearchBarContent()`
- `FilterDayTripsPage` passes `filters`+`updateFilter` into compact `ActivitySearch` — single state source, no dual-hook race
- `SearchDialogTrigger variant="input"` — white bg, NO left icon, `bg-fb-blue` icon-only submit, `h-10`, input `h-full`
- `PageMain` in `layout.js` — adaptive padding prevents layout gap
- `ActivitySearch` patterns: `isControlled` + `useDayTripFilters({ enabled })` + `didMountRef` + `isTypingRef`. See [[react-dual-hook-url-race]]

### Popular Routes Section (2026-05-28)
- `PopularRoutesSection.js` — NO `ContentCard` wrapper on happy path
- `Section` gets `py-6 px-4 xl:px-0`
- `ContentCard` hardcoded `bg-white` — cannot override with Tailwind

### Nav
- `NavigationSection` + `NavigationItem` — two-level hierarchy
- API cached 1hr server-side. Frontend fallback: `constants/navConfig.js`
- Migration 0010 applied locally — production needs `migrate`