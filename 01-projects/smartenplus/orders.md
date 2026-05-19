# Orders — Order Management

## Summary
Orders app manages order lifecycle. Central model: `Order`. Payment model tracks payment records. `WebhookEvent` is audit trail (outside atomic). `ManualAdjustment` replaces legacy admin charge flow. `Coupon` for discounts.

---

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

`clean()` fires on admin saves only. Direct `.save()` bypasses all guards — runtime status changes go through service functions.

**Key fields:**
- `order_id` — auto-generated unique ID
- `cart` FK — unique constraint: one active `ordering` order per cart
- `user` FK — nullable for guest checkout
- `billing_profile` FK — links to billing
- `status` — current order status
- `payment_finalized_at` — idempotency guard for `finalize_payment()`. If set, subsequent calls skip.
- `locked_amount` — freezes charge amount after first QR generated. Enforced at charge creation (Fix 3): if set and ≠ new amount → 409 `amount_locked`.
- `payment_notification_sent_at` — dedup sentinel for notifications. Atomic `UPDATE WHERE NULL`.
- `total_decimal` — order total
- `discount_decimal` — discount amount
- `coupon` FK — nullable. `times_used` incremented via `F()+1` in `finalize_payment()`.
- `retry_count` — payment retry counter

**Unique constraints:**
- `unique_active_ordering_order_per_cart` — one active `ordering` order per cart
- `order_locked_amount_set_when_payment_pending` — `locked_amount` must be set when status is `payment_pending`

---

### Payment
Payment record linked to Order. Legacy model (pre-GatewayCharge).

**Status values:** `created`, `pending`, `authorized`, `captured`, `voided`, `refunded`, `failed`.

**VALID_PAYMENT_TRANSITIONS** (in `clean()`):
- `created → {pending, failed}`
- `pending → {authorized, failed, voided}`
- `authorized → {captured, voided}`
- `captured → {refunded}`
- `voided/refunded` — terminal
- `failed → {pending, voided}`

**Fields:**
- `payment_id` — auto-generated via `pre_save_payment_field`
- `payment_method` — e.g., `CC`, `PP`, `MB_SCB`
- `amount_decimal` — precise decimal amount (preferred)
- `amount_paid` — legacy string field
- `currency` (default THB), `currency_rate`
- `status`

`amount` property: returns `amount_decimal` if set, else converts `amount_paid` string. `set_amount()` sets both fields atomically.

---

### Coupon
Discount coupons. Full doc at [[coupons]].

Key: `times_used` incremented via `F('times_used') + 1` in `finalize_payment()` — atomic, no race condition.

---

### PassengerDetail
Per-order passenger info. Fields: `first_name`, `last_name`, `email`, `phone`, `nationality`, `age_category`.

---

### WebhookEvent
Audit trail for external events (Omise webhooks). Saved **outside `transaction.atomic()`** — survives rollback even if business logic fails.

Fields: `source`, `event_type`, `event_id`, `payload` (JSON). Indexes on `event_id` + `created`.

---

### ManualAdjustment
Admin-recorded manual charges. Replaces `ExtraItemAction`. Payload: `{ order_id_str, amount, reason, note, extra_item_slug }`. Permission: `IsAdminOrIsStaff`.

---

## Lock Order Canonical

**Coupon → Order → BookingItem → TimeSlot**

Write-order guarantee: TimeSlot capacity cannot be oversold because Order must obtain lock before BookingItem confirms.

---

## Order Lifecycle

1. `Order` created with `status=ordering` (via `OrderManager.get_or_new()`)
2. `POST /payments/order-charge/` — `initiate_order_charge()` creates `GatewayCharge`
3. Payment pending → `status=payment_pending`, `locked_amount` set
4. Payment confirmed → `finalize_payment(order)` → `order.status='paid'`
5. Payment failed → `finalize_payment_failed()` → `status=payment_failed` (retryable)
6. Cancellation → `status=canceled` → can retry (canceled → ordering)

---

## Related
- [[payment-system]] (finalize_payment, locked_amount, payment_notification_sent_at)
- [[bookings]] (Order → BookingItem conversion)
- [[cart]] (Cart → Order conversion)
- [[coupons]] (Coupon model)
- [[backend-architecture]]