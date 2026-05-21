# Refund Flow

## Summary
Two refund models: `payments.Refund` (canonical) and `cards.Refund` (legacy, read-only). `RefundViewSet` in `cards` deprecated — pending Step 7 deletion after zero `DEPRECATED_ENDPOINT_USED` in prod logs.

## Models

### payments.Refund
`RefundCreateView` creates. Fields: `gateway_refund_id`, `gateway_charge` FK, `amount`, `currency`, `status`. Omise refund object stored.

### cards.Refund
Legacy. Linked to `cards.Charge`. No new refunds here.

## Flow

1. Admin initiates via `POST /payments/refund/` or admin dashboard
2. `RefundCreateView` calls Omise: `client.Refund.create(charge=charge_id)`
3. `Refund` record created with `gateway_refund_id`
4. Order status: `paid → refunded` or `paid → partial_refunded`

## Legacy Deprecation
- `cards/views.RefundViewSet` — logs `DEPRECATED_ENDPOINT_USED` on every request
- Step 7: delete after confirming zero prod usage

## Related
- [[payment-system]]
- [[backend-architecture]]
