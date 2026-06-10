# Django 400 vs 409 — Duplicate Cart Item Detection

## Summary
Backend raises HTTP 400 (not 409) for duplicate cart items. Frontend must catch 400 and inspect the error message string — not rely on status 409.

## Details

**Backend behavior** (`carts/serializers.py:349-351`, `392-394`):
```python
# Authenticated user
if CartItem.objects.filter(contract_id=contract_id, traveling_date=traveling_date, user_id=user_id).exists():
    raise serializers.ValidationError('A cart item with this contract and travel date already exists for this user.')

# Guest
if CartItem.objects.filter(contract_id=contract_id, cart_id=cart_id, traveling_date=traveling_date, user_id=None).exists():
    raise serializers.ValidationError('A cart item with this contract, cart, and travel date already exists for this guest.')
```

`serializers.ValidationError` → HTTP **400**. Not 409.

**HTTP 409 is only for `payment_pending`** (`carts/views.py:190`):
```python
return Response(data, status=status.HTTP_409_CONFLICT)  # only payment_pending
```

## Frontend Fix Pattern

`RecommendationBookingModal.js:177-183`:
```js
} else if (err?.status === 400) {
  const detail = typeof err?.data === 'string' ? err.data : (err?.data?.detail || '');
  if (detail.toLowerCase().includes('already exists')) {
    toast.info('This trip is already in your cart for this date', autoClose);
  } else {
    toast.error('Could not add to cart. Please try again.', autoClose);
  }
}
```

Check `includes('already exists')` — covers both authenticated and guest error strings.

## Why It Matters

Any cart mutation UI that shows "already in cart" feedback must catch **400**, not 409. Catching only 409 means the duplicate message never fires — user sees generic error instead.

## Related
[[payment-checkout-architecture-audit]] [[people-also-book-checkout-audit]]
