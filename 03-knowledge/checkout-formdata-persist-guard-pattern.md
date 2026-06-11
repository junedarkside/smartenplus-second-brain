# Checkout formData Persist Guard Pattern

## Problem

`useEffect` that clears Redux/state assignments fires on component mount before RTK Query resolves, permanently blocking sessionStorage restore.

## Root Cause Chain (C1)

1. `_app.js` — PersistGate wraps only `<RefreshTokenHandler>` / `<DevToolsProvider>`, NOT `<Component>`. Component mounts before Redux-persist rehydration.
2. `checkout/index.js` — Clear-assignments effect has no cart-loaded guard:
   ```js
   useEffect(() => {
     if (!hasMixedPassengerCounts) {  // ← fires on mount
       dispatch(clearPassengerAssignments());
       setFormData(prev => ({ ...prev, passengerAssignments: {} }));
     }
   }, [hasMixedPassengerCounts, dispatch]);
   ```
3. On mount: `data=undefined` → `passengerCounts=[]` → `hasMixedPassengerTypes([])=false` (length ≤ 1 guard) → clear fires.
4. `setFormData(prev => ({...undefined, passengerAssignments:{}}))` → `formData = { passengerAssignments:{} }` (truthy).
5. Inline saver writes gutted object to sessionStorage immediately.
6. Restore effect permanently blocked: `formData !== undefined` guard (formData was just set).

## Fix

```js
const isCartLoaded = !!data;  // stable bool — stays true after first load, doesn't re-trigger on refetch

useEffect(() => {
  if (isCartLoaded && !hasMixedPassengerCounts) {  // ← isCartLoaded gate
    dispatch(clearPassengerAssignments());
    setFormData(prev => ({ ...prev, passengerAssignments: {} }));
    setHasStaleData(false);
  }
}, [isCartLoaded, hasMixedPassengerCounts, dispatch]);
```

### Why `!!data` not `data` in deps

`data` (full RTK Query response) in deps re-runs effect on every refetch. `!!data` is a stable boolean — flips `false→true` once on first load, stays `true` on subsequent refetches. Avoids unnecessary clears.

### Why not fix PersistGate in _app.js

Wrapping `<Component>` in PersistGate has SSR/hydration implications. The `isCartLoaded` guard is minimal and correct either way — remains safe if PersistGate is fixed later.

## Related Pattern: HOC Cart Clear (C2)

RTK Query `.unwrap()` catch block must guard by error status:

```js
// WRONG — clears cartId for all errors including 500/timeout
} catch (error) {
  dispatch(cartActions.setCartId(null));
}

// CORRECT — only 404 means cart is gone on backend
} catch (error) {
  if (error?.status === 404) {
    dispatch(cartActions.setCartId(null));
    dispatch(cartActions.setTotal(0));
  }
}
```

RTK Query fetchBaseQuery error shapes:
- HTTP error → `{ status: 404, data: {...} }` — numeric
- Network error → `{ status: 'FETCH_ERROR' }` — string
- Timeout → `{ status: 'TIMEOUT_ERROR' }` — string

Only numeric `404` warrants cart clear. String statuses = transient; preserve cartId.

## Files

- `pages/checkout/index.js:183-201` — isCartLoaded gate
- `components/HOC/check-and-createcart.js:67` — 404-only clear
- `helpers/passengerTypeHelper.js:33` — `hasMixedPassengerTypes` length guard (why empty array → false)

## Context

SmartEnPlus checkout. Fixed `cb817d9` on `develop` 2026-06-11. Session #97.

## Related
- [[payment-audit-bugs-2026-06-11]] — confirmed bugs + C1/C2 fixes
- [[redux-persist-gate-scope-gap]] — PersistGate SSR/mount timing issue
- [[payment-checkout-5-principles]] — checkout architecture
- [[checkout-state-persistence]] — dual persistence strategy (guest vs logged-in), useCartSync ordering
- [[checkout-hoc-architecture]] — withCartValidation 404-only cart clear (C2 fix location)
