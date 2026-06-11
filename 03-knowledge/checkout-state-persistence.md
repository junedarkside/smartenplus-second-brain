# Checkout State & Persistence

## Summary
Checkout uses dual persistence (guest vs logged-in), 6-effect useCartSync with strict ordering, ghost trip detection, guest→backend migration on login, and 1-second debounced auto-save with stable comparison.

## Context
`hooks/checkout/useCartSync.js`, `helpers/checkoutPersistence.js`, `pages/checkout/index.js`. Most complex stateful area in the frontend. Multiple systems interact.

## Dual Persistence Strategy

| User type | Primary storage | Secondary | TTL |
|---|---|---|---|
| Guest | sessionStorage (per-tab) | Redux Persist (localStorage) | 30 min (session) / 48hr (Redux) |
| Logged-in | Backend API | Redux (navigation cache) | Backend-controlled |

**Logged-in critical detail:** backend-first write. No localStorage fallback. Failed backend save = data loss on next page load. Intentional (comment: "avoid infinite loop") — no retry logic.

**Restore sequence:** sessionStorage restores AFTER Redux rehydration (useEffect dependency on `isCheckoutRehydrated`). Never in useState initializer — would see stale cartId. See [[redux-persist-gate-scope-gap]].

## useCartSync 6-Effect Ordering (useCartSync.js:19-335)
```
Effect 1: Initialize passenger assignments from cart items (run once)
Effect 2: Validate assignments vs cart requirements (skip if migration pending)
Effect 3: Detect deleted cart items → prune assignments
Effect 4: Detect new cart items → generate default assignments
Effect 5: UUID migration (stableId removed, defaults to already-done)
Effect 6: Sync Redux assignments → formData on init only
```
**Critical:** Effect 5 sets `stableIdMigrationRanRef = true`. Effect 2 checks this ref before running (line 184-186). **Reordering effects breaks validation.**

5 refs guard loop prevention:
- `migrationRanRef` — prevents Effect 1 re-init
- `stableIdMigrationRanRef` — defaults `true` (migration 0012 complete, all users migrated)
- `hasInitializedAssignments` — one-shot init guard
- `lastValidatedAssignmentsRef` — `JSON.stringify` comparison prevents Effect 2 re-run
- `previousCartItemsRef` — detects item addition/deletion

**Warning:** `lastValidatedAssignmentsRef` uses string comparison. New field added to passenger object = string changes = Effect 2 re-runs unexpectedly.

## Ghost Trip Detection
Two independent paths detect cart item deleted but form still has trip data:

**Path 1: FormikValuesSync Effect 2** (`components/forms/checkout/FormikValuesSync.js:66-93`)
- Compares Formik trip keys vs current cart item IDs
- Clears stale trip data from Formik state

**Path 2: useCartSync lines 147-156**
- Detects assignments for cart item IDs that no longer exist
- Clears orphaned assignments from Redux

Both must clear independently. FormikValuesSync clears Formik; useCartSync clears Redux. Not interchangeable.

## Guest → Backend Migration on Login (pages/checkout/index.js:481-503)
```js
if (isGuestMode && session?.id) {
  const hasData = tripInfo || passengers?.length || contactInfo
  if (hasData) migrateGuestDataToBackend(guestData)
}
```
Runs once when `isGuestMode` flips to `false` (login during checkout). Only migrates if "meaningful data" present. After migration: guest Redux state cleared, backend becomes source of truth.

## Debounced Auto-Save with Stable Comparison (checkoutPersistence.js:99-325)
```js
// 1-second debounce on every form change
const debouncedSave = useDebouncedCallback(saveCheckoutData, 1000)

// Exclude unstable values from change detection:
function normalizeFormValuesForComparison(values) {
  // Date objects → ISO strings (avoids reference inequality)
  // UUID fields excluded (crypto.randomUUID on every render)
  return JSON.stringify(normalized)
}
```
Without UUID exclusion: new UUID each render → comparison always fails → debounce fires every second → 429s.

## hasLoadedBackendDataRef Behavior (checkoutBackendLoad.js:24-39)
Resets on every component mount, not only on cartId change. Ensures fresh backend data fetch on page refresh even if cartId is unchanged. Previous behavior (cartId-gated) caused stale checkout data on hard refresh.

## Related
- [[redux-persist-gate-scope-gap]] — rehydration timing hazards
- [[checkout-hoc-architecture]] — HOC that validates cart before checkout mounts
- [[checkout-formdata-persist-guard-pattern]] — C1/C2 formData restore guards
- [[checkout-formdata-time-fields]] — time field casing boundary in persistence
- [[rtk-query-advanced-patterns]] — saveCheckoutInfo missing invalidatesTags
- [[nextauth-session-shape]] — session?.user?.email for logged-in users
