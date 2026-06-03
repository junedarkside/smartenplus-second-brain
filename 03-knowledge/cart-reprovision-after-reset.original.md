# Cart Reprovisioning After Reset

## Summary
`resetCart()` nulls `cartId` — must fire `createCart()` immediately after or BookButton breaks on trip/search pages.

## Why It Matters
`withCartValidation` HOC is the only mechanism creating new carts. Trip detail + search pages are NOT wrapped — `BookButton` reads `null`, fails silently. Two order pages require this pattern.

## Detail
```js
dispatch(cartActions.resetCart({ items: [], total: 0 }));
createCart({ email }).unwrap()
  .then(res => { if (res?.id) dispatch(cartActions.setCartId(res.id)); })
  .catch(() => {}); // HOC recovers on next booking page
```

Auth email: `session?.user?.email`
Guest email: `router.query.email ? decodeURIComponent(router.query.email) : null`

Files that need this pattern:
- `pages/orders/[orderid].js`
- `pages/guest-order/[orderId].js`

## Constraints / Gotchas
- Fire-and-forget — do NOT await before continuing page logic
- `cartActions.resetCart()` on ORDER pages ONLY — never in `useOmisePayment.js`
- Pages with `BookButton` NOT wrapped in `withCartValidation` → `cartId` stays null without this

## Related
- [[payment-integration]]
- [[cart]]
- [[checkout-flow]]
