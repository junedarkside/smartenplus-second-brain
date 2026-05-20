# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-05-20
**Achieved this session:**
- Hydration error + infinite page refresh diagnosed and fixed (4 files)
- `PopularRoutesStructuredData.js` — `Date.now()` in render → module-level `PRICE_VALID_UNTIL` constant
- `GridComponent.js` — `renderTripItem` wrapped in `useCallback([locationImg])` → fixes `memo()` bypass
- `pages/_app.js` — removed `isClient` dual JSX tree → single `PersistGate loading={null}` tree (eliminates all-page hydration mismatch)
- `components/contexts/CurrencyContext.js` — `value` wrapped in `useMemo` → stops unnecessary consumer re-renders
- 3-agent investigation team deployed: SSR specialist + provider specialist + router specialist. Leader filtered ~40% false positives before accepting findings.

**In-progress / not committed:**
- Frontend: 9 modified/deleted files uncommitted on `260520-update/recommend-route`
- Backend: 4 modified files + 1 new migration uncommitted on same branch

**Next session resume:**
1. `npm run dev` → verify infinite refresh gone on all pages
2. If clean → commit frontend (all 9 files) + backend (4 files + migration) together
3. Open PR for `260520-update/recommend-route` → main
4. Then tackle loose end #7 (pre-existing build errors blocking clean build)

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

**Frontend** (8 modified + 1 deleted):
- `components/UI/BaseGridComponent.js` — Tailwind static COL_MAP + callback passthrough via renderItem
- `components/UI/GridComponent.js` — price/operator display + useCallback on renderTripItem
- `components/contexts/CurrencyContext.js` — useMemo on value object
- `lib/homepage/components/PopularRoutesSection.js` — locationImg=false, callbacks
- `lib/homepage/components/PopularRoutesStructuredData.js` — PRICE_VALID_UNTIL constant, Place type + price in offers
- `helpers/routeUtils.js` — fixed dead Bangkok check
- `pages/_app.js` — removed isClient dual-tree, single PersistGate tree
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
| 10 | Recommend-route: all changes uncommitted | Test `npm run dev` first, then commit | Frontend 9 files + Backend 4 files + migration |
| 11 | Recommend-route review: P2-P3 items not started | After commit + PR | See review report |

### Recently Closed

| Issue | Fix | Date |
|-------|-----|------|
| Hydration error + infinite page refresh (all pages) | 4-file fix: `Date.now()` constant, `useCallback` on renderTripItem, `_app.js` single PersistGate tree, `useMemo` on CurrencyProvider value | 2026-05-20 |
| Forex 429 Too Many Requests: double CurrencyProvider mount + anon throttle | Backend `throttle_classes = []` (`c859f3b`), frontend lifted CurrencyProvider outside ternary (`ff1f378`) | 2026-05-20 |
| Blog perf/SEO round 2: parallel fetches, mediaDetails, twitter:creator, sizes, gravatar, stable fn ref, ssr:true breadcrumb | `6b655d6` | 2026-05-20 |
| Blog HMR infinite loop: module-level require() + useEffect([blogPost]) object ref deps | `6b655d6` getDOMPurify() fn + [blogPost?.databaseId] dep | 2026-05-20 |
| Blog SEO: wrong canonical domain, Article→BlogPosting, missing fields | `0f38cf8` | 2026-05-19 |
| Breadcrumb + CategoryMenu tech debt fixed | `b27cbfb` | 2026-05-19 |
| Hero Banner CMS backend committed | `37c9177` | 2026-05-19 |

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
