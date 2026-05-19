# SmartEnPlus — Payment System

## Summary
Omise-based payment system with `payments` app (2026-05-13). Supports Thai payment methods: credit card, debit card, PromptPay QR, mobile banking, e-wallet. GatewayCharge model is canonical charge source.

## Architecture

### Two Charge Models
1. **`payments.GatewayCharge`** — new canonical model (2026-05-13). Domain statuses: `pending/processing/paid/failed/expired/refunded/partial_refunded`
2. **`cards.Charge`** — legacy Omise model. Statuses: `successful/pending/failed`

`getPrimaryCharge()` in `helpers/paymentMethods.js` handles both — successful > pending > latest.

### Canonical Charge Rule (2026-05-14)
Always use LATEST `GatewayCharge` per order (`order_by('-created').first()`). Historical charges must NOT trigger finalization or display. Never query "any paid charge exists" — query latest, check its status.

### Checkout Payment Flow
1. `POST /payments/order-charge/` — creates `GatewayCharge` + links to Order
2. Webhook: `/admin-dashboard-orders/payments/webhook/` → `OmiseWebhookView`
3. Old `cards/` endpoints untouched (admin still uses them)

### Payment Routing (PaymentComponent.js)
- CC/DEBIT_CARD → `triggerCardPayment()`
- PP → `triggerOmiseSourcePayment('promptpay', false)`
- Others → `triggerOmiseSourcePayment(OMISE_SOURCE_TYPES[type], true)`

### QR Polling (PromptPay)
- `useQRPolling` + `useQRTimer` in `QRPaymentForm`
- Polling starts when `orderDetails.expires_at` present
- GatewayCharge status: check BOTH `status === 'successful' || status === 'paid'`
- After success: redirect to `/orders/{id}` (auth) or `/guest-order/{id}?email=...` (guest)
- Never redirect to `authorizeUri` for PromptPay (empty)

### PendingChargeNotice
`components/payment/PendingChargeNotice.js` — shown when `current_charge_status='pending'` for redirect methods. CC/debit: no "Continue" button. Others: "Continue to Payment" only if `expiresAt > 60s` and `authorizeUri` present.

## Key Decisions

### payment_failed Is Recoverable (2026-05-14)
`ordering → payment_failed → paid` valid lifecycle. User may retry with different method. `finalize_payment_failed()` does NOT set `payment_finalized_at`. Admin/analytics: don't count as lost revenue until cancelled.

### Cart Reset Location (2026-05-13)
`cartActions.resetCart()` on order confirmation pages only (`/orders/[orderid].js`, `/guest-order/[orderId].js` when `status === 'paid'`). NOT in `useOmisePayment.js`.

### Double-Click Protection (2026-05-13)
`isSubmitting` state in `FormCard.js`. Pay Now disabled + "Processing..." for 10s. Uses `setPaymentTriggerEffect(true)`.

### Stripe Removed (2026-05-12)
Never re-add Stripe code.

## Backend Payment Options
`/gateway-fee/` API is single source of truth. Sends `payment_type`, `category`, `actived`, `fee_calculated`. Frontend stores raw `payment_type` — no normalization.

`OMISE_SOURCE_TYPES` in `helpers/paymentMethods.js` maps to Omise source types. `getBackendPaymentType()` in `useOmisePayment.js` converts for charge API.

## Backend Internals

### `finalize_payment(order)` — Single Source of Truth
`payments/services.py`. Called from webhook handler, polling fallback, and reconcile path. Every paid-order path funnels through this one function.

- `select_for_update()` + `payment_finalized_at` guard → idempotent. If field already set, returns immediately.
- Inside atomic: CartItem.delete → coupon `times_used` F()+1 → `confirm_booking_items_for_order()` → Order status to `paid` → `on_commit` notifications.
- **Rule:** if you need behavior on payment success, add it here — not in the caller.

