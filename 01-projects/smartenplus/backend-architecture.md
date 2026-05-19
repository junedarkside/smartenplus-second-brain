# SmartEnPlus — Backend Architecture

## Summary
Django 4.2 REST API. 14 apps. PostgreSQL 14 + Redis 7.2 + Celery. Omise-only payments. `finalize_payment()` in `payments/services.py` is single source of truth for payment completion.

## Stack

| Layer | Tech |
|-------|------|
| Framework | Django 4.2.16 + DRF |
| Database | PostgreSQL 14 |
| Cache/Broker | Redis 7.2 |
| Background | Celery + Beat |
| Storage | AWS S3 (media) + SES (email) |
| Payments | Omise (Thai methods only) |
| Realtime | Django Channels |
| Deploy | Docker + nginx |

## App Structure

| App | Purpose | Key Models |
|-----|---------|-----------|
| accounts | Users | Account, LoggedInUser, FamilyAndFriend |
| operators | Services & contracts | Operator, Contract, TimeSlot, ContractAddon, StopSaleDate |
| products | Routes & trips | Route, Trip, TripInfo |
| stations | Locations | Station, Location, Place, Image, Timeline |
| bookings | Reservations | BookingItem, BookingItemAddon, BookingPassengerDetail |
| carts | Shopping cart | Cart, CartItem, CartItemAddon, NumberPassenger |
| orders | Order management | Order, Payment, Coupon, PassengerDetail, WebhookEvent |
| payments | Payment processing | GatewayCharge, IdempotencyKey, Refund, ManualAdjustment |
| billings | Billing | BillingProfile, PaymentMethod |
| cards | Legacy charges (read-only) | Card, Charge, Refund, ForexData |
| journeys | Analytics | UserJourneyEvent |
| tickets | Support | Ticket |
| dialogue | Social | Comment, Review, Thread, Post |
| pages_info | CMS | Category, PageInfo, TermsAndConditions |

## Key Models

### Order (`orders`)
Statuses: `ordering → payment_pending → paid | payment_failed → canceled | processing → refunded | partial_refunded`. Key fields: `payment_finalized_at` (idempotency guard), `locked_amount` (charge freeze), `payment_notification_sent_at` (dedup). Transitions enforced in `clean()` only — admin saves, not runtime `.save()`.

### GatewayCharge (`payments`)
Domain statuses: `pending / processing / paid / failed / expired / refunded / partial_refunded`. Links to Order via FK. One pending redirect charge per order (DB constraint). Fields: `gateway_charge_id`, `authorize_uri`, `qr_code_uri`, `expires_at`.

### BookingItem (`bookings`)
Statuses: `Pending → Confirmed → No Show | Partially Refund | Fully Refund | Canceled`. Linked to Order, Contract, CartItem. Terminal states locked in `clean()`.

### Supporting Models
- **IdempotencyKey** — SHA-256(method, amount, currency). Prevents duplicate charges.
- **WebhookEvent** — Raw Omise event payload. Saved outside atomic block for audit survival.
- **Coupon** — Percentage or fixed discount. `times_used` counter. Per-user and new-user-only restrictions.
- **ManualAdjustment** — Replaces legacy `ExtraItemAction`. `{ order_id_str, amount, reason, note, extra_item_slug }`. Staff-only.

## API Endpoints

**Public:**
- `GET /contract/` — list contracts
- `GET /product-detail/{slug}/` — tour details
- `GET /contract/{id}/availability/?date=YYYY-MM-DD&people=N` — availability

**Payments:**
- `POST /payments/order-charge/` — initiate charge
- `POST /payments/webhook/` — Omise events
- `POST /payments/order-charge/{id}/expire/` — cancel pending QR
- `GET /payments/docs/` — Redoc API docs (staff only)

**Cart & Order:**
- `POST/PATCH/DELETE /api/carts/{id}/cartitems/`
- `POST /api/orders/`

**Admin:**
- `POST/PATCH/DELETE /admin-dashboard-operators/contract-details/{slug}/`
- `POST /admin-dashboard-charge/manual-adjustment/`

Language via `Accept-Language` header. 12 supported languages.

## Payment System
Deep docs at [[payment-system]]. Key points:
- `finalize_payment(order)` is SSOT — every paid-order path funnels here
- `locked_amount` freezes charge amount after first QR; reset on expire
- `ExpirePendingChargeView` handles 6 Omise status cases for QR cancellation
- IdempotencyKey + SHA-256 prevents duplicate charges
- WebhookEvent audit saved outside `transaction.atomic()` to survive rollback
- Polling fallback covers 3DS webhook misses
- JPY handled as zero-decimal (`_to_minor_units()`)

## Celery Tasks
Pattern: `bind=True, max_retries, default_retry_delay`. Exponential backoff: `countdown = min(60 * (2 ** retries), 3600)`.

**High-risk (duplicate side-effect on retry):**
- `send_booking_confirmation_email` — guarded by `UserJourneyEvent`
- `send_booking_data` — duplicate risk accepted (dispatch endpoint migrating)
- `send_html_email` — no task-level guard; call-site guards only

## Dev Commands
```bash
source activate.sh          # venv + PostgreSQL + Redis + Celery
source deactive.sh          # stop all
source funnel.sh on|off     # Tailscale Funnel for webhook testing
python manage.py test payments --keepdb
python manage.py test orders.tests bookings operators --keepdb
```

## Production
Docker memory budget: ~1088MB across 5 containers (web 512MB, celery-worker 384MB, celery-beat 64MB, redis 64MB, nginx 64MB).

```bash
docker-compose -f docker-compose-rds.yml build web
docker-compose -f docker-compose-rds.yml up --no-deps web -d
```

## Related
- [[architecture]] (frontend)
- [[payment-system]]
- [[payment-integration]]
- [[README]]
