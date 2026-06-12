# Payment Pending Deadlock — Paid Charge, Unfinalized Order

## Status: FIXED (Jun 13, 2026)

Three backend fixes deployed. 278 tests pass. Production recovery: `POST /payments/order-charge/chrg_test_67zrcauou19uk2t655l/expire/` with owner email.

## Summary
Order stuck in `payment_pending` despite charge PAID at Omise. Every recovery path dead-ended. Fixed via 3 backend changes — no frontend changes needed.

## Context
Live production bug on order `PLB0229785` (Jun 12, 2026). User cannot delete cart items or retry payment. All mutations blocked by `payment_pending` guard.

## Problem

### Symptoms
- `POST /order-billing/` → 409 `order_mutation_blocked_payment_pending`
- `POST /payments/order-charge/chrg_test_67zra0vnjch315955ai/expire/` → 400 `Charge is not pending`
- Frontend fully locked — no cart edits, no payment retry, no cancel

### Two charges on same order

| Charge ID | Status | Role |
|-----------|--------|------|
| `chrg_test_67zra0vnjch315955ai` | Non-pending (expired/failed) | First attempt — frontend tried to expire → 400 |
| `chrg_test_67zrcauou19uk2t655l` | **PAID** (1,012.71 THB, PromptPay, Jun 12 18:00:56) | Second attempt — Omise confirmed |

### Deadlock chain

**Route A — amount mismatch (hit PLB0229785)**

1. Charge A created → order = `payment_pending`, `locked_amount = X`
2. User tries to modify → 409 blocks. Charge A expires/fails at Omise.
3. Frontend tries expire on charge A → **400** (`views.py`: charge not pending)
4. User retries — amount recalculates (fee/FX refresh) → `locked_amount` updated to Y
5. Charge B created → charge B **PAYS** at Omise
6. Webhook fires → `_handle_order_paid` → `finalize_payment(order, triggered_by_gc=charge_B)`
7. `services.py:310-321` checks `charge_B.amount (X) != order.locked_amount (Y)` → **raises** `PaymentAmountMismatchError`
8. `views.py:289` catches + swallows ("manual ops review") → order stays `payment_pending`
9. Deadlock: charge B = PAID, order = `payment_pending`, no recovery

**Route B — lost webhook**

1. User pays → PAID at Omise → webhook never arrives
2. Celery self-expires PromptPay by TTL **without querying Omise** → charge locally mislabeled
3. Order stuck `payment_pending`, charge terminal → same dead end

### Why no automatic recovery (pre-fix)

| Code path | Why it failed |
|-----------|--------------|
| `ExpirePendingChargeView` (`views.py:385-389`) | Returned 400 for non-pending, non-expired charges. Never reached unlock logic at 482-485 |
| `reconcile_gateway_charge` (`services.py:240`) | Returned early if `gc.status != PENDING`. PAID charge never re-reconciled |
| `sync_pending_charges` celery task | Only queries `status=PENDING`. PAID charges ignored |
| `finalize_payment` | Never re-triggered — no code path retried after mismatch |
| Webhook | Already deduped (`last_webhook_event_id`). Won't re-fire |
| Retry payment `_handle_existing_charge` | Local-PAID → raised `AlreadyPaidError` without attempting finalize |

## How to Reproduce (staging)

```python
# Django shell — creates a stuck deadlock state
from payments.models import GatewayCharge
from orders.models import Order
from decimal import Decimal

order = Order.objects.get(order_id='YOUR_TEST_ORDER')
order.status = 'payment_pending'
order.locked_amount = Decimal('600.00')  # intentional drift from charge amount
order.save(update_fields=['status', 'locked_amount'])

gc = GatewayCharge.objects.create(
    gateway_charge_id='chrg_test_fake_paid',
    payment_method='promptpay',
    amount=Decimal('500.00'),   # mismatch: 500 != locked_amount 600
    status='paid',
    order=order,
)

# Now observe:
# - Any cart edit → 409 order_mutation_blocked_payment_pending
# - POST /payments/order-charge/chrg_test_fake_paid/expire/ + email → POST-FIX: 200 recovered
```

