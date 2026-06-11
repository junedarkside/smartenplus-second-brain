# Payment Backend Charge Flow

## Summary
6 non-obvious backend patterns in charge initiation: DB-level pending constraint, stale charge TOCTOU guard, 5-second reconcile throttle, proactive PromptPay expiry (C3b), AllowAny + manual ownership auth, grandTotal satang conversion.

## Context
`payments/models.py`, `payments/views.py`, `payments/services.py`. These patterns prevent double-charges, race conditions, and API hammering. Miss any one → production incident.

## Patterns

### 1. DB Constraint: One Pending Redirect Charge Per Order (`payments/models.py:37-50`)
```python
class Meta:
    constraints = [
        UniqueConstraint(
            fields=['order'],
            condition=Q(status='pending') & ~Q(payment_method='promptpay'),
            name='unique_pending_redirect_charge_per_order'
        )
    ]
```
Database blocks multiple `PENDING` redirect-method charges for same order. PromptPay excluded — inline QR can be regenerated. Service layer also guards via `PendingChargeError` (dual enforcement). DB constraint is last-resort safety net for race conditions.

### 2. Stale Charge Expiry with TOCTOU Guard (`payments/services.py:444-553`)
```python
# _handle_existing_charge() — called when idempotency key matches but charge is stale
with transaction.atomic():
    order = Order.objects.select_for_update().get(pk=order.pk)
    # Lock FIRST, then expire — prevents race with webhook finalizing same order
    omise_charge.expire()
    gc.status = 'expired'
    order.payment_notification_sent_at = None  # allow re-notification on next success
    order.status = 'ordering'
    order.locked_amount = None
    order.save()
```
TOCTOU: Time-of-check-to-time-of-use. Without lock: webhook could finalize order between `expire()` call and status reset → order stays `payment_pending` forever. `payment_notification_sent_at = None` reset is critical — allows success notification to fire on the new charge.

### 3. `reconcile_gateway_charge` 5-Second Throttle (`payments/services.py:237-238`)
```python
# Skip reconciliation if charge was updated less than 5 seconds ago
if (now() - gc.updated).seconds < 5:
    return gc  # already fresh, skip Omise API call
```
Called on every order-detail page load. Without throttle: every page view = Omise API call = 429 rate limit. Uses `updated` timestamp (auto_now), not `created` — charge may be old but recently reconciled.

### 4. Proactive PromptPay Expiry Before Blocking (`payments/services.py:580-616`)
```python
# C3b: before raising PendingChargeError, check if pending PP is stale
pending_pp = GatewayCharge.objects.filter(
    order=order, payment_method='promptpay', status='pending'
).first()
if pending_pp and (now() - pending_pp.created) > METHOD_EXPIRY[OmiseMethod.PROMPTPAY]:
    # Proactively expire — let user switch methods without explicit cancel
    _expire_charge_locally(pending_pp, order)
    # Falls through to create new charge
```
User switches PP → Mobile Banking without clicking Cancel → backend auto-expires the stale PP charge. Only applies when replacing PP (not other methods). Frontend does NOT need to call `expirePendingCharge()` before switching from PP.

### 5. `ChargeOrderView` Auth — AllowAny + Manual Ownership (`payments/views.py:79, 106-109`)
```python
permission_classes = [AllowAny]  # intentional — supports guest checkout

# Manual ownership check:
user_id = request.data.get('user_id')
email = request.data.get('email')
if not (user_id == request.user.id or email == order.email):
    return Response({'error': 'unauthorized'}, status=403)
```
`AllowAny` because guests have no token. Ownership validated via `user_id` (auth) OR `email` (guest). Both must match the order record. Guest orders linked to email-only profile.

### 6. `grandTotal` Satang Conversion (`payments/views.py:116`)
```python
# Frontend sends: Math.round(grandTotal * 100) — satang (minor units)
# Backend converts: amount_thb = grandTotal / 100 / currency_rate
amount_thb = Decimal(request.data['grandTotal']) / 100 / currency_rate
```
Frontend always sends in satang. Backend divides by 100 to get THB basis, then divides by currency rate for foreign amounts (USD, JPY, etc.). JPY: `/ 100` then `/ rate` — still correct because `_to_minor_units()` will re-multiply at charge creation using currency-aware factor.

## Related
- [[omise-client-integration]] — Omise SDK patterns used in these flows
- [[payment-charge-service-layer]] — create_charge orchestration
- [[payment-exception-catalog]] — PendingChargeError, LockedAmountError HTTP responses
- [[payment-finalize-deep-dive]] — what happens after charge succeeds
- [[payment-celery-expiry-strategy]] — Celery-side stale charge handling
- [[payment-gateway-charge-architecture]] — GatewayCharge model + canonical charge rule
