# Payment Finalize Deep Dive

## Summary
`finalize_payment()` has 6 non-obvious behaviors: log-only snapshot validation, path-dependent amount mismatch, expired→successful recovery, superseded charge guard, cross-order lock, and CAS notification dedup.

## Context
`payments/services.py:284-408`. Called from 3 paths: webhook (primary), reconcile polling, retry. All behavior here is SSOT — add payment success side effects here, never in callers.

## Critical Behaviors

### 1. Snapshot Validation — Log-Only (lines 317-348)
Cart hash compared against CheckoutSnapshot at finalization time:
```python
if not snapshot.is_valid_for_cart(current_hash):
    logger.warning("cart_may_have_drifted order=%s", order.order_id)
    # does NOT return, does NOT raise
    # payment proceeds even if cart changed mid-payment
```
**Implication:** Items added/removed between checkout start and payment completion don't block finalization. Designed to not strand customers.

### 2. Amount Mismatch — Path-Dependent (lines 304-315)
```python
# Webhook path: triggered_by_gc = GatewayCharge object → CHECK
if triggered_by_gc is not None and order.locked_amount is not None:
    if triggered_by_gc.amount != order.locked_amount:
        raise PaymentAmountMismatchError(...)  # caught upstream, NOT re-raised

# Reconcile path: triggered_by_gc = None → SKIP CHECK
```
See [[payment-exception-catalog]] for why mismatch is never re-raised.

### 3. Expired → Successful Recovery (payments/views.py:224-230)
```python
# If local GatewayCharge.status == EXPIRED but Omise says successful:
if gc.status == 'expired' and verified_status == 'successful':
    logger.warning("recovering_expired_charge gc=%s", gc.id)
    # proceeds to mark PAID
```
**Use case:** User scans PromptPay QR, completes payment in bank app, but QR UI already showed "expired" (10-min TTL elapsed). Omise received the payment. System auto-recovers.

### 4. Superseded Charge Guard (payments/views.py:295-309)
```python
# Called when charge FAILS or EXPIRES via webhook
newer_charge = GatewayCharge.objects.filter(
    order=order, created__gt=charge.created
).exclude(status__in=['expired', 'failed']).first()

if newer_charge:
    # User switched payment method; this charge was superseded
    # Skip failure finalization — don't mark order payment_failed
    return
```
**Prevents:** User switches PP → mobile banking → PP fails → order incorrectly marked failed.

### 5. Cross-Order Pending Lock (payments/services.py:640-664)
```python
# Before creating new charge, lock ALL orders for this cart
orders = Order.objects.select_for_update(nowait=False).filter(
    cart=cart, status__in=['payment_pending']
)
# If any exist → PendingChargeError → 409
```
**Prevents:** Two browser tabs creating separate orders for same cart, both reaching payment_pending simultaneously.

### 6. Notification Dedup — CAS Guard (payments/views.py:405-408)
```python
# Atomic compare-and-set prevents double emails/SMS on concurrent webhooks
updated = Order.objects.filter(
    pk=order.pk, payment_notification_sent_at__isnull=True
).update(payment_notification_sent_at=now())
if updated == 1:
    send_notifications()  # only fires if this update won the race
```
Notifications fire in `on_commit()` — after transaction commits. CAS guard prevents duplication even with retried webhooks.

### Side Effect Order (lines 350-366)
1. Delete CartItems (clears cart)
2. Increment `coupon.times_used` via `F()+1`
3. `confirm_booking_items_for_order()` (confirms all BookingItems)
4. Order → `paid`, `payment_finalized_at=now()`, `locked_amount=None`
5. `on_commit`: fire notifications (guarded by CAS)

**Critical:** Cart cleared BEFORE order marked paid. If transaction rolls back after cart clear, retry will re-enter idempotency guard via `payment_finalized_at`.

## Related
- [[payment-gateway-charge-architecture]] — finalize_payment SSOT principle
- [[payment-exception-catalog]] — PaymentAmountMismatchError contract
- [[omise-webhook-security]] — verification before finalize_payment fires
- [[payment-sentinel-idempotency]] — payment_finalized_at sentinel pattern
- [[payment-celery-expiry-strategy]] — reconcile path that calls finalize_payment
