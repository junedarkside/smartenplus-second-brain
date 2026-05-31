# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-01 (session #16 — vault atomization)

**Achieved this session (2026-06-01 #16):**
- **Vault atomization** — extracted 5 atomic notes from fat knowledge files:
  - `airport-transfer-at1-redesign-spec` ← from `transportation-category-audit` (317→220 lines)
  - `nextjs-hydration-rules` ← from `nextjs-patterns` (128→80 lines)
  - `payment-checkout-5-principles` ← from `payment-integration` (137→110 lines)
  - `nextjs-static-path-prop-divergence` ← from `trip-detail-deep-review` (H8 extracted)
  - `designsystem-shadow-border-tokens` ← from `design-system-tokens-expansion` (105→55 lines)
  - Source notes trimmed + wikilinked. index.md updated. Vault now 93 pages. Commit `75590b9`.
- **Feature branch merged** — `260528-feat/header-redesign-2026` → `develop` (`81a8f99`). Shipped to production by user.

**Achieved this session (2026-05-31 #15):**
- **SearchDialogTrigger `variant='input'` cleanup** — 3 small UI fixes:
  - Removed left magnifier icon from input container (was redundant with blue submit btn)
  - Fixed input padding `pl-9` → `pl-3` (no icon to offset)
  - Removed "Search" text from submit button (icon-only), added `aria-label="Search"`
  - Fixed input/button height mismatch: added `h-full` to input (was `py-1.5` only, didn't fill `h-10`)
  - Commits: `ff43d3d` (icon/text cleanup) + `aea6cf0` (height fix) on `260528-feat/header-redesign-2026`

**Achieved this session (2026-05-31 #14):**
- **Blog width audit** — design-review agent audited /blog vs /activities/detail width. Root cause: blog doesn't use Section/ContentCard abstractions.
- **BlogPostDisplay.js4 fixes applied:**
  - Section wrapper: added `px-2 md:px-3 xl:px-0`
  - Article: `lg:w-2/3` → `lg:w-full`
  - Engagement bar: `px-2 md:px-4` → `px-2 md:px-3 xl:px-0`
  - Removed duplicate breadcrumb (was in both BlogPageWrapper + BlogPostDisplay)
- **Audit doc committed** `73af6e9` — `docs/width-inconsistency-audit-2026-05-30.md`

**Achieved this session (2026-05-31 #13):**
- **Homepage carousel 4-card fix** — `b104962` pushed to `260528-feat/header-redesign-2026`
  - Root cause: `xl:w-[25vw]` overflowed 1200px container (4×300+4×16=1264px)
  - Fix: `xl:w-[284px]` on `PopularRouteImageCard.js` + `ExperienceCard.js` (4×284+4×16=1200px)
  - Applies to both "Explore Popular Routes" + "Explore Experiences" carousels

**Achieved previous session (2026-05-30 #12 — back/share btn debug):**

**Achieved this session (2026-05-30 #11) — EXP-1 complete:**
- **Experiences section on homepage** — built + committed
  - Backend `4ab5771`: `PopularExperienceSerializer` (6 fields, standalone) + `_fetch_popular_experiences()` in `pages_info/views.py`. Inventory gate passed: 27 active contracts (12 DAY_TOUR + 3×5 others).
  - Frontend `f27f077`: `ExperienceCard.js` + `ExploreExperiencesSection.js` + `homepagev2.js` wired. Section renders after Popular Routes, before Reviews.
  - Both repos committed, ready for QA.

**Achieved previous session (2026-05-30 #10):**
- Experiences section design fully locked (vault research + scrutinize + grill). All grill decisions confirmed correct.

**Achieved sessions #6–9:**
- AT section redesign `1eec0aa` + `3759dc2` + AT-1 spec. Width consistency `0ebd755`. Vault structure fixed.

**Blocked / carry-forward:**
1. **Merge pending** — `260528-feat/header-redesign-2026` not merged to main (contains AT-1 spec + EXP-1 code).
2. **Backend uncommitted** — 8 agent files deleted, `settings.local.json` + `CLAUDE.md` modified, `docs/n8n-webhook-resend-operator.md` untracked. (intentional)
3. **Nav table empty** — restart backend + populate NavigationSection via admin UI.
4. **Width increase deferred** — sitewide `Section.js` + all `max-w-[1200px]` pages together.
5. **Deferred gaps** — GAP-3, GAP-5, GAP-6, GAP-7 — P2/P3, not blocking.

**Next session resume point (EXACT):**
1. **P0 — Fix blog width inconsistencies** (BW-1, BW-2, BW-3)
   - `pages/blog/index.js:186` — hero `px-4` → `px-2 md:px-3 xl:px-0`
   - `pages/blog/index.js:206` — featured section `px-2 md:px-4` → `px-2 md:px-3 xl:px-0`
   - `components/blog/BlogCard.js` — `rounded-lg` → `rounded-md` + add `mx-2 md:mx-3 xl:mx-0`
2. **P1 — Implement airport transfer professional redesign** (spec `03-knowledge/transportation-category-audit-2026-05-30.md`)
   - Backend: `products/serializers.py:696` + `:715` — add `station_name`, `iata_code`, `route_name`
   - Frontend: redesign `AirportTransferRouteCard.js` + `AirportTransferSection.js`
3. **P2 — EXP-1 QA** — verify carousel + styling in dev mode
4. After both pass QA: merge `260528-feat/header-redesign-2026` → main
5. Commit backend loose files (skip `.claude/agents/`)

### Active Branches

| Repo | Branch | Last Commit |
|------|--------|-------------|
| `smartenplus-frontend` | `develop` | `81a8f99` Merge branch '260528-feat/header-redesign-2026' into develop |
| `smartenplus-backend` | `main` | `4ab5771` feat(pages_info): add popular_experiences to frontpage API |
| `admin-dashboard` | `main` | `95082f3` fix(bookings): CSV export typo fixes |
| `smartenplus-content` | `master` | `fca8ee6` init: smartenplus-content repo |
| `vault` | `master` | (pending commit) session-end: blog width audit + partial fix |

_Last verified 2026-05-31 (session wrap-up #13)_

### Uncommitted — Frontend
`?? homepage-refinement-2026.md` — reference doc at project root, not committed intentionally.
`M components/airport-transfer/TripListingSection.js` + `M pages/airport-transfer/[slug].js` — on branch, not yet merged.

**Backend:** 8 `.claude/agents/` deleted, `settings.local.json` + `CLAUDE.md` modified, `docs/n8n-webhook-resend-operator.md` untracked. Content repo: clean.

---

## Section 2 — Loose Ends

### Open

| # | Issue | Blocker | Where |
|---|-------|---------|-------|
| BW-1 | Blog index hero `px-4` padding | Should be `px-2 md:px-3 xl:px-0` | `pages/blog/index.js:186` |
| BW-2 | Blog index featured section `px-2 md:px-4` | Should be `px-2 md:px-3 xl:px-0` | `pages/blog/index.js:206` |
| BW-3 | BlogCard `rounded-lg` + no mx- margins | Should be `rounded-md` + `mx-2 md:mx-3 xl:mx-0` | `components/blog/BlogCard.js` |
| AT-2 | Airport-transfer post-calendar width mismatch | Fix attempt (remove px/mx margins) broke layout — reverted. Root cause: inner margins on StationInformation (px-2 md:px-3, mx-3) + GuidesSection (px-2 md:px-3) + ProductCardContainer (mx-2). Next team: redesign sections as full-width wrappers with centered inner content. Full report: `03-knowledge/airport-transfer-width-audit-2026-05-30.md` | `components/destinations/StationInformation.js`, `components/destinations/GuidesSection.js`, `components/image/ProductCardContainer.js` |
| AT-1 | **Airport Transfer professional redesign** | P0. Spec complete in vault `03-knowledge/transportation-category-audit-2026-05-30.md` → "Redesign Spec". Backend: serializers.py:696 + :715. Frontend: AirportTransferRouteCard + AirportTransferSection. | `products/serializers.py`, `components/airport-transfer/AirportTransferRouteCard.js`, `lib/homepage/components/AirportTransferSection.js` |
| PR-2 | ~~Popular Routes carousel 4-card desktop fix~~ | ✓ Closed `b104962` — `xl:w-[284px]` on both card components | — |
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

### Recently Closed (sessions #9–11)

| Issue | Fix | Date |
|-------|-----|------|
| EXP-1 — Experiences section on homepage | `PopularExperienceSerializer` + `ExperienceCard` + `ExploreExperiencesSection`, 27 contracts, gate passed. Backend `4ab5771`, frontend `f27f077`. | 2026-05-30 |
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
| Popular Experiences API | `/front-page/` → `popular_experiences[]`. Fields: `id`, `name`, `slug`, `service_category`, `image` (S3 URL via imagegallery_set), `min_price` (from Contract_RateCard). 8-item limit, ordered by -booked_count. |
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
- `SearchDialogTrigger` `variant="input"` — white bg, NO left icon, "Plan your Thailand journey" placeholder, `bg-fb-blue` icon-only submit button right, `h-10`. Input `h-full` to match button height.
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
