# Orders — Order Management

## Summary
Orders app. Central model: `Order`. `Payment` tracks records. `WebhookEvent` audit trail (outside atomic). `ManualAdjustment` replaces legacy admin charge. `Coupon` for discounts.

## Models

### Order
Central order entity. Auto-generates `order_id` via `pre_save_order_field`.

**Status values:** `ordering`, `payment_pending`, `paid`, `processing`, `refunded`, `partial_refunded`, `canceled`, `payment_failed`.

**VALID_ORDER_TRANSITIONS** (in `clean()` — admin only):
- `ordering → {paid, canceled, processing}`
- `payment_pending → {ordering, paid, canceled, payment_failed}`
- `processing → {paid, canceled}`
- `paid → {refunded, partial_refunded, canceled}`
- `payment_failed → {ordering, canceled}`
- `canceled → {ordering}` (allows retry)

`clean()` fires on admin saves only. Direct `.save()` bypasses guards — runtime changes via service functions.

**Key fields:**
- `order_id` — auto-generated unique ID
- `cart` FK — unique constraint: one active `ordering` order per cart
- `user` FK — nullable for guest
- `billing_profile` FK — links to billing
- `payment_finalized_at` — idempotency guard for `finalize_payment()`. If set → skip.
- `locked_amount` — freezes charge after first QR. Set && ≠ new amount → 409 `amount_locked`.
- `payment_notification_sent_at` — dedup sentinel. Atomic `UPDATE WHERE NULL`.
- `total_decimal`, `discount_decimal`, `coupon` FK (nullable, `times_used` via `F()+1`)
- `retry_count`

**Constraints:** `unique_active_ordering_order_per_cart`, `order_locked_amount_set_when_payment_pending`

### Payment
Legacy payment record linked to Order.

**Status:** `created → pending → authorized → captured → refunded`. `voided/refunded` = terminal. `failed → {pending, voided}`.

`amount` property: `amount_decimal` if set, else converts `amount_paid` string. `set_amount()` sets both atomically.

### Coupon
`times_used` incremented via `F('times_used') + 1` in `finalize_payment()` — atomic, no race. Full doc at [[coupons]].

### PassengerDetail
Per-order passenger info. `first_name`, `last_name`, `email`, `phone`, `nationality`, `age_category`.

### WebhookEvent
Audit trail for Omise webhooks. Saved OUTSIDE `transaction.atomic()` — survives rollback. Fields: `source`, `event_type`, `event_id`, `payload` (JSON).

### ManualAdjustment
Admin manual charges. Replaces `ExtraItemAction`. Payload: `{ order_id_str, amount, reason, note, extra_item_slug }`. `IsAdminOrIsStaff`.

## Lock Order Canonical

**Coupon → Order → BookingItem → TimeSlot**

Write-order guarantee: Order must obtain lock before BookingItem confirms → TimeSlot can't oversell.

## Order Lifecycle

1. `Order` created `status=ordering` (via `OrderManager.get_or_new()`)
2. `POST /payments/order-charge/` → `initiate_order_charge()` creates GatewayCharge
3. Pending → `status=payment_pending`, `locked_amount` set
4. Confirmed → `finalize_payment(order)` → `status='paid'`
5. Failed → `finalize_payment_failed()` → `status=payment_failed` (retryable)
6. Cancel → `status=canceled` → can retry (`canceled → ordering`)

## Related
- [[payment-system]]
- [[bookings]]
- [[cart]]
- [[coupons]]
- [[backend-architecture]]
