# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-05-28 (session wrap-up #5)

**Achieved this session (2026-05-28):**
- **Header redesign Days 1–3 IMPLEMENTED** — branch `260528-feat/header-redesign-2026`, commit `a4158b0`
- 10 files changed: CartButton, ProfileButton, SearchDialogTrigger, NavDropdown, globals.css, main-header, HeaderSearchSummary, layout.js (HeaderRowsContext), StickySearchBar
- Glassmorphism fully removed. Solid white header live on branch.
- `/blog` removed from ONE_ROW_PATHS → now Type B (2-row, 96px)
- `HeaderRowsContext` exported from layout.js, consumed by StickySearchBar
- **Handoff doc created:** `01-projects/header-redesign-2026-implementation.md`
- **CLAUDE.md compressed** (caveman compress — no token savings, already lean)

**Blocked / carry-forward:**
1. **Day 4 QA pending** — regression matrix not yet run. Branch not merged to main.
2. **Frontend other uncommitted** — `HeaderSearchContext.js` (staged), `BlogPageWrapper.js`, `BlogPostDisplay.js`, `SearchCover.js`, several page files M, `HEADER_REDESIGN_2026.md` untracked (on main, not on feature branch)
3. **Backend uncommitted** — `.claude/agents/` 8 files deleted, `settings.local.json` + `CLAUDE.md` modified, `docs/n8n-webhook-resend-operator.md` untracked
4. **admin-dashboard** — `CLAUDE.md` modified, uncommitted
5. **Content repo GitHub remote** — create manually at github.com
6. **Nav table empty** — restart backend + populate NavigationSection via admin UI

**Next session resume point:**
1. **Day 4 QA** — run regression matrix from `header-redesign-2026-implementation.md`
   - Pages: `/`, `/blog`, `/destinations`, `/trips/[from]/[to]`, `/checkout`, `/login`
   - Breakpoints: 1440, 768, 375
   - Final grep: `grep -rn "text-white" components/layout/ components/search/ components/cart/ components/auth/`
2. **Merge** `260528-feat/header-redesign-2026` → main after QA passes
3. Commit backend loose files (stage selectively — skip deleted agents)
4. Commit admin-dashboard CLAUDE.md
5. Separate PRs: homepage hero height + custom font loading

### Active Branches

| Repo | Branch | Last Commit |
|------|--------|-------------|
| `smartenplus-frontend` | `260528-feat/header-redesign-2026` | `a4158b0` feat(header): replace glassmorphism with solid white adaptive header |
| `smartenplus-backend` | `main` | `2bdf31b` fix: N8N_WEBHOOK_URL default=None |
| `admin-dashboard` | `main` | `95082f3` fix(bookings): CSV export typo fixes |
| `smartenplus-content` | `master` | `fca8ee6` init: smartenplus-content repo |

_Last verified 2026-05-28_

### Uncommitted
- **frontend:** `HeaderSearchContext.js` (staged), `BlogPageWrapper.js`, `BlogPostDisplay.js`, `SearchCover.js`, `pages/airport-transfer`, `pages/destinations`, `pages/locations/*`, `pages/trips/index.js` (all M), `HEADER_REDESIGN_2026.md` (untracked)
- **backend:** `.claude/agents/` 8 files deleted, `settings.local.json` + `CLAUDE.md` modified, `docs/n8n-webhook-resend-operator.md` untracked
- **admin-dashboard:** `CLAUDE.md` modified
- **vault:** clean (updated this session)

---

## Section 2 — Loose Ends

### Open

| # | Issue | Blocker | Where |
|---|-------|---------|-------|
| 14 | 429 Too Many Requests on `/front-page/` | DONE — `c73f6de` merged + pushed to main | `pages_info/views.py` — parameterized 300s cache |
| 14b | `refetchOnMountOrArgChange: 300` in useTripData | DEFERRED — orthogonal to 429, targets /api/v1/trips/ | `hooks/useTripData.js:16,24` — open as #15 |
| 14c | `props` object in RefreshTokenHandler deps | DONE — `a797a59` merged + pushed to main | `components/auth/refreshTokenHandler.js:25` |
| 15 | `refetchOnMountOrArgChange: 300→true` in useTripData | Separate justification needed — increases anon request volume | `hooks/useTripData.js:16,24` |
| 1 | `AdminBookingSummaryViewSet` unauthenticated | Needs frontend sign-off | `orders/views.py` |
| 2 | Delete `RefundViewSet` (legacy step 7) | Waiting on zero `DEPRECATED_ENDPOINT_USED` in prod logs | `cards/views.py` |
| 3 | Remove Stripe 410 stub `/payments/stripe-webhook/` | Waiting on zero prod traffic | `payments/urls.py` |
| 8 | Forex endpoint on admin-dashboard-charge URL | Naming debt — public endpoint on admin path | `cards/urls.py` |
| Nav | NavigationSection table empty | Restart backend + populate via admin `/securelogin/pages_info/navigationsection/add/` — plain links only, no Experiences/Explore children | `pages_info` |
| Explore Thailand submenu | Needs `location_type` CharField+choices on `Location` model before rebuilding | `stations/models.py` |
| HD-1 | CurrencySelector button too small (text-xs, max-w-40px) at tablet | Low — confirmed icon-only logo helps, sizing is design debt | `CurrencySelector.js:55` |
| HD-2 | CartButton/ProfileButton dim (70% opacity) | Low — acceptable design choice | `CartButton.js:116`, `ProfileButton.js:367` |
| HD-3 | xl padding gap (px-0 vs px-3) | Low — edge case | `main-header.js:90` |
| HD-4 | Edit search text size mismatch vs CurrencySelector | Low — design debt | `SearchDialogTrigger.js:46` |
| HD-5 | Route text truncation at narrow tablets | Low — smart-wrapping resolves | `StickySearchBar.js:89` |
| HD-6 | Logo size jump mobile→desktop (text-lg→text-2xl) | P2 — separate fix | `main-header.js:66,95` |
| HD-7 | Passenger button wide at narrow tablets | Low — StickySearchBar deleted; N/A if destinations pattern used | — |

