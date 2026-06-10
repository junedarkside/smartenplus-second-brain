# People Also Book — Checkout Booking Flow Audit

## Summary
3-agent audit + 2-pass debug-mantra falsification. Initial audit: 4 bugs, 2 UX concerns. After code verification: **1 real bug confirmed**. All others overturned. Audited + verified 2026-06-10.

## Context
Checkout page shows recommended trips. Each card has a Book button → modal opens with date pre-filled from `cartItems[last].traveling_date`. User adjusts passengers, submits → adds to cart.

## Flow
```
CheckoutRelatedTrips.js:154
  → bookingDate = cartItems[last].traveling_date
  → RecommendationCard → defaultDate prop
      → RecommendationBookingModal.js:36-39
          → selectedDate = useState(() => new Date(defaultDate))
          → POST /carts/{cartId}/cartitems/
```

## Confirmed Bug (1)

### P1 — Duplicate detection toast never fires
- Backend `serializers.py:349-351` and `392-394`: duplicate raises `serializers.ValidationError` → HTTP **400**
- Frontend `RecommendationBookingModal.js:175`: catches only `err?.status === 409`
- HTTP 409 fires exclusively for `payment_pending` at `views.py:190` — unrelated
- **User sees:** generic "Could not add to cart" — never sees "already in cart" message

**Fix (2 lines added to existing catch block):**
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

## Overturned Findings

| Claim | Evidence Against |
|-------|-----------------|
| Empty ratecards before date selected | `RecommendationBookingModal.js:63` guards `if (!selectedDateStr \|\| raw.length === 0) return raw` — returns raw ratecards before deduplication is called |
| Stale date on modal reopen | Each `RecommendationCard` = separate instance. Card B has own `useState(defaultDate)`. No cross-card stale state. |
| Greyed date with no explanation | `availabilityError` at line 191-197 populates immediately when `selectedDateStr` is non-null + unavailable. Shows `"Not operating on this day of week"` in DatePicker `helperText`. Already handled. |
| Date string comparison brittle | `errors.beforeStart/afterEnd` never read by modal. Gate uses `isBookingDateInRange()` with proper `new Date()`. Works. |

## What Looks Correct

- Pre-fill UX design — correct. `shouldDisableDate` + `availabilityError` protect user from invalid dates.
- `availabilityError` shown immediately when pre-filled date is unavailable — red outline + message on open ✓
- `RecommendationBookingModal.js:63` guard — raw ratecards returned before deduplication when no date ✓
- Backend double-validates `traveling_date` ✓
- Separate card instances — no cross-card stale state ✓
- `findMinVehicleSeat` returns 999 for null ✓
- PRIVATE/CHARTER vs JOIN ratecard logic ✓
- `child` field matches backend serializer ✓
- `user` nullable for guests ✓
- 409 for `payment_pending` handled correctly ✓

## Design Verdict

**Design is correct. One real execution bug — 2-line fix.**

Pre-filling cart's `traveling_date` is right UX. Calendar guards handle invalid dates with clear error messages. Only defect: duplicate item shows wrong toast (generic error instead of "already in cart").

## Related
[[cross-sell-placement-strategy]] [[recommendation-type-selection-by-service-category]] [[payment-checkout-architecture-audit]]
