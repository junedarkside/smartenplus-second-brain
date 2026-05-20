# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-05-20
**Achieved this session:**
- Deleted `main_js_pattern_review.md` from admin-dashboard (untracked reviewer artifact)
- Fixed build error #7 (`96c9c10`): exported `calculateAge` in `helpers/dateHelper.js`, replaced `pages/trips/detail/index.js` dead re-export with single `export { default }`
- Removed unnecessary `ssr: false` from `DynamicReviewListByProduct` (`3f948bf`): reviews now SSR'd + crawlable
- Blog index #5 partial (`1e34601`): H1 visible on mobile + Load More filled button (featured post style skipped by user)
- HMR hot-update 404 fix (`b56d62a`): `next.config.js` Cache-Control narrowed from `/_next/static/(.*)` to `/_next/static/(chunks|css)/(.*)` — webpack hot-update files no longer cached as immutable

**In-progress / not done:**
- PRs not opened yet for all 3 repos on `260520-update/recommend-route` (user skipped — do via GitHub web)

**Next session resume:**
1. Open PRs: `260520-update/recommend-route` → `develop` on all 3 repos (GitHub web UI)
2. Loose end #6: breadcrumb dedup — plan ready in `03-knowledge/breadcrumb-dedup-plan-2026-05-20.md`. New branch `260520-refactor/breadcrumb-dedup`. GROUP B first (10 files), then C (4), then D (2). 3 commits.

### Active Branches

| Repo | Branch | Last Commit |
|------|--------|-------------|
| `smartenplus-backend` | `260520-update/recommend-route` | `3e49644` feat: recommend-route backend |
| `smartenplus-frontend` | `260520-update/recommend-route` | `b56d62a` fix: HMR Cache-Control + blog index fixes |
| `admin-dashboard` | `260520-update/recommend-route` | `c06af90` refactor: dashboard Main.js RTK Query migration |

### Uncommitted
All repos clean.

---

## Section 2 — Loose Ends

### Open

| # | Issue | Blocker | Where |
|---|-------|---------|-------|
| 1 | `AdminBookingSummaryViewSet` unauthenticated | Needs frontend sign-off | `orders/views.py` |
| 2 | Delete `RefundViewSet` (legacy step 7) | Waiting on zero `DEPRECATED_ENDPOINT_USED` in prod logs | `cards/views.py` |
| 3 | Remove Stripe 410 stub `/payments/stripe-webhook/` | Waiting on zero prod traffic | `payments/urls.py` |
| 4 | `locked_amount` missing `CheckConstraint` + index | Tech debt — migration `0039` not created | `orders/models.py` |
| 5 | Blog index: featured post visual weight (user chose as-is for now) | Deferred by user | `components/blog/BlogCard.js` variant="featured" |
| 6 | Breadcrumb container duplication across 29 pages | Tech debt — 7 different wrapper patterns | All pages using StandardBreadcrumb |
| 8 | Forex endpoint on admin-dashboard-charge URL | Naming debt — public endpoint on admin path | `cards/urls.py` |
| 11 | Recommend-route review: P2-P3 items not started | After PR merged | See review report |
| 12 | PRs not opened: all 3 repos on `260520-update/recommend-route` → `develop` | Open via GitHub web UI | frontend + backend + admin-dashboard |

### Recently Closed

| Issue | Fix | Date |
|-------|-----|------|
| Build errors #7 + ssr:false #13 | `96c9c10` export calculateAge + simplify detail/index.js; `3f948bf` remove ssr:false ReviewListByProduct | 2026-05-20 |
| main_js_pattern_review.md deleted | rm untracked reviewer artifact from admin-dashboard | 2026-05-20 |
| Recommend-route uncommitted (#10) | frontend `2434124` + backend `3e49644` committed; PRs not yet opened | 2026-05-20 |
| Trip detail 16 fixes: quick-wins + deferred deep issues | `3f35d8c` (10 safe fixes) + `0bf038d` (6 deferred) — dead imports, GTM, useMemo, ISO8601 schema, domainURL, title/desc, noindex | 2026-05-20 |
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

**Route Analytics:** `GET /admin-dashboard-routes/home/` (paginated, returns slug, query_count, lowest_price, operator_count)

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
