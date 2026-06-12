# Payment Exception Catalog

## Summary
All custom payment exceptions, their HTTP codes, and which are re-raised vs. swallowed. `PaymentAmountMismatchError` has a critical "never re-raised" contract.

## Context
Payment views catch specific exceptions and map them to HTTP responses. Mishandling any of these causes incorrect charge states or UI failures. The exception hierarchy is flat (all inherit `Exception`, no base `PaymentException`).

## Exception Reference

| Exception | HTTP | Response body | Re-raised? |
|---|---|---|---|
| `PendingChargeError` | 409 | `{error: 'pending_charge_exists', charge: {...}}` | No |
| `AlreadyPaidError` | 409 | `{error: 'Order already paid', charge_id: id}` | No |
| `LockedAmountError` | 409 | `{error: 'amount_locked', locked_amount, attempted_amount}` | No |
| `PaymentAmountMismatchError` | — | **NOT re-raised** (logged as ERROR, charge stays PAID) | Never |
| `NotImplementedError` (from create_charge) | 400 | `{error: str(e)}` | No |
| `ValueError` (idempotency mismatch) | 409 | `{error: 'reused with different parameters'}` | No |
| `ValueError` (method validation) | 400 | `{error: str(e)}` | No |

### Frontend 409 Mapping
```js
// useOmisePayment.js:166-182
if (error.response?.data?.error === 'pending_charge_exists') → pendingCharge state
if (error.response?.data?.error === 'amount_locked') → amountLocked state
if (error.response?.data?.error === 'Order already paid') → alreadyPaid + clearPaymentProcessing()
```

## Critical: PaymentAmountMismatchError Contract (payments/services.py:283-315)
```python
# Only checked when triggered_by_gc is not None (webhook path)
# Reconcile path (gc=None) skips this check entirely
if triggered_by_gc.amount != order.locked_amount:
    raise PaymentAmountMismatchError(...)

# In webhook handler — caught, logged, but NOT re-raised
try:
    finalize_payment(order, triggered_by_gc=gc)
except PaymentAmountMismatchError:
    logger.error("finalize_payment_amount_mismatch ...")
    # charge stays PAID — do not reverse
```
**Why:** If Omise confirmed payment, money was collected. Amount mismatch is a data inconsistency to investigate, not a reason to mark the order failed. Customer would be stranded.

## Silent Declined Card (M13 — FE bug, not BE exception)
`create_charge` stores `GatewayCharge` with `status=map_omise_status('failed')=PaymentStatus.FAILED` for a declined card. View returns HTTP **201** with serialized charge including `status='failed'`. FE (`useOmisePayment.js`) never reads `data.status` — returns `{success:true}`. `PaymentComponent.js` `handleClick` sees success, sets no state → completely silent. User left on payment form with `payment_pending` order, no error message.
**Fix:** read `data.status` after destructure; if `'failed'`, return `{success:false, errorMessage: data.failure_message}`.

## ValueError Overloading
Same exception type used for two unrelated errors:
- **Idempotency:** `"reused idempotency key with different parameters"` → 409
- **Method validation:** method not implemented → 400

Frontend must check HTTP code + message to distinguish.

## Related
- [[payment-gateway-charge-architecture]] — charge lifecycle, finalize_payment
- [[payment-finalize-deep-dive]] — where these exceptions originate
- [[omise-webhook-security]] — webhook verification before exceptions fire
- [[payment-charge-service-layer]] — create_charge exception paths
