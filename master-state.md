# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-01 (session #26 — ACT-12 deep debug, Option F attempted, 3 regressions found)

**Achieved this session (2026-06-01 #26):**
- **ACT-12 flicker root cause confirmed** — 3-specialist debug + scrutinize team. Kill chain: compact `ActivitySearch` mounts → calls `useDayTripFilters()` → hydration fires → `router.push({ shallow: true })` → `routeChangeStart` fires → `HeaderSearchContext` clears `setSearchBarContent(null)`. Original hypothesis (cleanup fires on re-render) was WRONG.
- **HeaderSearchContext fix applied** — `routeChangeStart` listener now checks `{ shallow }` — only clears on non-shallow navigations. `components/contexts/HeaderSearchContext.js:12`. Flicker fixed.
- **renderOption key warning fixed** — `ActivitySearch.js:102` — extracted `key` from spread props → `<li key={key} {...optionProps}>`. React 18 + MUI Autocomplete warning resolved.
- **Option F attempted (BROKEN — DO NOT COMMIT)** — added `routeChangeComplete` listener + `isPushingRef` guard to `useDayTripFilters.js`. Attempted to fix: compact search writes URL but page hook never re-hydrates. Result: 2 regressions introduced (see ACT-12 bug report below). Files modified but not committed.
- **inputValue sync fix applied (PARTIALLY BROKEN)** — `ActivitySearch.js:22–24` — `useEffect([filters.location, filters.search])` syncs `inputValue` after hydration. Fixes URL param display (e.g. `?search=samui` shows in input). But conflicts with Option F's `routeChangeComplete` re-hydration → `inputValue` overwritten mid-typing.

**Achieved this session (2026-06-01 #25):**
- CHARTER type, Phase 2+3 merged, ACT-11 mobile shipped. See prior entries.

**Achieved sessions #23–24:** Phase 1+2 activities marketplace shipped.

**Blocked / carry-forward:**
1. **ACT-12 STILL OPEN — NEW BUGS INTRODUCED** — branch `260601-feat/header-activities-search`. 4 modified files, uncommitted. See bug report in Section 4.
2. **Merge pending** — `260528-feat/header-redesign-2026` not merged to main
3. **Nav table empty** — restart backend + populate NavigationSection via admin UI
4. **Width increase deferred** — sitewide `Section.js` + all `max-w-[1200px]` pages together

**Next session resume point (EXACT):**
1. **ACT-12 — Finish header search** (PRIORITY — see full bug report Section 4)
   - Branch: `260601-feat/header-activities-search`
   - Flicker: FIXED (`HeaderSearchContext` shallow guard) ✓
   - Remaining: compact search typing/URL-param display broken. 2 regressions from Option F. REVERT `useDayTripFilters.js` Option F changes, implement Option E instead.
   - Option E: pass `filters` + `updateFilter` from page → compact via `setSearchBarContent(<ActivitySearch compact filters={filters} updateFilter={updateFilter} />)` + `useEffect` inputValue sync
2. **BW-1/BW-2/BW-3** — blog width padding fixes (small, fast)
3. **AT-1** — airport transfer P0 redesign

### Active Branches

| Repo | Branch | Last Commit |
|------|--------|-------------|
| `smartenplus-frontend` | `develop` | `f93df66` Merge activities-mobile-filters |
| `smartenplus-frontend` | `260601-feat/header-activities-search` | `1cbec0f` + 4 uncommitted changes (broken) |
| `smartenplus-backend` | `develop` | `2d5a6ee` Merge contract-locations-endpoint |
| `admin-dashboard` | `main` | `a962145` fix(timeline): new stop place.id null sentinel |
| `smartenplus-content` | `master` | `fca8ee6` init: smartenplus-content repo |

_Last verified 2026-06-01 (session wrap-up #26)_

### Uncommitted (frontend — DO NOT COMMIT YET)
- `components/contexts/HeaderSearchContext.js` — shallow guard ✓ KEEP
- `components/activities/shared/ActivitySearch.js` — renderOption key fix ✓ KEEP + inputValue sync ⚠️ REVIEW
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
| ACT-12 | **Header search — flicker FIXED, functional search BROKEN** | Flicker: `HeaderSearchContext` shallow guard ✓. Compact results: Option F failed (race + mid-type overwrite). Next: revert Option F → Option E (pass page filters+updateFilter to compact). | `hooks/useDayTripFilters.js` + `ActivitySearch.js` + `FilterDayTripsPage.js` |
| BW-1 | Blog index hero `px-4` padding | Should be `px-2 md:px-3 xl:px-0` | `pages/blog/index.js:186` |
| BW-2 | Blog index featured section `px-2 md:px-4` | Should be `px-2 md:px-3 xl:px-0` | `pages/blog/index.js:206` |
| BW-3 | BlogCard `rounded-lg` + no mx- margins | Should be `rounded-md` + `mx-2 md:mx-3 xl:mx-0` | `components/blog/BlogCard.js` |
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

### Header Search (2026-05-28)
- `HeaderSearchContext` — single source of truth
- Only `FilterTripsPage.js` + `homepagev2.js` call `setSearchBarContent()` (+ `FilterDayTripsPage.js` from session #25, bug open)
- `SearchDialogTrigger variant="input"` — white bg, NO left icon, `bg-fb-blue` icon-only submit, `h-10`, input `h-full`
- `PageMain` in `layout.js` — adaptive padding prevents layout gap

### ACT-12 Bug Report — Header Activities Search (2026-06-01, updated session #26)

**STATUS: PARTIALLY FIXED. Flicker resolved. Functional search broken. Option F introduced regressions. Next session: revert Option F, implement Option E.**

---

#### Problem 1 — Flicker (FIXED ✓)
Compact `ActivitySearch` mounts → `useDayTripFilters()` → `router.push({ shallow: true })` → `routeChangeStart` → `HeaderSearchContext` cleared.
**Fix applied:** `HeaderSearchContext.js:12` — `(_url, { shallow }) => { if (!shallow) setSearchBarContent(null); }`. Verified correct.

---

#### Problem 2 — Compact search doesn't affect page results (UNFIXED ✗)
**Root cause:** Compact `ActivitySearch` uses own `useDayTripFilters()` instance (line 13). Both instances independent — share only URL, not React state. Compact writes URL via `router.push(shallow)`. Page hook hydration deps = `[router.isReady]` — only fires once on mount. Page hook never re-reads URL after compact pushes → `useGetContractsQuery` args unchanged → results don't update.

**Option F attempted (BROKEN — REVERT):**
Added `routeChangeComplete` listener in `useDayTripFilters.js` to re-hydrate on external URL changes. `isPushingRef` guard (set during own push, cleared in `.finally()`) intended to prevent loop.

**Regression 1 — Race condition:** `router.push().finally()` resolves async. `routeChangeComplete` fires before `.finally()` in some cases → `isPushingRef.current` still `true` when listener fires → listener skips re-hydration when it shouldn't. OR fires when it should skip → re-hydrates → resets filters to URL state discarding in-flight changes.

**Regression 2 — inputValue overwrite mid-typing:** `ActivitySearch.js:22–24` `useEffect([filters.location, filters.search])` → `setInputValue(...)`. When user types: keystroke → `updateFilter('search', X)` → URL-sync push → `routeChangeComplete` → `setFilters(fromQuery)` → `filters.search` updates → sync effect → `setInputValue` overwrites what user is typing mid-keystroke. Input stutters/resets.

---

#### Problem 3 — URL param not shown in input on direct load (PARTIALLY FIXED ⚠️)
`?search=samui` in URL → `useDayTripFilters` hydrates `filters.search='samui'` → but `inputValue` initialized from DEFAULT_FILTERS (empty) before hydration. Fixed by `useEffect([filters.location, filters.search])` in `ActivitySearch.js:22`. Works on direct load. Broken mid-typing due to Regression 2 above.

---

#### Next session: implement Option E

**Revert `useDayTripFilters.js`** — remove `filtersFromQuery`, `isPushingRef`, `routeChangeComplete` listener. Restore original 2-effect structure. Keep `filtersFromQuery` as helper (clean extraction, no harm).

**Option E implementation:**
1. `FilterDayTripsPage.js:32–34` — pass page's `filters` + `updateFilter` into compact:
```js
// BEFORE:
setSearchBarContent(<ActivitySearch compact />);
// AFTER:
setSearchBarContent(<ActivitySearch compact filters={filters} updateFilter={updateFilter} />);
```
2. `ActivitySearch.js:13–15` — when `compact=true` AND props provided, use props not own hook:
```js
const ownHook = useDayTripFilters();
const filters = (compact && filtersProp) ? filtersProp : (compact ? ownHook.filters : filtersProp);
const updateFilter = (compact && updateFilterProp) ? updateFilterProp : (compact ? ownHook.updateFilter : updateFilterProp);
```
3. Keep `useEffect([filters.location, filters.search])` inputValue sync in `ActivitySearch.js` — needed for URL-param display on direct load. Safe because page's `filters` only updates on hydration or user action, not mid-keystroke.

**Why Option E is safe:** compact uses PAGE's hook — single source of truth. No second instance, no routeChangeComplete needed. `inputValue` sync effect fires on hydration only (not mid-typing) because page's `updateFilter` updates `filters` only on complete actions.

---

#### Files to change next session
| File | Action |
|------|--------|
| `hooks/useDayTripFilters.js` | Revert Option F — remove routeChangeComplete listener + isPushingRef. Keep `filtersFromQuery` helper. |
| `components/activities/browse/FilterDayTripsPage.js` | Pass `filters` + `updateFilter` to compact: `<ActivitySearch compact filters={filters} updateFilter={updateFilter} />` |
| `components/activities/shared/ActivitySearch.js` | Update lines 13–15 to prefer props when compact+props provided. Keep inputValue sync effect. |
| `components/contexts/HeaderSearchContext.js` | Already correct — keep as-is. |

### Popular Routes Section (2026-05-28)
- `PopularRoutesSection.js` — NO `ContentCard` wrapper on happy path
- `Section` gets `py-6 px-4 xl:px-0`
- `ContentCard` hardcoded `bg-white` — cannot override with Tailwind

### Nav
- `NavigationSection` + `NavigationItem` — two-level hierarchy
- API cached 1hr server-side. Frontend fallback: `constants/navConfig.js`
- Migration 0010 applied locally — production needs `migrate`
