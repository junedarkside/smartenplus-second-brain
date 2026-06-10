# RTK Query Cart Tag Invalidation — Auto-Refetch Pattern

## Summary
`createCartItem` mutation invalidates `Cart:{cartId}` tag → `checkCartId` query auto-refetches. Cart data stays live without manual `refetch()` calls or `onSuccess` wiring.

## Details

`api-slice.js:58` — `checkCartId` provides tags:
```js
providesTags: (result, error, { cartId }) => [{ type: 'Cart', id: cartId }, { type: 'Cart', id: 'LIST' }]
```

`api-slice.js:119` — `createCartItem` invalidates:
```js
invalidatesTags: (result, error, { cartId }) => [{ type: 'Cart', id: cartId }]
```

Tag match → RTK automatically re-runs `checkCartId` → `data?.cart_item` updates → all components consuming `cartItems` re-render with fresh data.

Same pattern applies to `updateCartItem` (line 167) and `deleteCartItem` (line 180) — all invalidate `Cart:{cartId}`.

## Why It Matters

Components receiving `cartItems={data?.cart_item}` (e.g. `CheckoutRelatedTrips`, checkout form) **do not need `onSuccess` callbacks or manual refetch calls** after cart mutations. RTK handles it via tag invalidation.

Implication: `RecommendationCard.js` not passing `onSuccess` to modal is **not a bug** — cart auto-refetches anyway.

## Gotcha

`recommendationsApi` is a **separate RTK slice** with zero tags. Cart mutation does NOT invalidate recommendations cache. Recommendations only update when query args change (`sourceContractId`, `recType`).

## Related
[[people-also-book-checkout-audit]] [[cross-sell-placement-strategy]]
