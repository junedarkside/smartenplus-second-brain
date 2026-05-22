# SmartEnPlus — Payment System

## Summary
Omise-based payments via `payments` app (2026-05-13). Thai methods: CC, debit, PromptPay QR, mobile banking, e-wallet. `GatewayCharge` = canonical charge source.

## Architecture

### Two Charge Models
1. **`payments.GatewayCharge`** — canonical. Domain statuses: `pending/processing/paid/failed/expired/refunded/partial_refunded`
2. **`cards.Charge`** — legacy Omise. Statuses: `successful/pending/failed`

`getPrimaryCharge()` in `helpers/paymentMethods.js` — successful > pending > latest.

### Canonical Charge Rule (2026-05-14)
LATEST `GatewayCharge` per order (`order_by('-created').first()`). Historical charges must NOT trigger finalization/display.

### Payment Flow
1. `POST /payments/order-charge/` → creates GatewayCharge + links to Order
2. Webhook: `/admin-dashboard-orders/payments/webhook/` → `OmiseWebhookView`

### Payment Routing (PaymentComponent.js)
- CC/DEBIT_CARD → `triggerCardPayment()`
- PP → `triggerOmiseSourcePayment('promptpay', false)`
- Others → `triggerOmiseSourcePayment(OMISE_SOURCE_TYPES[type], true)`

### QR Polling (PromptPay)
`useQRPolling` + `useQRTimer` in `QRPaymentForm`. Poll when `orderDetails.expires_at` present. Check BOTH `status === 'successful' || status === 'paid'`. After success: redirect to order page (auth) or guest order page (guest). Never redirect to `authorizeUri` for PP.

### PendingChargeNotice
Shown when `current_charge_status='pending'` for redirect methods. CC/debit: no "Continue" button. Others: only if `expiresAt > 60s` && `authorizeUri`.

## Key Decisions

### payment_failed Is Recoverable
`ordering → payment_failed → paid` valid lifecycle. `finalize_payment_failed()` does NOT set `payment_finalized_at`.

### Cart Reset Location
`cartActions.resetCart()` on order confirmation pages only (`/orders/[orderid].js`, `/guest-order/[orderId].js` when `status === 'paid'`). NOT in `useOmisePayment.js`.

### Double-Click Protection
`isSubmitting` in `FormCard.js`. Pay Now disabled + "Processing..." for 10s.

### Stripe Removed (2026-05-12)
Never re-add.

## Backend Payment Options
`/gateway-fee/` API = SSOT. Sends `payment_type`, `category`, `actived`, `fee_calculated`. Frontend stores raw `payment_type`.

## Backend Internals

### `finalize_payment(order)` — SSOT
`payments/services.py`. Every paid-order path funnels here.
- `select_for_update()` + `payment_finalized_at` guard → idempotent
- Inside atomic: CartItem.delete → coupon `times_used` F()+1 → `confirm_booking_items_for_order()` → Order → `paid` → `on_commit` notifications
- **Rule:** add payment success behavior here, not in callers

### `locked_amount` — Charge Amount Freezing
Set on first QR generation. Prevents double-charge on retry. Reset on expire + method switch (C3b). Enforced at charge creation: `locked_amount` set && ≠ new amount → 409 `amount_locked`.

### `ExpirePendingChargeView` — QR Cancellation
`POST /payments/order-charge/{id}/expire/`. Six-case behavior:

| Omise status at retrieve | `.expire()` result | Local action | HTTP |
|---|---|---|---|
| `successful` | not called | gc→PAID, `finalize_payment()` | 409 |
| `expired` / `failed` | not called | gc→EXPIRED | 200 |
| `pending` / `unknown` | succeeds | gc→EXPIRED | 200 |
| `pending` / `unknown` | throws | gc→EXPIRED | 200 |
| other | not called | — | 409 |
| retrieve throws | — | — | 503 |

On 200: resets `locked_amount = NULL`. Sends `_send_payment_failed_notifications` before order reset.

### IdempotencyKey
SHA-256(method, amount, currency). Pending + same key → reuse. Hash mismatch → expire old, create fresh. Already paid → 409.

### WebhookEvent Audit
Saved OUTSIDE `transaction.atomic()`. Survives rollback.

### JPY Zero-Decimal
`_to_minor_units(amount, currency)`. THB/EUR/USD ×100, JPY ×1.

### Polling Fallback
Orderdetails endpoint: GatewayCharge PAID → `finalize_payment()`. PENDING → `reconcile_gateway_charge()` → Omise live query.

### Notification Dedup
`payment_notification_sent_at` on Order. Atomic `UPDATE WHERE NULL`. Max 2 notifications per order.

### Status Machines
**Order:** `ordering → {paid, canceled, processing}` | `payment_pending → {ordering, paid, canceled, payment_failed}` | `payment_failed → {ordering, canceled}` | `paid → {refunded, partial_refunded, canceled}`. Enforced in `clean()` only.

**BookingItem:** `Pending → {Confirmed, Canceled}` | `Confirmed → {No Show, Partially Refund, Fully Refund, Canceled}`.

### Charge Creation Order (`initiate_order_charge`)
1. **C3b** — expire stale PP if switching method
2. **C3** — block if another PENDING redirect charge → 409
3. **Fix 3** — enforce `locked_amount`
4. Idempotency check → `create_charge()` → atomic update

## Phase 2 Changes (2026-05-16)

### Idempotency Key on Order Creation
`Order.idempotency_key` + `X-Idempotency-Key` header. Same key + valid order → returns existing (200). Frontend: `getOrderAndBilling()` passes key scoped to `cartId:total`.

### Reconciliation Endpoint
`POST /order-detail/<order_id>/reconcile/?email=...` — forces Omise sync for stuck orders.

### CheckoutSnapshot
`orders/models.py` — immutable cart state at payment initiation. `update_or_create` for idempotency.

### Expire Endpoint Protection
Now reconciles instead of erroring when charge already paid/expired at Omise.

### Frontend 409 Error Handling
`getBillingAndOrder.js`: `payment_pending` → `PAYMENT_PENDING`, `amount_locked` → `AMOUNT_LOCKED`, `Order already paid` → `ORDER_ALREADY_PAID`.

### Cross-Tab Cart Sync
`cart_version` storage key + listener in `store/index.js`.

### formData SessionStorage
Structure: `{cartId, updatedAt, formData}`. Freshness (30min) + cartId match. Cleared on payment success.

## Repay Failure Root Causes (2026-05-16)

| # | Root Cause | File | Fix |
|---|-----------|------|-----|
| 1 | `cartId` not cleared on reset | `store/cart-slice.js` | Uncomment `state.cartId = null` |
| 2 | 409 handlers missing | `helpers/getBillingAndOrder.js` | Map 409 → error types |
| 3 | Error branches missing in hook | `hooks/usePaymentInitialization.js` | Add all 3 error types |
| 4 | Alert not per error type | `PaymentComponent.js` | Conditional alerts |
| 5 | No cross-tab sync | `store/index.js` + `cart-slice.js` | `cart_version` key |
| 6 | `PendingChargeNotice` null guard | `PendingChargeNotice.js` | Add `onCheckStatus &&` |
| 7 | `formData` lost on refresh | `checkout/index.js` | sessionStorage with validation |

## Related
- [[README]]
- [[checkout-flow]]
- [[payment-integration]]
- [[backend-architecture]]
