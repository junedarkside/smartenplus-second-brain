# NextAuth Session Shape

## Summary
SmartEnPlus NextAuth session has custom root fields — `session.email` always undefined.

## Why It Matters
Hits every auth feature. Wrong access pattern (`session?.email`) silently returns undefined — no error, just blank email causing silent failures in cart, payment, order pages.

## Detail
```js
// Correct session shape:
{
  id,           // custom root field — use for auth check
  accessToken,  // custom root field
  user: {
    email,      // ONLY here
    name,
    image,
  }
}

// Auth check:  session?.id
// Email:       session?.user?.email   ← always here
// NEVER:       session?.email         ← always undefined
```

Guest email sources:
- Checkout: `formData?.email`
- Order pages: `router.query.email ? decodeURIComponent(router.query.email) : null`

## Constraints / Gotchas
- `expirePendingCharge()` must NOT send `?email=` when authenticated — backend routes by param presence, not value
- Condition on `!token` (not `!!email`) to determine auth context

## Related
- [[payment-integration]]
- [[checkout-flow]]
- [[accounts]]