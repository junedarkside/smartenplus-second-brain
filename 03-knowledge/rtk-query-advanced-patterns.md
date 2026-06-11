# RTK Query Advanced Patterns

## Summary
6 non-standard RTK Query patterns in api-slice.js: child/children field normalization, fixedCacheKey mutation dedup, intentional missing invalidatesTags, bookmark 409/404 suppression, "null" string cartId guard, date-based forceRefetch.

## Context
`store/api/api-slice.js`. Patterns deviate from RTK Query docs — each has a specific reason. Know these before adding new endpoints or mutations.

## Patterns

### 1. `child` → `children` Field Normalization (api-slice.js:36-50, 81-99, 128-151)
```js
// Backend returns: { child: 2 }
// Frontend expects: { children: 2 }
transformResponse: (response) => ({
  ...response,
  cart_item: response.cart_item?.map(item => ({
    ...item,
    children: item.children ?? item.child ?? 0
  }))
})
```
Applied in 3 separate mutation transformResponse blocks. No shared helper. **Risk:** backend field rename → 3 silent breaks. `children ?? child ?? 0` means 0-value children are safe.

### 2. fixedCacheKey per cartItemId (api-slice.js:152-157)
```js
updateCartItem: builder.mutation({
  extraOptions: ({ cartItemId }) => ({
    fixedCacheKey: `update-cart-item-${cartItemId}`
  })
})
```
Passenger count fields fire rapid increments (+1, +1, +1). Without fixedCacheKey, RTK allows parallel mutations → multiple simultaneous PATCH requests → 429. Per-item key forces serial queueing per cartItemId only (parallel updates to different items still allowed).

### 3. saveCheckoutInfo Missing invalidatesTags — Intentional
```js
saveCheckoutInfo: builder.mutation({
  // No invalidatesTags — intentional
  // Reason: useCheckoutAutoSave dispatches to Redux before this mutation fires
  // RTK cache stays in sync via Redux, not tag invalidation
})
```
**Risk:** if `useCheckoutAutoSave` hook fails or races, backend and RTK cache diverge silently. No fallback sync.

### 4. Bookmark 409/404 Suppression (api-slice.js:222-289)
```js
// POST bookmark → 409 (already exists) = treat as success
// DELETE bookmark → 404 (already gone) = treat as success
```
`unique_together` constraint = idempotent. Surfacing 409/404 as errors causes optimistic flip then 100ms revert visible glitch. Suppression happens at **component level** (catch block returns early), not at RTK level. See `r3-leader-synthesis.md §B`.

### 5. `cartId !== 'null'` String Guard (api-slice.js:45-51, pages/checkout/index.js:68-75)
```js
// Wrong: if (cartId)  ← passes for string "null"
// Correct:
if (cartId && cartId !== 'null' && typeof cartId === 'string') {
  // safe to use cartId
}
```
Redux initializes `cartId` as JS `null`. redux-persist can serialize `null` as string `"null"`. RTK Query endpoint called with `"null"` → hits `/carts/null/` → 429 spam. String guard prevents this.

### 6. Recommendations Date forceRefetch (recommendationsApi.js:42-45)
```js
serializeQueryArgs: ({ queryArgs: { date, ...rest } }) => rest,
forceRefetch: ({ currentArg, previousArg }) =>
  currentArg?.date !== previousArg?.date
```
Date excluded from cache key (prices are time-sensitive). forceRefetch fires new request when date string changes. **Risk:** if `date` is a Date object (not string), reference inequality causes refetch on every render. Must pass YYYY-MM-DD string.

## What Is Standard
For reference — these RTK patterns ARE standard and don't need documentation:
- `providesTags` / `invalidatesTags` on CRUD endpoints
- `transformResponse` for data reshaping
- `refetchOnMountOrArgChange` on queries

## Related
- [[redux-store-architecture]] — store-level cross-tab cart invalidation
- [[rtk-cart-tag-invalidation-auto-refetch]] — Cart tag invalidation chain
- [[checkout-state-persistence]] — saveCheckoutInfo sync with Redux
- [[cart-reprovision-after-reset]] — cartId lifecycle
