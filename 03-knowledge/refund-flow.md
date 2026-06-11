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
2. `RefundCreateView` calls Omise: `client.Refund.create(charge=charge_id, amount=amount_satang)`
3. `Refund` record created with `gateway_refund_id`, `amount`, `currency`, `status`
4. Order status updated: `paid → refunded` (full) or `paid → partial_refunded` (partial)

### Full vs Partial
- Full: `amount == gateway_charge.amount` → Order.status = `refunded`
- Partial: `amount < gateway_charge.amount` → Order.status = `partial_refunded`
- Multiple partials possible until sum reaches full charge amount
- GatewayCharge.status mirrors: `refunded` or `partial_refunded`

### Omise API Call
```python
client = get_omise_client()
omise_refund = client.Charge.retrieve(gc.gateway_charge_id).refunds.create(
    amount=amount_in_satang,  # minor units — must convert before sending
)
```
`booking_slug` field on `Refund` model: links refund to specific booking within multi-booking order. Allows refunding individual passenger/trip within same order without full order refund.

## Legacy Deprecation
- `cards/views.RefundViewSet` — logs `DEPRECATED_ENDPOINT_USED` on every request
- `cards.Refund` model: read-only, linked to deprecated `cards.Charge`
- No new `cards.Refund` records created since migration
- Step 7: delete `cards/views.RefundViewSet` after confirming zero prod `DEPRECATED_ENDPOINT_USED` logs

## Related
- [[payment-gateway-charge-architecture]] — GatewayCharge statuses: `refunded` / `partial_refunded`
- [[manual-adjustment-model]] — admin manual charges (additive, not refunds)
- [[payment-status-enums]] — Order.status transitions for refund
- [[omise-client-integration]] — `get_omise_client()` pattern used in refund creation