### `locked_amount` — Charge Amount Freezing
Set when first PromptPay QR generated. Prevents double-charge on retry with different amount. Reset to NULL on expire (`ExpirePendingChargeView`) and method switch (C3b step).

Enforced at charge creation (Fix 3): if `locked_amount` set and ≠ new amount → 409 `amount_locked`. Migration 0038. Tech debt: missing `CheckConstraint` + index.

### `ExpirePendingChargeView` — QR Cancellation
`POST /payments/order-charge/{id}/expire/`. Six-case behavior:

| Omise status at retrieve | `.expire()` result | Local action | HTTP |
|---|---|---|---|
| `successful` | not called | gc→PAID, `finalize_payment()` | 409 |
| `expired` / `failed` | not called | gc→EXPIRED | 200 |
| `pending` / `unknown` | succeeds | gc→EXPIRED | 200 |
| `pending` / `unknown` | throws | gc→EXPIRED (trust exception) | 200 |
| other | not called | — | 409 |
| retrieve throws | — | — | 503 |

On 200 success: resets `Order.locked_amount = NULL`. Sends `_send_payment_failed_notifications(order, reason='expired')` before order reset (2026-05-18 fix).

### IdempotencyKey — Duplicate Charge Prevention
SHA-256 hash of (method, amount, currency). On new charge: matching key + pending → reuse. Hash mismatch → expire old charge, create fresh. Already paid → 409.

### WebhookEvent Audit Trail
`WebhookEvent.get_or_create()` saved OUTSIDE `transaction.atomic()`. Survives rollback — audit record available for debugging even if business logic fails.

### JPY Zero-Decimal Handling
`_to_minor_units(amount, currency)` in `payments/services.py`. THB/EUR/USD ×100, JPY ×1. `ZERO_DECIMAL_CURRENCIES = {'JPY'}`. Bug fixed 2026-05-13: previous `_to_satang()` multiplied JPY by 100.

### Polling Fallback for 3DS
`orders/views.py` orderdetails endpoint. When frontend polls:
- GatewayCharge PAID → `finalize_payment()` (covers 3DS webhook miss)
- GatewayCharge PENDING → `reconcile_gateway_charge()` → Omise live query → `_sync_order_status()`

### Notification Deduplication
`payment_notification_sent_at` on Order. Set via atomic `UPDATE WHERE NULL` in `finalize_payment()`. Max 2 notifications per order: one pending (charge creation), one paid (finalization).

### Status Machines
**Order:** `ordering → {paid, canceled, processing}` | `payment_pending → {ordering, paid, canceled, payment_failed}` | `payment_failed → {ordering, canceled}` | `paid → {refunded, partial_refunded, canceled}`. Enforced in `clean()` only — admin saves. Direct `.save()` bypasses guards.

**BookingItem:** `Pending → {Confirmed, Canceled}` | `Confirmed → {No Show, Partially Refund, Fully Refund, Canceled}`. Terminal states locked.

### Charge Creation Order (`initiate_order_charge`)
1. **C3b** — expire stale PromptPay if switching method. Reset `locked_amount`. Must run before C3.
2. **C3** — block if another PENDING redirect charge exists → 409 `pending_charge_exists`.
3. **Fix 3** — enforce `locked_amount`: if set and ≠ new amount → 409 `amount_locked`.
4. Idempotency check → `create_charge()` → Payment/Order update in `transaction.atomic()`.

### ManualAdjustment
Replaces `ExtraItemAction`. `POST /admin-dashboard-charge/manual-adjustment/`. Payload: `{ order_id_str, amount, reason, note, extra_item_slug }`. Permission: `IsAdminOrStaff`. Legacy `cards.Charge` + `cards.Refund` now read-only.

## Phase 2 Changes (2026-05-16)

### Idempotency Key on Order Creation
`Order.idempotency_key` field + `X-Idempotency-Key` HTTP header support in `OrderAndBillingProfileViewSet`. Same key + valid order → returns existing order (200). Prevents duplicate orders on double-click/retry. Key stored on create, reused on subsequent attempts.

