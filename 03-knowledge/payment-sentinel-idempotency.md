# Payment Sentinel Idempotency

## Summary
Timestamp fields as exactly-once guards — better than booleans for any side effect that must fire once.

## Why It Matters
Reusable pattern beyond payments. Any high-risk side effect (email, booking confirm, settlement) can use this. Timestamp gives audit visibility at zero cost.

## Detail
Use a nullable timestamp field (`payment_finalized_at`, `payment_notification_sent_at`) as sentinel:
- `WHERE field IS NULL` before acting
- Set inside atomic transaction
- Already set → skip (idempotent)
- Timestamp > boolean: stores *when* it happened, not just *that* it happened — free audit trail

```python
# Guard pattern
if order.payment_finalized_at is not None:
    return  # already done
# ... do the work ...
order.payment_finalized_at = now()
order.save(update_fields=['payment_finalized_at'])
```

## Constraints / Gotchas
- Must set sentinel inside `select_for_update()` block — race condition if set after
- `payment_failed` does NOT set `payment_finalized_at` — only success sets sentinel
- High-risk tasks (email, booking confirm) additionally guard via `UserJourneyEvent` dedup

## Related
- [[payment-integration]]
- [[payment-system]]
- [[celery-tasks]]
