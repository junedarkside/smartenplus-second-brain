# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-05-28 (session wrap-up #9)

**Achieved this session (2026-05-28 — evening):**
- **Popular Routes — no white card bg** — removed `ContentCard` wrapper from happy-path render in `PopularRoutesSection.js`. Cards now sit directly on page bg (`#f0f2f5`). Error state still uses `ContentCard`.
- **Homepage section gaps** — `main` in `homepagev2.js`: `gap-2` → `gap-8` (32px between sections)
- **Card gaps** — `CardCarouselContainer.js`: `gap-2 p-2` → `gap-3` (12px between cards, no inner padding)
- **Popular Routes section padding** — `Section` gets `py-6 px-4 xl:px-0` — breathing room top/bottom, responsive horizontal
- **Carousel breakpoint** — `PopularRoutesCarousel.js` confirmed at `carouselBreakpoint="lg"` (reverted from earlier md attempt)
- **Section bg** — `ContentCard` `bg-transparent` attempts failed (hardcoded before className); solved by removing wrapper entirely

**Previously achieved (session #8 — afternoon):**
- SearchDialogTrigger redesign — `variant="input"`, fb-blue Search button, h-10, "Plan your Thailand journey"
- Search bar left-aligned — `main-header.js` `justify-start` + `max-w-2xl`
- Header height h-10 (40px) applied

**Previously achieved (session #7 — morning):**
- P0: Homepage sticky search — `useStickyVisibility` + `setSearchBarContent` in `homepagev2.js`
- P1: Layout height gap — `PageMain` in `layout.js`
- Empty state fix — `HeaderSearchSummary.js` guard
- Playwright audit script — `scripts/header-audit.js`

**Blocked / carry-forward:**
1. **Uncommitted** — all changes on `260528-feat/header-redesign-2026`, none committed
2. **Merge pending** — branch not merged to main
3. **Backend uncommitted** — 8 agent files deleted, `settings.local.json` + `CLAUDE.md` modified, `docs/n8n-webhook-resend-operator.md` untracked
4. **Nav table empty** — restart backend + populate NavigationSection via admin UI
5. **Deferred gaps** — GAP-3, GAP-5, GAP-6, GAP-7 — P2/P3, not blocking

**Next session resume point:**
1. **Commit frontend** — 5 logical commits:
   - `feat(header): sticky search on homepage + adaptive layout padding` → `homepagev2.js` + `layout.js`
   - `fix(header): empty state → input variant with "Plan your Thailand journey"` → `HeaderSearchSummary.js` + `SearchDialogTrigger.js`
   - `feat(header): left-align sticky search bar + constrain width` → `main-header.js`
   - `feat(homepage): popular routes — remove white card bg, fix section/card gaps` → `PopularRoutesSection.js` + `CardCarouselContainer.js` + `homepagev2.js`
   - `chore: header audit docs + Playwright script` → `docs/audits/` + `scripts/`
2. Merge `260528-feat/header-redesign-2026` → main after QA
3. Commit backend loose files (skip deleted agents — intentional)
4. **Next design task** — Popular Routes card style still uses original gradient overlay. User wants GYG-style (full-image). Data limitation: no rating/duration/category from API. Options: (a) improve text hierarchy on existing card, (b) request backend adds fields.

### Active Branches

| Repo | Branch | Last Commit |
|------|--------|-------------|
| `smartenplus-frontend` | `260528-feat/header-redesign-2026` | `96bc6f9` + uncommitted session #7–9 changes |
| `smartenplus-backend` | `main` | `2bdf31b` fix: N8N_WEBHOOK_URL default=None |
| `admin-dashboard` | `main` | `95082f3` fix(bookings): CSV export typo fixes |
| `smartenplus-content` | `master` | `fca8ee6` init: smartenplus-content repo |

_Last verified 2026-05-28 (session wrap-up #9)_

### Uncommitted — Frontend (`260528-feat/header-redesign-2026`)

| File | Change |
|------|--------|
| `components/layout/layout.js` | P1 adaptive padding (`PageMain`) |
| `components/layout/main-header.js` | `justify-start` + `max-w-2xl` |
| `components/search/HeaderSearchSummary.js` | empty state guard + `variant="input"` |
| `components/search/SearchDialogTrigger.js` | input variant redesign h-10 fb-blue |
| `components/UI/CardCarouselContainer.js` | `gap-3`, removed `p-2` |
| `lib/homepage/components/PopularRoutesSection.js` | removed ContentCard wrapper, added `py-6 px-4 xl:px-0` to Section |
| `pages/homepagev2.js` | sticky search + `gap-8` on main |
| `docs/audits/` | new: 2 design reports + screenshots |
| `scripts/header-audit.js` | new: Playwright audit script |
| `HEADER_REDESIGN_2026.md`, `HOMEPAGE_REDESIGN_2026.md`, `POPULAR_ROUTES_REDESIGN_2026.md` | untracked docs |
| Pre-existing M | `BlogPageWrapper.js`, `BlogPostDisplay.js`, `SearchCover.js`, `pages/airport-transfer`, `pages/destinations`, `pages/locations/*`, `pages/trips/index.js` |

**Backend:** 8 `.claude/agents/` deleted, `settings.local.json` + `CLAUDE.md` modified, `docs/n8n-webhook-resend-operator.md` untracked

---

## Section 2 — Loose Ends

### Open

| # | Issue | Blocker | Where |
|---|-------|---------|-------|
| PR-1 | Popular Routes card GYG-style | No rating/duration data from API — design decision needed | `components/UI/PopularRouteImageCard.js` |
| 15 | `refetchOnMountOrArgChange: 300→true` in useTripData | Separate justification needed | `hooks/useTripData.js:16,24` |
| 1 | `AdminBookingSummaryViewSet` unauthenticated | Needs frontend sign-off | `orders/views.py` |
| 2 | Delete `RefundViewSet` (legacy step 7) | Waiting on zero `DEPRECATED_ENDPOINT_USED` in prod logs | `cards/views.py` |
| 3 | Remove Stripe 410 stub | Waiting on zero prod traffic | `payments/urls.py` |
| 8 | Forex endpoint on admin-dashboard-charge URL | Naming debt | `cards/urls.py` |
| Nav | NavigationSection table empty | Restart backend + populate via admin | `pages_info` |
| Explore Thailand submenu | Needs `location_type` CharField on `Location` model | `stations/models.py` |
| HD-1 | CurrencySelector button too small at tablet | Low | `CurrencySelector.js:55` |
| HD-2 | CartButton/ProfileButton dim (70% opacity) | Low — acceptable | `CartButton.js:116`, `ProfileButton.js:367` |
| HD-3 | xl padding gap (px-0 vs px-3) | Low | `main-header.js:90` |
| HD-6 | Logo size jump mobile→desktop | P2 | `main-header.js:66,95` |
| GAP-3 | Mobile position flip relative→fixed | P2 | `main-header.js:45–77` |
| GAP-5 | Nav hidden while searching on trip page | P2 — accepted tradeoff | `main-header.js:112` |
| GAP-6 | threshold=0 abrupt snap | P3 — `useStickyVisibility(50)` one-liner | `hooks/useStickyVisibility.js:12` |
| GAP-7 | Wordmark hidden at md–xl when search active | P3 | `main-header.js:95` |

### Recently Closed (session #9)

| Issue | Fix | Date |
|-------|-----|------|
| Popular Routes white card bg | Removed ContentCard wrapper from PopularRoutesSection happy path | 2026-05-28 |
| Section gap 8px | `main gap-2` → `gap-8` in homepagev2.js | 2026-05-28 |
| Card gap 0px | `CardCarouselContainer gap-2 p-2` → `gap-3` | 2026-05-28 |
| No section padding | `Section` gets `py-6 px-4 xl:px-0` | 2026-05-28 |

### Recently Closed (sessions #7–8)

| Issue | Fix | Date |
|-------|-----|------|
| GAP-1 — Homepage search lost on scroll | P0: `useStickyVisibility` + `setSearchBarContent` | 2026-05-28 |
| GAP-2 — Header height gap (54px) | P1: `PageMain` in `layout.js` | 2026-05-28 |
| Empty state broken ` → ` | Guard `if (!from \|\| !to)` → CTA | 2026-05-28 |
| Empty state button→input redesign | `variant="input"`, h-10, fb-blue | 2026-05-28 |
| Search bar centered→left-aligned | `justify-start` + `max-w-2xl` | 2026-05-28 |
| Homepage redesign 2026 | `96bc6f9` — color tokens, Inter, DiscoverySection | 2026-05-28 |
| StickySearchBar dead code | Deleted 138-line component | 2026-05-27 |
| Header glassmorphism → solid white | `a4158b0` | 2026-05-28 |

---

## Section 3 — Cross-Repo API Contract

### Endpoints

**Public:** `GET /contract/` | `GET /product-detail/{slug}/` | `GET /contract/{id}/availability/?date=YYYY-MM-DD&people=N`

**Admin:** `POST/PATCH/DELETE /admin-dashboard-operators/contract-details/{slug}/` | `POST .../copy/` | `POST /admin-dashboard-charge/manual-adjustment/`

**Cart & Order:** `POST /api/carts/{id}/cartitems/` | `PATCH .../cartitems/{item_id}/` | `DELETE .../cartitems/{item_id}/` | `POST /api/orders/` | `GET /api/orders/{id}/`

**Payment:** `POST /payments/order-charge/` | `POST /payments/webhook/` | `POST /payments/order-charge/{id}/expire/`

**User:** `GET /api/user/` (self, token) | `GET/PUT /users/{id}/` (admin-only)

**CMS:** `GET /hero-banners/` | `POST/PATCH/DELETE /hero-banners/{id}/`

**Navigation:** `GET /api/v1/pages-info/navigation/` — returns nav structure from NavigationSection/NavigationItem models

**Forex:** `GET /admin-dashboard-charge/forex/` | `GET /admin-dashboard-charge/forex/fetch-rates/`

**Route Analytics:** `GET /admin-dashboard-routes/home/`

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
| `display_order` | Empty string → DRF rejects. Must be integer |
| Navigation API | Returns `[]` if no NavigationSection records. Returns 404 only if server not restarted with new code. |
| Popular Routes API | `/front-page/` → `home_routes[]`. Fields: `departure_station`, `arrival_station`, `lowest_price`, `operator_count`. NO rating/duration/category. |

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

### Celery
- Pass IDs to tasks, not model objects.
- All tasks: `bind=True, max_retries, default_retry_delay`

### Infra
- Memory: web 512MB | celery-worker 384MB | redis 64MB = ~960MB
- `WebhookEvent.get_or_create` outside `atomic()`

### Header Search (2026-05-28)
- `HeaderSearchContext` — single source of truth for header search content
- Only `FilterTripsPage.js` and `homepagev2.js` call `setSearchBarContent()`
- `HeaderSearchSummary` — guards `!from || !to` → renders `SearchDialogTrigger` CTA
- `SearchDialogTrigger` `variant="input"` — white bg, search icon left, "Plan your Thailand journey", `bg-fb-blue` "Search" button right, `h-10`
- `PageMain` in `layout.js` — reads context, adaptive padding prevents layout gap
- `useStickyVisibility` — IntersectionObserver, threshold=0 default
- Search bar left-aligned: `main-header.js` uses `justify-start` + `max-w-2xl`

### Popular Routes Section (2026-05-28)
- `PopularRoutesSection.js` — NO `ContentCard` wrapper on happy path. `ContentCard` only in error state.
- `Section` gets `py-6 px-4 xl:px-0` — standard section padding
- `CardCarouselContainer` — `gap-3` cards, no inner `p-2` padding
- `homepagev2.js` main — `gap-8` between all sections
- `ContentCard` has hardcoded `bg-white` before `${className}` — cannot be overridden with Tailwind. Always remove wrapper instead of patching className.

### Nav
- `NavigationSection` + `NavigationItem` — two-level hierarchy (section → items)
- API cached 1hr server-side via Django cache
- Frontend fallback: static `constants/navConfig.js` when API unavailable
- Migration 0010 applied locally — production needs `migrate`
