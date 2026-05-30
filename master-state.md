# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-05-30 (session wrap-up #9)

**Achieved this session (2026-05-30 #9):**
- **Airport transfer page width audit** — 3-agent team (header-auditor, sections-auditor, live-verifier). Root cause: `w-full` + `max-w-[1200px]` = full viewport (max-width doesn't shrink back from 100%). Fix: explicit `w-[1200px]` on hero absolute div.
- **Width consistency fixes applied:**
  - `FeaturedImageHeader.js:121` — removed `w-full`, added `max-w-[1200px] mx-auto w-[1200px]` on absolute div
  - `TripListingSection.js:63` — added `px-2 md:px-3` to grid container
  - `StationInformation.js:15` — `sm:mx-3` → `px-2 md:px-3`
  - `GuidesSection.js:12` — `sm:mx-3` → `px-2 md:px-3`
  - `SearchAndLoading.js:7` — `px-4` → `px-2 md:px-3`
  - `[slug].js:253` — added `w-full` to breadcrumb wrapper
  - `[slug].js:257` — added `w-full` to calendar section outer
  - `[slug].js:258` — `gap-2` → `gap-1` on calendar inner
  - `TripListingSection.js:100` — added `mx-auto z-10` to outer section
- **Sort dropdown in title row** — `TripListingSection.js` now has `SortDropdown` alongside title (same row), imported directly from `SortDropDown.js`
- **AirportTransferSection hidden** from homepage — commented out in `homepagev2.js:358` pending AT-1 redesign
- **Commit `0ebd755`** — width consistency + hide airport transfer section

**Achieved this session (2026-05-30 #8) — vault optimize only, no code committed:**
- **Vault structure fixed:**
  - `04-knowledge/` rogue folder deleted → `backend-n8n-resend-webhook.md` moved to `03-knowledge/`
  - `homepage/` rogue folder deleted → `airport-transfer-redesign-2026.md` + `destinations-redesign-review.md` → `01-projects/`
  - `southeast_asia_transport_platform_direction.md` root orphan → `02-areas/`
  - `mobile-header-redesign-glassmorphism.md` → `08-archive/`
- **Index cleaned:** 3 stale DECIDED → COMPLETED, Archive section added, 3 missing entries added, stale one-liners updated, Stats 69→72
- **Known debt logged:** `01-projects/smartenplus/` subfolder (50+ files) violates flat schema — wikilinks still resolve, defer flatten to separate session

**Achieved previous session (2026-05-30 #7) — vault/research only:**
- Transport category audit (3-agent), scrutinize pass (8 corrections), professional redesign spec for AT-1 written into `03-knowledge/transportation-category-audit-2026-05-30.md`

**Achieved session (2026-05-30 #6):**
- **Airport Transfers homepage section — full redesign** (`1eec0aa`) — Backend `3759dc2` + Frontend `1eec0aa`.

**Blocked / carry-forward:**
1. **Merge pending** — `260528-feat/header-redesign-2026` not merged to main.
2. **Backend uncommitted** — 8 agent files deleted, `settings.local.json` + `CLAUDE.md` modified, `docs/n8n-webhook-resend-operator.md` untracked. (agents deletion intentional)
3. **Nav table empty** — restart backend + populate NavigationSection via admin UI.
4. **Width increase deferred** — sitewide `Section.js` + all `max-w-[1200px]` pages together.
5. **Deferred gaps** — GAP-3, GAP-5, GAP-6, GAP-7 — P2/P3, not blocking.

**Next session resume point (EXACT):**
1. **P0 — Implement airport transfer professional redesign** (spec complete in vault — no research needed)
   - Backend: `products/serializers.py:696` — add `station_name`, `iata_code` to local StationSerializer fields
   - Backend: `products/serializers.py:~715` — add `route_name` to HomeSerializer fields
   - Verify: GET `/front-page/` → `airport_routes[0]` has `station_name`, `iata_code`
   - Frontend: redesign `components/airport-transfer/AirportTransferRouteCard.js` (image card, IATA badge, gradient fallback)
   - Frontend: update `lib/homepage/components/AirportTransferSection.js` (subtitle, "View all →", mobile carousel)
   - Full spec: `03-knowledge/transportation-category-audit-2026-05-30.md` → "Redesign Spec" section
2. After redesign passes QA: merge `260528-feat/header-redesign-2026` → main
3. Commit backend loose files (skip deleted .claude/agents/)
4. QA ProfileButton + full homepage mobile
5. **Width506px question unresolved** — trips page reference showed same ~506px at same viewport. Both pages consistent. User may revisit with specific screenshot.
6. **Sort dropdown inline fix** — committed in `0ebd755`. Verify on reload.

### Active Branches

| Repo | Branch | Last Commit |
|------|--------|-------------|
| `smartenplus-frontend` | `260528-feat/header-redesign-2026` | `0ebd755` fix(homepage): width consistency + hide airport transfer section |
| `smartenplus-backend` | `main` | `3759dc2` feat(pages_info): add airport_routes to frontpage API |
| `admin-dashboard` | `main` | `95082f3` fix(bookings): CSV export typo fixes |
| `smartenplus-content` | `master` | `fca8ee6` init: smartenplus-content repo |

_Last verified 2026-05-30 (session wrap-up #8)_

### Uncommitted — Frontend
`?? homepage-refinement-2026.md` — reference doc at project root, not committed intentionally.

**Backend:** 8 `.claude/agents/` deleted, `settings.local.json` + `CLAUDE.md` modified, `docs/n8n-webhook-resend-operator.md` untracked. Content repo: clean.

---

## Section 2 — Loose Ends

### Open

| # | Issue | Blocker | Where |
|---|-------|---------|-------|
| AT-1 | **Airport Transfer professional redesign** | Spec complete in vault `03-knowledge/transportation-category-audit-2026-05-30.md` → "Redesign Spec". Backend: serializers.py:696 + :715. Frontend: AirportTransferRouteCard + AirportTransferSection. | `products/serializers.py`, `components/airport-transfer/AirportTransferRouteCard.js`, `lib/homepage/components/AirportTransferSection.js` |
| PR-2 | Popular Routes mobile carousel QA | Check card min-w, arrow buttons, scroll on real mobile | `components/UI/PopularRouteImageCard.js` |
| 15 | `refetchOnMountOrArgChange: 300→true` in useTripData | Separate justification needed | `hooks/useTripData.js:16,24` |
| 1 | `AdminBookingSummaryViewSet` unauthenticated | Needs frontend sign-off | `orders/views.py` |
| 2 | Delete `RefundViewSet` (legacy step 7) | Waiting on zero `DEPRECATED_ENDPOINT_USED` in prod logs | `cards/views.py` |
| 3 | Remove Stripe 410 stub | Waiting on zero prod traffic | `payments/urls.py` |
| 8 | Forex endpoint on admin-dashboard-charge URL | Naming debt | `cards/urls.py` |
| Nav | NavigationSection table empty | Restart backend + populate via admin | `pages_info` |
| Explore Thailand submenu | Needs `location_type` CharField on `Location` model | `stations/models.py` |
| HD-1 | CurrencySelector button too small at tablet | Low | `CurrencySelector.js:55` |
| HD-2 | CartButton dim (70% opacity) | Low — acceptable | `CartButton.js:116` _(ProfileButton.js:367 ref stale — file restructured `dac7e66`)_ |
| HD-3 | xl padding gap (px-0 vs px-3) | Low | `main-header.js:90` |
| HD-6 | Logo size jump mobile→desktop | P2 | `main-header.js:66,95` |
| GAP-3 | Mobile position flip relative→fixed | P2 | `main-header.js:45–77` |
| GAP-5 | Nav hidden while searching on trip page | P2 — accepted tradeoff | `main-header.js:112` |
| GAP-6 | threshold=0 abrupt snap | P3 — `useStickyVisibility(50)` one-liner | `hooks/useStickyVisibility.js:12` |
| GAP-7 | Wordmark hidden at md–xl when search active | P3 | `main-header.js:95` |

### Recently Closed (sessions #9–10)

| Issue | Fix | Date |
|-------|-----|------|
| Popular Routes card GYG-style | Split-card: image 180px top, white panel below, location label + title + operators + price | 2026-05-28 |
| Popular Routes white section bg | Removed ContentCard wrapper from PopularRoutesSection happy path | 2026-05-28 |
| Section gap 8px | `main gap-2` → `gap-8` | 2026-05-28 |
| Card gap 0px | `CardCarouselContainer gap-2 p-2` → `gap-3 items-start` | 2026-05-28 |
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
| Airport Routes API | `/front-page/` → `airport_routes[]`. Same shape as `home_routes`. Currently `departure_station` = `{location: {location_name}, slug}` only — NO `station_name`, NO `iata_code`. **Planned (AT-1):** expand local `StationSerializer` at `products/serializers.py:696` to add `station_name` + `iata_code`. HomeSerializer at :715 to add `route_name`. |

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
