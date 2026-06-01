# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-02 (session #28 — BW-1/BW-2/BW-3 verified already fixed, closed in vault)

**Achieved this session (2026-06-02 #27):**
- **ACT-12 FULLY RESOLVED** — all bugs fixed, 4 commits pushed to `260601-feat/header-activities-search`. Branch ready to merge to develop.
  - `979c45d` Option E: compact search shares page `filters`+`updateFilter`. Removed Option F (routeChangeComplete + isPushingRef). `useCallback` stable refs. `isTypingRef` mid-type guard. Category-aware `getActivityLocationsQuery`.
  - `37764cb` Debounce: reused existing `components/utils/useDebounce.jsx` (300ms). First consumer of that shared hook.
  - `39ff918` `useDayTripFilters({ enabled })` — gate URL-sync on secondary instances. `isControlled` flag in `ActivitySearch` passes `enabled: false` to ownHook → stops URL race. `didMountRef` prevents debounce mount-fire clearing URL search.
  - `5eaf8e2` MUI freeSolo Enter fix: `handleChange` string branch added — was missing → input blanked on Enter press.
- **Knowledge atomized** — `03-knowledge/react-dual-hook-url-race.md` — dual-hook URL race + `{ enabled }` + `isControlled` + `didMountRef` + freeSolo string branch patterns.

**Achieved session #26:** HeaderSearchContext shallow guard (flicker fix). Option F attempted + failed (3 regressions). All recorded in prior entry.

**Achieved sessions #23–25:** Phase 1+2+3 activities marketplace shipped. CHARTER type, mobile layout, sidebar filters.

**Carry-forward:**
1. **Merge** `260601-feat/header-activities-search` → develop (first action next session)
2. **AT-1** — airport transfer P0 redesign
3. **Nav table empty** — restart backend + populate NavigationSection via admin UI

**Next session resume point (EXACT):**
1. `git merge 260601-feat/header-activities-search` into develop, push
2. AT-1 — spec at `03-knowledge/transportation-category-audit-2026-05-30.md`

### Active Branches

| Repo | Branch | Last Commit |
|------|--------|-------------|
| `smartenplus-frontend` | `develop` | `f93df66` Merge activities-mobile-filters |
| `smartenplus-frontend` | `260601-feat/header-activities-search` | `5eaf8e2` fix: freeSolo Enter — **READY TO MERGE** |
| `smartenplus-backend` | `develop` | `2d5a6ee` Merge contract-locations-endpoint |
| `admin-dashboard` | `main` | `a962145` fix(timeline): new stop place.id null sentinel |
| `smartenplus-content` | `master` | `fca8ee6` init: smartenplus-content repo |

_Last verified 2026-06-02 (session wrap-up #27)_

### Uncommitted
None — all clean.
- `hooks/useDayTripFilters.js` — Option F routeChangeComplete ✗ REVERT
- `components/activities/browse/FilterDayTripsPage.js` — unknown changes, review before commit

---

## Section 2 — Loose Ends

### Open

| # | Issue | Blocker | Where |
|---|-------|---------|-------|
| ~~ACT-7~~ | ~~Phase 1 QA + merge~~ | ✓ Done | — |
| ~~ACT-8~~ | ~~Backend merge~~ | ✓ Done `2d5a6ee` → develop | — |
| ~~ACT-9~~ | ~~Phase 2 pre-flight (backend)~~ | ✓ Done `508949b` | — |
| ~~ACT-10~~ | ~~Phase 2 QA + merge~~ | ✓ Done `b552e55` → develop | — |
| ~~ACT-11~~ | ~~Phase 3 mobile layout~~ | ✓ Done `f93df66` → develop | — |
| ~~ACT-12~~ | ~~Header search~~ | ✓ Done `5eaf8e2` — all bugs resolved, branch ready to merge | — |
| ~~BW-1~~ | ~~Blog index hero `px-4` padding~~ | ✓ Already fixed | — |
| ~~BW-2~~ | ~~Blog index featured section `px-2 md:px-4`~~ | ✓ Already fixed | — |
| ~~BW-3~~ | ~~BlogCard `rounded-lg` + no mx- margins~~ | ✓ Already fixed | — |
| AT-2 | Airport-transfer post-calendar width mismatch | Root cause: inner margins on StationInformation + GuidesSection + ProductCardContainer. | `components/destinations/StationInformation.js` etc. |
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
- `ordering` — now also accepts `min_rate` / `-min_rate` (requires price filter to annotate)

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
