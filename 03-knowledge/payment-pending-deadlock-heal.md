---
name: payment-pending-deadlock-heal
description: Paid-but-unfinalized order deadlock — order in `payment_pending` despite charge PAID, because ExpirePendingChargeView returns 400 for non-pending charges and reconcile skips non-pending. Two backend fixes: expire endpoint recovery for paid/failed, reconcile retry for paid+unfinalized.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: payment-pending-deadlock
---

# Payment Pending Deadlock — Heal Procedure

## Summary
Order stuck `payment_pending` despite charge PAID at Omise. `ExpirePendingChargeView` rejects non-pending (400), `reconcile_gateway_charge` skips non-pending. No retry for `finalize_payment`.

## Why It Matters
Customer paid but order invisible — can't access booking, can't refund. Deadlock requires manual DB fix.

## Detail
**Reproduction:** Order `PLB0229785`. Charge PAID → order remains `payment_pending`. Status stuck.

**Root cause chain:**
1. `ExpirePendingChargeView` (DELETE `/payments/expire/{pending_charge_id}/`) returns 400 for `paid`/`failed` charges — only allows `pending`.
2. `reconcile_gateway_charge` (Celery webhook handler) skips non-pending charges → never calls `finalize_payment`.
3. `finalize_payment` has no retry on `PaymentAmountMismatchError` → single-shot failure = permanent stuck.

**Two backend fixes:**

**Fix 1 — Expire endpoint recovery for paid/failed:**
```python
# payments/views.py ExpirePendingChargeView
# Allow paid/failed charges to attempt finalize (one-shot recovery)
if charge.status in ('paid', 'failed'):
    finalize_payment(order)  # idempotent, safe to call
```

**Fix 2 — Reconcile retry for paid+unfinalized:**
```python
# payments/tasks.py reconcile_gateway_charge
if order.payment_finalized_at is None and charge.status == 'paid':
    try:
        finalize_payment(order)
    except PaymentAmountMismatchError as e:
        # Retry once for paid orders (permanent fix for deadlock)
        raise self.retry(exc=e, countdown=60)
```

**Manual heal (runbook):**
```python
from orders.models import Order
from payments.views import finalize_payment
o = Order.objects.get(order_id='PLB0229785')
Order.objects.filter(id=o.id).update(payment_finalized_at=None)
finalize_payment(o)
```

## Constraints / Gotchas
`finalize_payment` is idempotent — safe to call multiple times. Fix 1 is one-shot recovery endpoint. Fix 2 prevents future deadlocks.

## Related
- [[payment-pending-deadlock]] — parent bug report
- [[payment-deep-review]] — H5 finding (paid-but-unfinalized invisible orders)
