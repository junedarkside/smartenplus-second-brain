# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-05-19
**Achieved this session:**
- UI consistency commit `911df1d`: 41 files — blog pages, breadcrumbs consolidated (BlogBreadcrumbs deleted), AccountLayout simplified, ~20 listing pages updated
- Breadcrumb + CategoryMenu audit: tech debt identified and fixed (icon, label, alignment, spacing)
- Breadcrumb alignment fix `b27cbfb`: Typography display inline, blog padding standardized `px-2 md:px-4`, CategoryMenu AppsIcon + unified label
- CategoryMenu UX: PlaylistAddIcon → AppsIcon, "Cats" mobile label → single "Categories"
- StandardBreadcrumb cleanup: removed redundant inline styles, padding moved to py-2 only
- BlogPageWrapper: padding moved to container for breadcrumb + CategoryMenu alignment

**In-progress / not committed:** Admin dashboard HeroBanner UI untracked (components/heroBanners/, pages/routemanagement/hero-banners/, store/api/heroBannersApi.js).
**Next session resume:** Implement remaining blog design audit gaps (L1 hero→content spacing, L2 featured post weight, U1 Load More CTA). Commit admin HeroBanner UI. Fix pre-existing build errors (calculateAge import, getStaticProps re-export).

### Active Branches

| Repo | Branch | Last Commit |
|------|--------|-------------|
| `smartenplus-backend` | `260519-update/product-feature` | `37c9177` feat(pages_info): add HeroBanner CMS model and CRUD endpoint |
| `smartenplus-frontend` | `260519-update/product-feature` | `b27cbfb` fix: breadcrumb alignment, CategoryMenu UX, and blog spacing consistency |
| `admin-dashboard` | `260519-update/product-feature` | `b4825d7` update |

### Uncommitted (frontend)

```
M .claude/settings.local.json
```

### Uncommitted (admin-dashboard)

```
M  components/sidemenu/menuData.js
M  store/index.js
?? components/heroBanners/
?? pages/routemanagement/hero-banners/
?? store/api/heroBannersApi.js
```

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

### Recently Closed

| Issue | Fix | Date |
|-------|-----|------|
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
