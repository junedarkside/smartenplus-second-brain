# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-05-28 (session wrap-up #7)

**Achieved this session (2026-05-28):**
- **Header search bar audit** — Playwright live metrics, 10 screenshots, 7 gaps found + documented (`docs/audits/header-searchbar-ux-audit.md`)
- **P0 fix** — Homepage sticky search: `pages/homepagev2.js` injects `HeaderSearchSummary` into header when `DiscoverySection` scrolls out. Same pattern as trip page. Reused `useStickyVisibility` + `useHeaderSearch` + `HeaderSearchSummary` — zero new components.
- **P1 fix** — Layout height gap: `components/layout/layout.js` — new `PageMain` component reads `searchBarContent` from context, toggles `md:pt-[48px]` vs `md:pt-[96px]` with `transition-[padding-top] duration-150`. No white gap when header collapses.
- **Empty state fix** — `components/search/HeaderSearchSummary.js` — guard `if (!from || !to)` renders `SearchDialogTrigger` "Search trips" CTA. Prevents broken ` → ` output for fresh users. Design report at `docs/audits/header-searchbar-empty-state-design.md`.
- **Playwright audit script** — `scripts/header-audit.js` — reusable, captures metrics + screenshots across homepage + trip page, desktop (1280px) + mobile (390px), 3 scroll states.

**Blocked / carry-forward:**
1. **Uncommitted** — all session changes on `260528-feat/header-redesign-2026`, none committed yet
2. **Merge pending** — branch not merged to main
3. **Backend uncommitted** — 8 agent files deleted, `settings.local.json` + `CLAUDE.md` modified, `docs/n8n-webhook-resend-operator.md` untracked
4. **admin-dashboard** — `CLAUDE.md` modified, uncommitted
5. **Nav table empty** — restart backend + populate NavigationSection via admin UI
6. **Deferred gaps** — GAP-3 (mobile position flip), GAP-5 (nav hidden), GAP-6 (threshold), GAP-7 (wordmark) — P2/P3, not blocking

**Next session resume point:**
1. Commit frontend in 3 logical commits:
   - `feat(header): sticky search on homepage + adaptive layout padding` → `homepagev2.js` + `layout.js`
   - `fix(header): empty state CTA in HeaderSearchSummary` → `HeaderSearchSummary.js`
   - `chore: header audit docs + Playwright script` → `docs/audits/` + `scripts/`
2. Run `node scripts/header-audit.js` (check active port first — was 3002 last session)
3. Merge `260528-feat/header-redesign-2026` → main after QA
4. Commit backend loose files (skip deleted agents — intentional)
5. Commit admin-dashboard `CLAUDE.md`

### Active Branches

| Repo | Branch | Last Commit |
|------|--------|-------------|
| `smartenplus-frontend` | `260528-feat/header-redesign-2026` | `96bc6f9` feat(homepage): redesign 2026 (+ uncommitted changes this session) |
| `smartenplus-backend` | `main` | `2bdf31b` fix: N8N_WEBHOOK_URL default=None |
| `admin-dashboard` | `main` | `95082f3` fix(bookings): CSV export typo fixes |
| `smartenplus-content` | `master` | `fca8ee6` init: smartenplus-content repo |

_Last verified 2026-05-28 (session wrap-up #7)_

### Uncommitted

**frontend (`260528-feat/header-redesign-2026`):**
- `components/layout/layout.js` — P1 adaptive padding (`PageMain`)
- `components/search/HeaderSearchSummary.js` — empty state CTA guard
- `pages/homepagev2.js` — P0 sticky search injection
- `docs/audits/` — new: 2 design reports + 10 screenshots
- `scripts/header-audit.js` — new: Playwright audit script
- `HEADER_REDESIGN_2026.md`, `HOMEPAGE_REDESIGN_2026.md` — untracked docs
- Pre-existing M: `BlogPageWrapper.js`, `BlogPostDisplay.js`, `SearchCover.js`, `pages/airport-transfer`, `pages/destinations`, `pages/locations/*`, `pages/trips/index.js`

**backend:** 8 `.claude/agents/` deleted, `settings.local.json` + `CLAUDE.md` modified, `docs/n8n-webhook-resend-operator.md` untracked

**admin-dashboard:** `CLAUDE.md` modified

---

## Section 2 — Loose Ends

### Open

| # | Issue | Blocker | Where |
|---|-------|---------|-------|
| 15 | `refetchOnMountOrArgChange: 300→true` in useTripData | Separate justification needed — increases anon request volume | `hooks/useTripData.js:16,24` |
| 1 | `AdminBookingSummaryViewSet` unauthenticated | Needs frontend sign-off | `orders/views.py` |
| 2 | Delete `RefundViewSet` (legacy step 7) | Waiting on zero `DEPRECATED_ENDPOINT_USED` in prod logs | `cards/views.py` |
| 3 | Remove Stripe 410 stub `/payments/stripe-webhook/` | Waiting on zero prod traffic | `payments/urls.py` |
| 8 | Forex endpoint on admin-dashboard-charge URL | Naming debt — public endpoint on admin path | `cards/urls.py` |
| Nav | NavigationSection table empty | Restart backend + populate via admin `/securelogin/pages_info/navigationsection/add/` | `pages_info` |
| Explore Thailand submenu | Needs `location_type` CharField+choices on `Location` model | `stations/models.py` |
| HD-1 | CurrencySelector button too small at tablet | Low | `CurrencySelector.js:55` |
| HD-2 | CartButton/ProfileButton dim (70% opacity) | Low — acceptable | `CartButton.js:116`, `ProfileButton.js:367` |
| HD-3 | xl padding gap (px-0 vs px-3) | Low | `main-header.js:90` |
| HD-6 | Logo size jump mobile→desktop | P2 | `main-header.js:66,95` |
| GAP-3 | Mobile position flip relative→fixed (scroll jump risk) | P2 — needs real-browser scroll test | `main-header.js:45–77` |
| GAP-5 | Nav fully hidden while searching on trip page | P2 — accepted tradeoff, design debt | `main-header.js:112` |
| GAP-6 | threshold=0 abrupt snap | P3 — `useStickyVisibility(50)` one-liner | `hooks/useStickyVisibility.js:12` |
| GAP-7 | Wordmark hidden at md–xl when search active | P3 — confirm xl breakpoint value | `main-header.js:95` |

### Recently Closed (this session)

| Issue | Fix | Date |
|-------|-----|------|
| GAP-1 — Homepage search lost on scroll | P0: `useStickyVisibility` + `setSearchBarContent` in `homepagev2.js` | 2026-05-28 |
| GAP-2 — Header height gap (54px) on search activate | P1: `PageMain` in `layout.js`, adaptive `md:pt` + transition | 2026-05-28 |
| Empty state broken ` → ` in `HeaderSearchSummary` | Guard `if (!from \|\| !to)` → "Search trips" CTA | 2026-05-28 |
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

### Header Search (NEW — 2026-05-28)
- `HeaderSearchContext` — single source of truth for header search content
- Only `FilterTripsPage.js` and `homepagev2.js` call `setSearchBarContent()`
- `HeaderSearchSummary` — guards `!from || !to` → renders CTA, never broken ` → `
- `PageMain` in `layout.js` — reads context, adaptive padding prevents layout gap
- `useStickyVisibility` — IntersectionObserver, threshold=0 default, reused across both pages

### Nav
- `NavigationSection` + `NavigationItem` — two-level hierarchy (section → items)
- API cached 1hr server-side via Django cache
- Frontend fallback: static `constants/navConfig.js` when API unavailable
- Migration 0010 applied locally — production needs `migrate`