Frontend: `getOrderAndBilling()` passes `X-Idempotency-Key` scoped to cart snapshot (`cartId:total`). Key regenerates if cart changes.

### Reconciliation Endpoint
`POST /order-detail/<order_id>/reconcile/?email=...` — forces Omise status sync for stuck `payment_pending` orders. Guest: `?email=...` param required. Auth: matches by `user_id`. Returns `{status, charge_status, is_final}`.

Frontend: `getReconcileOrder()` helper in `helpers/getBillingAndOrder.js`.

### CheckoutSnapshot Model
`orders/models.py` — `CheckoutSnapshot` model created in `initiate_order_charge()` after `create_charge()`. Immutable record of cart state at payment initiation: `cart_id`, `total_thb`, `item_count`, `items_hash`.

Uses `update_or_create` for idempotency — safe on retry. Future: validate cart unchanged before new charge attempt.

### Expire Endpoint Protection
`POST /payments/order-charge/<id>/expire/` now reconciles instead of erroring when charge is already paid/expired at Omise. Catches "already paid" / "cannot be expired" → calls `reconcile_gateway_charge()` → returns 409 with actual Omise status.

### Frontend 409 Error Handling
`helpers/getBillingAndOrder.js` maps backend 409 errors:
- `payment_pending` → `PAYMENT_PENDING`
- `amount_locked` → `AMOUNT_LOCKED`
- `Order already paid` → `ORDER_ALREADY_PAID`

`usePaymentInitialization.js` handles each distinctly. `PaymentComponent.js` renders per type: amber for retry-able, red for fatal, green for success.

### Cross-Tab Cart Sync
`cart_version` storage key — bumped on cart mutation in `cart-slice.js`, storage event listener in `store/index.js` invalidates RTK Query cart cache in other tabs.

### formData SessionStorage
`pages/checkout/index.js` persists `formData` to sessionStorage. Structure: `{cartId, updatedAt, formData}`. Validates: freshness (30min max), cartId match. Cleared on payment success via `paymentSuccess` event.

## Repay Failure Root Causes (2026-05-16)

Seven bugs causing "can't retry payment after refresh or cart update". All fixed on branch `260513-refactor/payment`.

| # | Root Cause | File | Fix |
|---|-----------|------|-----|
| 1 | `cartId` not cleared on reset | `store/cart-slice.js` | Uncomment `state.cartId = null` |
| 2 | 409 `payment_pending`/`amount_locked` handlers missing | `helpers/getBillingAndOrder.js` | Map 409 → error types |
| 3 | Error branches missing in hook | `hooks/usePaymentInitialization.js` | Add `PAYMENT_PENDING`, `AMOUNT_LOCKED`, `ORDER_ALREADY_PAID` |
| 4 | Alert not per error type | `pages/checkout/PaymentComponent.js` | Conditional alerts per error type |
| 5 | No cross-tab cart sync | `store/index.js` + `cart-slice.js` | `cart_version` storage key + listener |
| 6 | `PendingChargeNotice` null guard missing | `components/payment/PendingChargeNotice.js` | Add `onCheckStatus &&` before callback |
| 7 | `formData` lost on refresh | `pages/checkout/index.js` | sessionStorage with 30min + cartId validation |

### Test Scenarios
- Refresh at payment step → formData restores from sessionStorage
- Two tabs, Tab 2 tries pay → amber alert + Cancel button (409 PAYMENT_PENDING)
- Cart changed, retry → AMOUNT_LOCKED alert
- Payment success + new checkout → cartId cleared, no stale key
- Double-click Pay Now → idempotency key prevents duplicate order
- Cancel pending payment → charge expired, order resets to editable

## Related
- [[README]]
- [[checkout-flow]]
- [[payment-integration]]
- [[backend-architecture]]
