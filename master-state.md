# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-05-20
**Achieved this session:**
- Forex 429 fix: backend `throttle_classes = []` on `OmiseForexViewSet` (`c859f3b`) + frontend CurrencyProvider deduplicated mount + dead import removed (`ff1f378`)
- Specialist team (backend-reviewer, frontend-reviewer) verified root causes: double-mount from `isClient` ternary, anon throttle 500/hr, no auth token
- Custom TTL cache rejected — project uses RTK Query for API caching, not hand-rolled TTL
- Admin HeroBanner UI committed + pushed (`d3194d8`) — CRUD page, form, RTK Query API
- Recommend-route review: 3-agent team audited backend, frontend, validation gaps. 20 items found across P0-P3.
- Backend changes (uncommitted): HomeSerializer extended (slug, query_count, lowest_price, operator_count), HomeViewSet active contract filter, Celery beat schedule for query_count (weekly), db_index migration
- Frontend changes (uncommitted): GridComponent price/operator display, BaseGridComponent Tailwind fix + callback passthrough, PopularRoutesSection fixes, deleted dead OptimizedPopularRoutesGrid, deduplicated route constants, structured data fix, routeUtils dead code fix

**In-progress / not committed:**
- Backend: 4 modified files + 1 new migration (all uncommitted on `260520-update/recommend-route`)
- Frontend: 7 modified/deleted files (all uncommitted on `260520-update/recommend-route`)

**Next session resume:** Frontend hydration error still occurring on `npm run dev` after popular routes changes. Causes infinite page refresh. Root cause likely in BaseGridComponent or GridComponent changes. Files: `BaseGridComponent.js`, `GridComponent.js`, `PopularRoutesSection.js`. Backend changes verified working — API returns new fields correctly.

### Active Branches

| Repo | Branch | Last Commit |
|------|--------|-------------|
| `smartenplus-backend` | `260520-update/recommend-route` | `c859f3b` fix: exempt OmiseForexViewSet from throttle |
| `smartenplus-frontend` | `260520-update/recommend-route` | `ff1f378` fix: forex 429 — deduplicate CurrencyProvider mount |
| `admin-dashboard` | `260520-update/recommend-route` | `d3194d8` feat: Hero Banner CMS admin dashboard |

### Uncommitted

**Backend** (4 modified + 1 new migration):
- `Smartenplus/celery.py` — added weekly `update-route-query-counts` beat schedule
- `products/serializers.py` — HomeSerializer: slug, query_count, lowest_price, operator_count
- `products/views.py` — HomeViewSet: price/operator annotations + active contract filter
- `products/models.py` — `db_index=True` on Route.query_count
- `products/migrations/0008_add_query_count_index.py` — new migration

**Frontend** (6 modified + 1 deleted):
- `components/UI/BaseGridComponent.js` — Tailwind static COL_MAP + callback passthrough via renderItem
- `components/UI/GridComponent.js` — price/operator display + article click/hover handlers
- `lib/homepage/components/PopularRoutesSection.js` — reverted require() fix, locationImg=false, callbacks
- `lib/homepage/components/PopularRoutesStructuredData.js` — Place type + price in offers
- `helpers/routeUtils.js` — fixed dead Bangkok check
- `pages/trips/[...slug].js` — imports PROVEN_POPULAR_ROUTES from routeConstants
- `lib/homepage/components/OptimizedPopularRoutesGrid.js` — DELETED (dead code)

---

## Section 2 — Loose Ends

### Open

