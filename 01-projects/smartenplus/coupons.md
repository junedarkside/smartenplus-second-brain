# Coupons — Discount System

## Summary
`orders.models.Coupon`. Percentage or fixed discount. `times_used` incremented via `F()+1` in `finalize_payment()`. Restrictions: per-user limit, new-users-only, operator/route whitelist.

---

## Model Fields

- `code` — unique string
- `valid_from` / `valid_to` — datetime range
- `discount_type` — `percentage` or `fixed`
- `discount_value` — Decimal. Percentage: max 100 (validated `clean()`).
- `active` — boolean
- `max_uses` — nullable (null = unlimited)
- `times_used` — auto-incremented via `F()+1` in `finalize_payment()`, not save()
- `limit_per_user` — default True. One use per email.
- `new_users_only` — default False. Only users with no prior paid orders.
- `applicable_operators` — M2M to `Operator`. Blank = all.
- `applicable_routes` — M2M to `Route`. Blank = all.

**Validation:** `clean()` checks percentage ≤ 100, valid_from < valid_to.

---

## Usage in `finalize_payment()`

Atomic increment:
```python
Coupon.objects.filter(id=coupon_id).update(times_used=F('times_used') + 1)
```

`F()` expression — no race condition on concurrent finalizations.

---

## Coupon Application

`ApplyCouponView` (admin-dashboard) applies coupon to order. `RemoveCouponView` removes.

---

## Related
- [[backend-architecture]]
- [[payment-system]] (finalize_payment → coupon F()+1)