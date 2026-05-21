# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-05-21
**Achieved this session:**
- Trip detail quick-win audit: 9/10 already done, 2 real fixes applied (`b866f6c`)
  - `console.log` → `console.warn` (line 450, getStaticProps redirect log)
  - Dead `'isr'` branch removed from `__dataSource` ternary (line 97, unreachable)
- Branch `260521-fix/trip-detail-quickwins` — committed, NOT yet merged

**In-progress / not done:**
- `260521-fix/trip-detail-quickwins` not pushed/merged yet
- Issue #1 deferred: Reviews section `bg-fb-blue` vs all others `bg-white` — needs design team decision
- Loose end #11 CLOSED — all safe quick-wins verified done or applied

**Next session resume:**
1. Push + merge `260521-fix/trip-detail-quickwins` → develop → main
2. Issue #1: Reviews section bg color — check design decision
3. Deep fixes (H1 ratecard guard, H2 ISO8601, H3 fetch timeout) — if user wants

### Active Branches

| Repo | Branch | Last Commit |
|------|--------|-------------|
| `smartenplus-frontend` | `260521-fix/trip-detail-quickwins` | `b866f6c` trip detail fixes — clean |
| `smartenplus-backend` | `main` | `3e49644` recommend-route backend — clean |
| `admin-dashboard` | `main` | `c06af90` RTK Query migration Main.js — clean |

### Uncommitted
- All 3 repos: clean

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
| 6 | Breadcrumb container duplication across 29 pages | DONE — merged to develop `61c5aeb` | All pages using StandardBreadcrumb |
| 8 | Forex endpoint on admin-dashboard-charge URL | Naming debt — public endpoint on admin path | `cards/urls.py` |
| 11 | Trip detail deep fixes: H1 ratecard guard, H2 ISO8601, H3 fetch timeout | Require testing/verification | trip-detail-deep-review-2026-05-20.md |
| 12 | PRs not opened: all 3 repos on `260520-update/recommend-route` → `develop` | Already merged directly to develop (no PR) | frontend + backend + admin-dashboard |

### Recently Closed

| Issue | Fix | Date |
|-------|-----|------|
| Trip detail `console.log` + dead `__dataSource` ternary | `b866f6c` on 260521-fix/trip-detail-quickwins | 2026-05-21 |
| Footer inner container `w-full` never applied (typo) | `06ccca1` space fix | 2026-05-21 |
| Check Your Booking: off-brand heading/icon/button colors | `0bd8762` aligned to design system | 2026-05-21 |
| Reviews error button `text-blue-600` (wrong blue) | `8048923` → `text-fb-blue` | 2026-05-21 |
| Guides "and more" link double-navigation (`<a>` + `router.push`) | `8048923` → `<Link>` | 2026-05-21 |
| Hero header stray `b` class (dead typo) | `8048923` removed | 2026-05-21 |
| Design system wrong hex values + stale button/input configs | `532b7bb` synced to reality | 2026-05-21 |
| Forum table overflow — no max-width constraint | `713468e` added max-w-[1200px] to table section + ranking aside | 2026-05-20 |
| Breadcrumb dedup — 7 different wrapper patterns across 29 pages | `61c5aeb` merged 3 commits, 16 files standardized, -22 lines | 2026-05-20 |

| Issue | Fix | Date |
|-------|-----|------|
| MUI+Tailwind CSS specificity: hero buttons white, help icon mobile | `fc307b1` sx prop + `a0e7aea` MUI Box display breakpoint | 2026-05-20 |
| Trip detail 4 fixes: breadcrumb SSR, redirect 308, scroll rAF, reviews fetch | `ec850be` — removed ssr:false, permanent:true, requestAnimationFrame, removed reviews useEffect (-26 lines) | 2026-05-20 |
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