| # | Issue | Blocker | Where |
|---|-------|---------|-------|
| 1 | `AdminBookingSummaryViewSet` unauthenticated | Needs frontend sign-off | `orders/views.py` |
| 2 | Delete `RefundViewSet` (legacy step 7) | Waiting on zero `DEPRECATED_ENDPOINT_USED` in prod logs | `cards/views.py` |
| 3 | Remove Stripe 410 stub `/payments/stripe-webhook/` | Waiting on zero prod traffic | `payments/urls.py` |
| 4 | `locked_amount` missing `CheckConstraint` + index | Tech debt — migration `0039` not created | `orders/models.py` |
| 5 | Blog index: remaining design audit gaps (hero spacing, featured post weight, Load More CTA) | Ready to implement | `pages/blog/index.js` + `components/blog/BlogCard.js` |
| 6 | Breadcrumb container duplication across 29 pages | Tech debt — 7 different wrapper patterns | All pages using StandardBreadcrumb |
| 7 | Pre-existing build errors: `calculateAge` import + `getStaticProps` re-export | Blocks clean build | `helpers/checkout/passengerValidationHelper.js`, `pages/trips/detail/index.js` |
| 8 | Forex endpoint on admin-dashboard-charge URL | Naming debt — public endpoint on admin path | `cards/urls.py` |
| 9 | Frontend hydration error + infinite refresh after popular routes changes | Blocks recommend-route feature | `BaseGridComponent.js`, `GridComponent.js`, `PopularRoutesSection.js` |
| 10 | Recommend-route backend changes uncommitted | Needs frontend fix first | `products/views.py`, `products/serializers.py`, `Smartenplus/celery.py` |
| 11 | Recommend-route review: P2-P3 items not started | After hydration fix | See review report |

### Recently Closed

| Issue | Fix | Date |
|-------|-----|------|
| Forex 429 Too Many Requests: double CurrencyProvider mount + anon throttle | Backend `throttle_classes = []` (`c859f3b`), frontend lifted CurrencyProvider outside ternary (`ff1f378`) | 2026-05-20 |
| Blog perf/SEO round 2: parallel fetches, mediaDetails, twitter:creator, sizes, gravatar, stable fn ref, ssr:true breadcrumb | `6b655d6` | 2026-05-20 |
| Blog HMR infinite loop: module-level require() + useEffect([blogPost]) object ref deps | `6b655d6` getDOMPurify() fn + [blogPost?.databaseId] dep | 2026-05-20 |
| Blog SEO: wrong canonical domain, Article→BlogPosting, missing fields | `0f38cf8` getSiteUrl(), schema fixes, og:locale, robots meta | 2026-05-19 |
| Blog perf: LCP (featured card lazy), CLS (no aspect ratio), useMemo, ISR | `0f38cf8` priority prop, aspect-video, useMemo([posts]), revalidate 300 | 2026-05-19 |
| Breadcrumb + CategoryMenu tech debt fixed | `b27cbfb` alignment, icon, label, spacing consistency | 2026-05-19 |
| UI consistency across 41 files committed | `911df1d` blog, breadcrumbs, AccountLayout, listing pages | 2026-05-19 |
| Hero Banner CMS backend committed | `37c9177` feat(pages_info): FileField+AVIF fix, /hero-banners/ CRUD | 2026-05-19 |
| Contract_TranspotComposit crash (sentinel id=-1) | `id <= 0` → `create()`, positive → `get_or_create()` | 2026-05-19 |
| Expiry notification not sent | `_send_payment_failed_notifications` added to 3 expiry paths | 2026-05-18 |
| PromptPay expire → 503/409 loop | Trust `.expire()` result, no re-fetch. `ExpirePendingChargeView` | 2026-05-16 |
| Method-switch → 409 (C3 before C3b) | C3b runs first, resets `locked_amount` | 2026-05-16 |

---

## Section 3 — Cross-Repo API Contract

### Endpoints

**Public:** `GET /contract/` | `GET /product-detail/{slug}/` | `GET /contract/{id}/availability/?date=YYYY-MM-DD&people=N`

**Admin:** `POST/PATCH/DELETE /admin-dashboard-operators/contract-details/{slug}/` | `POST .../copy/` | `POST /admin-dashboard-charge/manual-adjustment/` `{order_id_str, amount, reason, note, extra_item_slug}`

**Cart & Order:** `POST /api/carts/{id}/cartitems/` | `PATCH .../cartitems/{item_id}/` | `DELETE .../cartitems/{item_id}/` | `POST /api/orders/` | `GET /api/orders/{id}/`

**Payment:** `POST /payments/order-charge/` | `POST /payments/webhook/` | `POST /payments/order-charge/{id}/expire/` | `GET /payments/docs/` (staff only)

**User:** `GET /api/user/` (self, token) | `GET/PUT /users/{id}/` (admin-only, since 2026-05-07)

