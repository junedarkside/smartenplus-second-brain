# Refund Flow

## Summary
Two refund models: `payments.Refund` (canonical, active) and `cards.Refund` (legacy, read-only from `cards.Charge`). `RefundViewSet` in `cards` is deprecated pending Step 7 deletion after confirming zero `DEPRECATED_ENDPOINT_USED` in prod logs.

---

## Models

### payments.Refund
Created via `payments/views.py:RefundCreateView`. Fields: `gateway_refund_id`, `gateway_charge` (FK), `amount`, `currency`, `status`. Omise refund object stored.

### cards.Refund
Legacy. Linked to `cards.Charge`. No new refunds should be created here.

---

## Flow

1. Admin initiates refund via `POST /payments/refund/` or admin dashboard.
2. `RefundCreateView` calls Omise API: `client.Refund.create(charge=charge_id)`.
3. `Refund` record created with `gateway_refund_id`.
4. Order status updated: `paid → refunded` or `paid → partial_refunded`.

---

## Legacy Deprecation

- `cards/views.RefundViewSet` — logs `DEPRECATED_ENDPOINT_USED` warning on every request.
- Step 7: delete `RefundViewSet` after confirming zero prod usage.

---

## Related
- [[payment-system]]
- [[backend-architecture]]