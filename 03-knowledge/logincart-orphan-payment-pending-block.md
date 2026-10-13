# Login Cart Merge Blocked By Orphan payment_pending Order

## Summary
`PUT /logincart/<cartId>/` returns 409 `payment_pending` while any active `payment_pending` order belongs to the guest cart or the user. An ORPHAN order (latest charge already `expired`/`failed` locally, order never reset) blocks the merge forever, so a guest trip is dropped after email login. Google login looked fine because its merge path differs.

## Why It Matters
Sweepers write the charge status and the order status in separate transactions with swallowed exceptions, and `expire_stale_payments` is not in celery beat. One failed write leaves the order stuck. Cart edits are blocked too ("Cancel payment to edit cart").

## Detail
- Heal `carts/orphan_payment_heal.py::heal_orphan_payment_orders` runs BEFORE `payment_guard.has_payment_pending_order`. It asks Omise about the LATEST charge: `successful` -> charge PAID + `finalize_payment`; `failed`/`expired`/`reversed` -> `finalize_payment_failed` (order `payment_failed`, `locked_amount` cleared); anything else or Omise error/timeout -> skipped, guard still 409 (fail closed).
- Never heal a latest charge that is `pending`/`processing`, or an order with no charge. 6 s total budget, max 3 orders, Omise lookup on a daemon thread (client has no timeout).
- Lock order GatewayCharge then Order (same as webhook). Recheck under lock: order still `payment_pending`, charge still terminal, still the newest charge.
- Amount mismatch on a paid heal: charge stays PAID (money confirmed), order stays `payment_pending`, merge stays 409.
- User escape: `/orders/[orderid]` cancel button -> `POST /payments/order-charge/<id>/expire/` -> order `ordering`, `locked_amount` None. Unblocks cart edits and checkout; does NOT merge the guest trip (merge runs only at login).
- Measure: one `logincart_blocked_payment_pending cart_id= user_id=` warning per 409, logged only in the `/logincart` handler (not in the shared `payment_pending_response`).
- Test trap: PromptPay cancel calls Omise `.expire()`, a fake charge id gives 503. Seed a mobile-banking charge instead (local abandon).

## Related
BE `docs/technical/PAYMENT_SYSTEM.md` (heal section), [[payment-backend-charge-flow]], [[cart-reprovision-after-reset]]