### Recently Closed (this session)
| Issue | Fix | Date |
|-------|-----|------|
| Nav Phase 0 — label renames | 5 labels updated in `main-header.js` + `layout.js`, committed + pushed | 2026-05-24 |
| Nav Phase 1 — Experiences dropdown | NavDropdown.js + navConfig.js created, committed + pushed | 2026-05-24 |
| Nav Phase 2 — Explore Thailand dropdown + URL param | `destinations/index.js` reads router.query.filter, navConfig children updated, committed + pushed | 2026-05-24 |
| Nav Phase 3 backend — NavigationSection model | Models + serializer + viewset + admin + migration applied, committed + pushed | 2026-05-25 |
| Nav Phase 3 frontend — RTK Query | navigationApi.js created + main-header.js updated with fallback, committed + pushed | 2026-05-25 |
| Bug fix — api-slice wrong import path | Corrected to `api-slice`, committed + pushed | 2026-05-25 |
| Bug fix — /api/v1 prefix missing in navApi query | Added `/api/v1/` prefix, committed + pushed | 2026-05-25 |
| Bug fix — React key in PopularRoutesCarousel | Moved key to React.Fragment wrapper, committed + pushed | 2026-05-25 |
| Bug fix — React key in CardCarouselContainer | Added key to Fragment wrapper, committed + pushed | 2026-05-25 |
| Bug fix — Missing ListModelMixin import | Added to pages_info/views.py, migration created + applied | 2026-05-25 |
| Nav 404 fixed | Explicit `path('api/v1/pages-info/navigation/')` in `apis/urls.py` before slug catch-all. `6f5286e` | 2026-05-25 |
| Frontend dead code removed | Deleted unused `navLinks` export, fixed misleading comments. `3feafaa` | 2026-05-25 |
| Header help icon removed | Deleted `main-header.js:92-98` + `HelpOutlineOutlinedIcon` import. Footer Help link preserved. | 2026-05-25 |
| Header scroll opacity inconsistency | CSS transition asymmetry fixed — added 200ms to `.glass-bg-scrolled`. Desktop header now always dark glass (no scroll toggle). | 2026-05-27 |
| NavDropdown WCAG contrast bug | `text-white/70` tokens, `py-4`, `ring-white/50` — fixes WCAG AA failure on dark glass header. `a405807` | 2026-05-27 |
| HeaderSearchContext re-render | `useMemo` on context value — stops Layout state cascading into MainHeader. `a405807` | 2026-05-27 |
| Injection effect over-firing | Removed `effectiveDepartureDate` dep — HSS reads date from Redux directly. `a405807` | 2026-05-27 |
| StickySearchBar dead code | Deleted 138-line component — never rendered, competing surface, duplicated logic. `a405807` | 2026-05-27 |

---

## Section 3 — Cross-Repo API Contract

### Endpoints

**Public:** `GET /contract/` | `GET /product-detail/{slug}/` | `GET /contract/{id}/availability/?date=YYYY-MM-DD&people=N`

**Admin:** `POST/PATCH/DELETE /admin-dashboard-operators/contract-details/{slug}/` | `POST .../copy/` | `POST /admin-dashboard-charge/manual-adjustment/`

**Cart & Order:** `POST /api/carts/{id}/cartitems/` | `PATCH .../cartitems/{item_id}/` | `DELETE .../cartitems/{item_id}/` | `POST /api/orders/` | `GET /api/orders/{id}/`

**Payment:** `POST /payments/order-charge/` | `POST /payments/webhook/` | `POST /payments/order-charge/{id}/expire/`

**User:** `GET /api/user/` (self, token) | `GET/PUT /users/{id}/` (admin-only)

**CMS:** `GET /hero-banners/` | `POST/PATCH/DELETE /hero-banners/{id}/`

**Navigation (NEW):** `GET /api/v1/pages-info/navigation/` — returns nav structure from NavigationSection/NavigationItem models

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
| Navigation API | Returns empty list `[]` if no NavigationSection records in DB. Returns 404 only if server hasn't restarted with new code. |

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

### Nav (NEW — 2026-05-25)
- `NavigationSection` + `NavigationItem` — two-level hierarchy (section → items)
- API cached 1hr server-side via Django cache
- Frontend fallback: static `constants/navConfig.js` used when API unavailable
- Migration 0010 applied locally — production needs `migrate`