## Fix — 3 backend changes, no frontend changes

### Fix 1: `ExpirePendingChargeView` recovery (`views.py:385+`)

Terminal charge + stuck order → recover instead of 400:

- `paid` + `payment_pending` → verify at Omise → `successful` → `finalize_payment(order)` **without amount check** (Omise confirmed, mismatch is bookkeeping). If finalize fails → fallback unlock to `ordering`. If Omise status drift → resync + unlock.
- `failed`/`refunded` + `payment_pending` → unlock to `ordering`, clear `locked_amount`, 200
- `processing` → keep 400 (genuinely in flight)
- `expired` → idempotent 200 (unchanged)
- New method `_recover_paid_stuck_order()` handles the PAID path

### Fix 2: `reconcile_gateway_charge` retry (`services.py:240+`)

PAID charge + `payment_pending` unfinalized order → retry `finalize_payment(order, triggered_by_gc=gc)`. Auto-heals webhook-lost route on every order-detail read. Mismatch caught + logged; Fix 1 is the manual hatch.

### Fix 3: `_handle_existing_charge` local-PAID parity (`services.py:484+`)

Before raising `AlreadyPaidError`, attempt `finalize_payment(order, triggered_by_gc=existing_charge)` — mirrors remote-successful branch at line 497-515. Mismatch logged, `AlreadyPaidError` still raised. Prevents "Order already paid" response while order stays stuck.

### Frontend unchanged

Callers already treat 200 as success:
- `FormCard.js:69-71` → `expirePendingCharge()` → success → `onUnlockPayment()`
- `Itineraries.js:46-47` → success → `refetchCart()`
- `PaymentComponent.js:153` → same pattern

## Key files

| File | Purpose |
|------|---------|
| `smartenplus-backend/payments/views.py` | `ExpirePendingChargeView` + `_recover_paid_stuck_order()` |
| `smartenplus-backend/payments/services.py` | `reconcile_gateway_charge` + `_handle_existing_charge` |
| `payments/tests/test_expire_view.py` | `ExpireRecoveryPaidStuckTest` (9 new tests) |
| `payments/tests/test_reconciliation.py` | `ReconcilePaidStuckRecoveryTest` (4 new tests) |
| `payments/tests/test_handle_existing_charge.py` | `AlreadyPaidFinalizesStuckOrderTest` (3 new tests) |

## Tradeoffs

| Aspect | Choice | Why |
|--------|--------|-----|
| Finalize without amount check on verified-PAID | Yes | Money confirmed at Omise. Mismatch is bookkeeping, logged loud for ops refund review |
| Fallback to `ordering` if finalize fails | Yes | Better stuck-at-ordering than stuck-at-payment_pending |
| Keep amount-safe path in reconcile (Fix 2) | Yes | Automatic path stays conservative; Fix 1 is the manual hatch for mismatch |
| Keep 400 for `processing` | Yes | Don't interfere with genuinely in-flight payments |
| No frontend change | Yes | Frontend already handles 200 success path correctly |

## Verification

Tests: 278 pass (`python manage.py test payments --keepdb`)

Manual:
1. Reproduce via Django shell above → `POST /payments/order-charge/.../expire/` + email → 200 `{status: 'recovered'}`, order = `paid`
2. FAILED charge + stuck order → expire → 200 `{status: 'unlocked'}`, order = `ordering`
3. PROCESSING charge → expire → still 400
4. EXPIRED charge → idempotent 200 (regression unchanged)

Production recovery for PLB0229785:
```
POST /payments/order-charge/chrg_test_67zrcauou19uk2t655l/expire/
body: {"email": "<owner email>"}
```
Or Django shell: `finalize_payment(Order.objects.get(order_id='PLB0229785'))`

## Related

- [[payment-deep-review-2026-06-12]] — H5: paid-but-unfinalized order invisible
- [[payment-backend-charge-flow]] — charge lifecycle
- [[payment-frontend-checkout-flow]] — frontend expire flow
- [[payment-implement-plan-2026-06-12]] — batch 4: H5+M5 resilience pair
