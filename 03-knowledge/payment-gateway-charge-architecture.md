# Payment Gateway Charge Architecture

## Summary
Two-charge model (GatewayCharge + legacy cards.Charge). Canonical = latest GatewayCharge. Webhook sole finalization source.

## Context
Omise integration for Thai payment methods. Needs clear charge selection rule to prevent double-finalization.

## Problem
Two charge models coexisted. Without selection rule, wrong charge triggers finalization → paid order marked failed, or vice versa.

## Details

### Two Charge Models
1. **`payments.GatewayCharge`** — canonical. Statuses: `pending/processing/paid/failed/expired/refunded/partial_refunded`
2. **`cards.Charge`** — legacy Omise. Statuses: `successful/pending/failed`

`getPrimaryCharge()` — successful > pending > latest.

### Canonical Charge Rule
LATEST `GatewayCharge` per order (`order_by('-created').first()`). Historical charges must NOT trigger finalization/display.

### Payment Flow
1. `POST /payments/order-charge/` → creates GatewayCharge + links to Order
2. Webhook → `OmiseWebhookView` → sole payment finalization source

### `finalize_payment(order)` — Idempotent SSOT
`select_for_update()` + `payment_finalized_at` guard. Inside atomic: CartItem.delete → coupon `times_used` F()+1 → `confirm_booking_items_for_order()` → Order → `paid` → `on_commit` notifications.
**Rule:** add payment success behavior here, not callers.

### `locked_amount` — Charge Amount Freezing
Set on first QR gen. Prevents double-charge on retry. Reset on expire + method switch. Enforced at charge creation: `locked_amount` set && ≠ new amount → 409 `amount_locked`.

### `ExpirePendingChargeView`
`POST /payments/order-charge/{id}/expire/`.

| Omise status at retrieve | `.expire()` result | Local action | HTTP |
|---|---|---|---|
| `successful` | not called | gc→PAID, `finalize_payment()` | 409 |
| `expired` / `failed` | not called | gc→EXPIRED | 200 |
| `pending` / `unknown` | succeeds | gc→EXPIRED | 200 |
| pending / unknown | throws | gc→EXPIRED | 200 |
| other | not called | — | 409 |
| retrieve throws | — | — | 503 |

On 200: resets `locked_amount = NULL`. Sends `_send_payment_failed_notifications` before order reset.

### WebhookEvent Audit
Saved OUTSIDE `transaction.atomic()`. Survives rollback.

### Status Machines
**Order:** `ordering → {paid, canceled, processing}` | `payment_pending → {ordering, paid, canceled, payment_failed}` | `payment_failed → {ordering, canceled}` | `paid → {refunded, partial_refunded, canceled}`. Enforced in `clean()` only.

**BookingItem:** `Pending → {Confirmed, Canceled}` | `Confirmed → {No Show, Partially Refund, Fully Refund, Canceled}`.

## Decision
Webhook = sole payment finalization source. `finalize_payment()` idempotent via `select_for_update()` + `payment_finalized_at` guard.

## Tradeoffs
- Two-charge model: legacy debt. GatewayCharge is canonical; cards.Charge ignored in practice.
- `locked_amount` serialization: small perf hit on charge init. Rare path, worth it.

## Consequences
- Double-charge prevented at DB level
- Payment success behavior centralized in `finalize_payment()`
- Webhook rollback safety via out-of-transaction webhook event storage

## Related
- [[payment-charge-service-layer]]
- [[payment-status-enums]]
- [[payment-integration]]
- [[promptpay-no-webhook-on-expiry]]