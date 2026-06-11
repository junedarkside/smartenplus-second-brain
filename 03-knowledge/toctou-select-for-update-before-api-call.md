# TOCTOU Guard: `select_for_update()` Before External API Call

## Summary
Acquire DB row lock BEFORE calling external API (Omise, Stripe, etc.) to prevent concurrent webhook from finalizing the same record between check and update.

## Pattern
```python
with transaction.atomic():
    order = Order.objects.select_for_update().get(pk=order_id)
    # Lock held — concurrent webhook blocks here until transaction completes
    external_api.expire(charge_id)   # external call inside lock
    order.status = 'ordering'
    order.save()
# Lock released — webhook can now proceed (sees updated state)
```

## Why Order Matters
```
BAD:
1. Check: order.status == 'payment_pending' ✓
2. Call: omise_charge.expire()
3. [webhook arrives, sees pending, finalizes order → status = 'paid']
4. Update: order.status = 'ordering'  ← OVERWRITES paid status!

GOOD:
1. select_for_update() — acquires lock
2. Call: omise_charge.expire()        ← webhook blocks here
3. Update: order.status = 'ordering'
4. Commit — webhook unblocks, sees 'ordering', skips finalization
```

## Constraints
- External API call inside `transaction.atomic()` = DB connection held during network call. Acceptable for low-frequency operations (charge expiry). NOT acceptable for high-frequency or slow APIs — use optimistic locking instead.
- Always lock the PARENT record (Order), not just the charge.

## SmartEnPlus Usage
`payments/services.py:444-553` — `_handle_existing_charge()` stale charge expiry.

## Related
- [[payment-backend-charge-flow]] — TOCTOU guard in charge flow
- [[payment-finalize-deep-dive]] — `select_for_update()` in finalize_payment()
- [[multitab-payment-race-condition-fixes]] — broader race condition catalog
