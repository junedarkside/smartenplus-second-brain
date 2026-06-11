# Redux Store Architecture

## Summary
8 non-obvious store patterns: 7-version persist migration, cross-tab cart invalidation, dual reset mechanism, SSR no-op storage, deprecated cart-slice, auth bypass whitelist, checkout TTL, payment reconciliation.

## Context
`store/index.js`. Built on Redux Toolkit + redux-persist. Non-standard patterns throughout — know these before touching store config.

## Patterns

### 1. Redux-Persist v3→v7 Migration (store/index.js:68-169)
```js
migrate: (state, version) => {
  // v4-v6: dayTrip → activities rename
  // v5-v7: inject checkout slice for old states
  // v3 falls through (epoch reset)
}
```
On rehydration error: clears storage + `window.location.reload()` (lines 195-200). Silent page refresh. No user-visible error.

### 2. Cross-Tab Cart Invalidation (store/index.js:215-224, store/cart-version.js)
```js
// Tab A: bump version in localStorage
bumpCartVersion()  // writes CART_VERSION_KEY = Date.now()

// Tab B: storage event listener
window.addEventListener('storage', (e) => {
  if (e.key === CART_VERSION_KEY) {
    dispatch(apiSlice.util.invalidateTags([{ type: 'Cart', id: 'LIST' }]))
  }
})
```
`setTimeout(..., 0)` defers invalidation until persist hydration completes. Uses separate key (not full persist key) to avoid noisy re-hydrations triggering other listeners.

### 3. Dual Store Reset (store/index.js:49-61, 226-245)
Two distinct reset mechanisms — different callers, different behaviors:
```js
// resetAppState(): sync, bypasses purge
// Manually calls storage.removeItem(persistKey) + dispatches state=undefined
// Used for: session expiry mid-session

// clearStoreAndResetApp(): async purge + sync dispatch
// persistor.purge() must complete before dispatch or state re-hydrates partially
// Used for: explicit logout
```
**Never swap them.** Using resetAppState for logout = purge not called, persisted data survives.

### 4. SSR No-Op Storage (store/sync_storage.js:3-20)
```js
// Server: typeof window === 'undefined'
const storage = typeof window !== 'undefined'
  ? createWebStorage('local')
  : { getItem: () => Promise.resolve(null), setItem: () => Promise.resolve(), removeItem: () => Promise.resolve() }
```
Silently drops all persist state during SSR. Data only rehydrates on client mount. getStaticProps/getServerSideProps always see initial Redux state. See [[redux-persist-gate-scope-gap]].

### 5. Legacy cart-slice (store/cart-slice.js)
```js
// DEPRECATED fields (do NOT use):
items, total, changed, cartVersion

// NOT deprecated — still required:
setCartId(state, action) { state.cartId = action.payload }
```
`cartId` drives RTK Query cache lookups — cannot remove. New code: read `cartId` only. Never write `items`/`total` (they're stale). See [[cart-reprovision-after-reset]].

### 6. Checkout Slice 48-Hour TTL (store/checkout-slice.js:4-11, 42-44, 154-159)
```js
// Every save updates expiresAt
expiresAt: Date.now() + 48 * 60 * 60 * 1000

// No auto-clear — component must check
const expired = useSelector(selectIsCheckoutDataExpired)
```
No middleware or saga watches this. If component doesn't call selector on mount, stale data persists indefinitely.

### 7. paymentStatusSlice Reconciliation (store/paymentStatusSlice.js:25-33, store/index.js:204)
```js
// Fires ONCE after store rehydration
dispatch(reconcileStaleProcessing())
// Clears isPaymentProcessing=true older than 30min
```
No periodic loop. Payment started > 30min before page load will be cleared. Payment started < 30min before page load persists until next rehydration. See [[payment-frontend-flow-mechanics]].

### 8. Auth Bypass Whitelist — 3 Separate Lists
```js
// store/api/api-slice.js:11-20
// store/api/tripsApi.js:12-21
// store/api/dayTripsApi.js:40-47
const PUBLIC_ENDPOINTS = ['getTrips', 'getTripDetail', ...]
// Endpoints in list → skip getSession() header injection
```
No shared constant. If one list is updated without others, auth bugs cascade silently. Adding new public endpoint requires updating all 3 files.

## Related
- [[redux-persist-gate-scope-gap]] — PersistGate scope + pre-rehydration hazards
- [[rtk-query-advanced-patterns]] — cache tag patterns, fixedCacheKey
- [[cart-reprovision-after-reset]] — cartId lifecycle after reset
- [[payment-frontend-flow-mechanics]] — paymentStatusSlice stale processing
- [[checkout-state-persistence]] — checkout slice usage in persistence layer
