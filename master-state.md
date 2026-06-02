# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-02 (session #30)

**Achieved this session (#30):**
- **Price range slider fix:** `DEFAULT_MAX_PRICE_THB` raised 10,000 → 30,000 in `components/activities/browse/ExperienceSidebar.js:9`. Multi-agent team debate (Backend Architect vs Frontend Design vs UX Research) concluded 30k optimal — matches Thai activity market ceiling, preserves slider precision for 500–8k density band, no backend work needed.
- **Multi-agent debate pattern used** — 3 specialist agents debated dynamic endpoint vs 30k vs 50k. 30k won: same 1-line fix as 50k but 40% better pixel-per-THB precision for majority of inventory.
- **Frontier:** dynamic `GET /api/v1/contract/price-stats/` endpoint deferred until first product >28k THB is onboarded.

**Achieved this session (#29):**
- Backend bugfix: `min_rate` ordering crash fixed. Committed `1c94110`.
- Activities sort/filter UX redesign. Committed `8f05ab3`.
- Knowledge atomized — `03-knowledge/activities-sort-filter-ux.md`.

**Carry-forward:**
1. **Merge** `260601-feat/header-activities-search` → develop (first action next session)
2. **AT-1** — airport transfer P0 redesign
3. **Nav table empty** — restart backend + populate NavigationSection via admin UI
4. **Commit ExperienceSidebar.js** price fix (uncommitted — `M components/activities/browse/ExperienceSidebar.js`)

**Next session resume point (EXACT):**
1. Commit `ExperienceSidebar.js` price range fix on frontend `main`
2. `git merge 260601-feat/header-activities-search` into develop, push
3. AT-1 — spec at `03-knowledge/transportation-category-audit-2026-05-30.md`
4. **FAV-1** — implement favorite heart. ADR fully designed + scrutinized: `04-decisions/adr-activity-card-favorite-button.md`. Sequence: (a) backend migration + views.py (b) BookmarkButton.js (c) DayTripCard.js

### Active Branches

| Repo | Branch | Last Commit |
|------|--------|-------------|
| `smartenplus-frontend` | `main` | `d615c1e` fix(auth): session cookie — **1 uncommitted file** |
| `smartenplus-frontend` | `260601-feat/header-activities-search` | `5eaf8e2` fix: freeSolo Enter — **READY TO MERGE** |
| `smartenplus-backend` | `main` | `fcb0511` feat(bookmarks): extend BookmarkViewSet |
| `admin-dashboard` | `main` | `a962145` fix(timeline): new stop place.id null sentinel |
| `smartenplus-content` | `master` | `fca8ee6` init: smartenplus-content repo |

_Last verified 2026-06-02 (session wrap-up #30)_

### Uncommitted
- `smartenplus-frontend`: `M components/activities/browse/ExperienceSidebar.js` — price range max 10k→30k. **Commit next session.**

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
| FAV-1 | **Favorite heart on DayTripCard** | ADR fully designed + scrutinized. 4 files: migration + views.py + BookmarkButton.js + DayTripCard.js. See [[adr-activity-card-favorite-button]] | `dialogue/views.py`, `BookmarkButton.js`, `DayTripCard.js` |
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