**CMS:** `GET /hero-banners/` (injected into `/front-page/`) | `POST/PATCH/DELETE /hero-banners/{id}/`

**Forex:** `GET /admin-dashboard-charge/forex/` (public, throttle_classes=[], 11 rows) | `GET /admin-dashboard-charge/forex/fetch-rates/` (admin/staff only)

### Auth

- Frontend: NextAuth session. Email = `session.user.email` NOT `session.email` (common bug)
- Admin: `Authorization: Token <key>`
- Logout: CSRF + fetch → `/api/auth/force-logout` (302). Never use NextAuth `signOut()`.

### Data Shape Gotchas

| Gotcha | Detail |
|--------|--------|
| Cart item key | `item.id` (`stable_id` removed 2026-02-13) |
| Availability param | `people` (not `party_size`) |
| Checkout sort | Chronological by `traveling_date` across ALL steps |
| Checkout SSR | Disabled: `dynamic(() => Promise.resolve(Index), { ssr: false })` |
| ISR revalidate | `revalidate: 300` on trip detail pages |
| `display_order` | Empty string → DRF rejects. Must be integer in FormData |
| HeroBanner field | `FileField` not `ImageField` — Pillow 9.3.0 rejects AVIF |
| Forex throttle | Exempt `throttle_classes = []` — public read-only, 11 rows |

### Payment Constants

**Gateway:** Omise only (Stripe dropped 2026-05-15)

**OmiseMethod:** `promptpay` `credit_card` `internet_banking_{scb,ktb,kbank,bbl,bay,tmb,gsb}` `alipay` `alipay_cn` `alipay_hk` `truemoney` `line_pay` `kakao_pay` `wechat_pay`

**REDIRECT_METHODS:** all above except `promptpay`

**Expiry:** PromptPay + mobile banking = 10 min | E-wallets = no TTL (reconcile after 30 min stale) | Card = no expiry

**Order statuses:** `ordering` → `{paid,canceled,processing}` | `payment_pending` → `{ordering,paid,canceled,payment_failed}` | `payment_failed` → `{ordering,canceled}` | `paid` → `{refunded,partial_refunded,canceled}`

**GatewayCharge statuses:** `pending` `processing` `paid` `failed` `expired` `refunded` `partial_refunded`

---

## Section 4 — Architecture Guardrails

### Payment
- `finalize_payment(order)` in `payments/services.py` — single source of truth. Never duplicate.
- `select_for_update()` + `payment_finalized_at` guard — idempotent, race-safe. Don't bypass.
- Charge creation order: **C3b** (expire stale PP, reset `locked_amount`) → **C3** (block pending redirect) → **Fix3** (enforce `locked_amount`) → idempotency → `create_charge()`
- `locked_amount` — freezes charge amount after first QR. Reset on expire or method-switch.
- `payment_failed` is recoverable — not terminal.
- Omise sends NO webhook when PP/mobile banking expire. All 3 expiry paths must call `_send_payment_failed_notifications()`.
- Idempotency: SHA-256(method, amount, currency). Mismatch → expire old → fresh. Already-paid → 409.

### DB / ORM
- Lock order: **Coupon → Order → BookingItem → TimeSlot**. Never invert.
- `on_delete=PROTECT` on audit-trail FKs. `db_index=True` on hot filter/sort fields.
- `select_related`/`prefetch_related` — avoid N+1.

### Celery
- Pass IDs to tasks, not model objects.
- All tasks: `bind=True, max_retries, default_retry_delay`. Backoff: `min(60 * (2 ** retries), 3600)`.
- High-risk tasks (email, booking confirm) guard via `UserJourneyEvent` dedup.

### Infra
- Never touch `docker-compose-rds.yml` unless explicitly asked.
- Memory: web 512MB | celery-worker 384MB | celery-beat 64MB | redis 64MB | nginx 64MB = ~1088MB
- `WebhookEvent.get_or_create` outside `atomic()` — must survive rollback.

### Heal Commands

```python
Order.objects.filter(id=o.id).update(payment_finalized_at=None); finalize_payment(o)
Order.objects.filter(order_id='XXX').update(locked_amount=None)
```
