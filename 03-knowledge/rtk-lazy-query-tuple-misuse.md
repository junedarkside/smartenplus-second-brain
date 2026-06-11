# RTK Lazy Query Tuple Misuse

## Summary

`useLazyXQuery` hooks return a `[trigger, result]` tuple and take NO query args — passing args + object-destructuring produces silent dead code with no error.

## Problem

```js
// WRONG — looks plausible, compiles, never fires a request
const { data, isLoading } = useLazyCheckCartIdQuery({ cartId, email }, {
  refetchOnMountOrArgChange: true,
});
// data === undefined, isLoading === undefined, forever

// RIGHT — lazy form
const [checkCart, { data, isLoading }] = useLazyCheckCartIdQuery();
// later: checkCart({ cartId, email })

// RIGHT — eager form (if you want args + auto-fetch)
const { data, isLoading } = useCheckCartIdQuery({ cartId, email }, {
  refetchOnMountOrArgChange: true,
});
```

Object-destructuring an array yields `undefined` for every named key — no runtime error, no request, no warning. The bug reads like a working eager query to reviewers.

## Why It Matters

- Found live in `components/UI/BookButton.js:41-43` (harmless there only because the values were unused — but it masked itself for months).
- Any guard built on the phantom `data`/`isLoading` silently never activates.

## Detection

Grep for lazy hooks destructured with `{`:
```
grep -rn "} = useLazy" --include="*.js"
```
Every hit is a bug — lazy hooks always destructure with `[`.

## Related

[[booking-payment-e2e-audit-2026-06-11]] · [[rtk-cart-tag-invalidation-auto-refetch]]
