---
name: payment-idempotency-key-name-error
description: IdempotencyKey without `key=` prefix breaks charge creation in `initiate_order_charge` — NameError on `IdempotencyKey` class, causing server error. Missing prefix prevents Omise from recognizing key.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: payment-deep-review
---

# Payment Idempotency Key Name Error

## Summary
`IdempotencyKey` without `key=` prefix breaks charge creation in `initiate_order_charge`. NameError on class → server error. Omise doesn't recognize key format.

## Why It Matters
Idempotency prevents double-charge on retry. Broken key = race condition → duplicate charges on network flakiness.

## Detail
**Bug pattern:**
```python
# WRONG (NameError if IdempotencyKey not imported)
idempotency_key = IdempotencyKey.generate('order_123')
charge = omise.Charge.create(
    amount=1000,
    currency='THB',
    idempotency_key=idempotency_key,  # Wrong object type
)

# CORRECT
import omise
idempotency_key = f"key_{order_id}_{timestamp}"  # Omise format
charge = omise.Charge.create(
    amount=1000,
    currency='THB',
    idempotency_key=idempotency_key,
)
```

**Fix:** Use `omise.IdempotencyKey` class OR generate string with `key=` prefix. Omise requires `key=` prefix to recognize idempotency keys.

## Constraints / Gotchas
Key must be unique per order. Format: `key_{order_id}_{timestamp}`. Max 250 chars.

## Related
- [[payment-deep-review]] — keyless-branch NameError + duplicate charge risk
