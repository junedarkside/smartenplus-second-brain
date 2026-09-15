# Checkout Guest Migration — Async IIFE Sequencing Pattern

## Summary
When migrating guest checkout data to backend on login, use a single async IIFE to sequence flush→POST→refetch→dispatch→clear. Prevents intermittent form data loss caused by async timing races.

## Problem
Guest user fills InfoFields → logs in → form blanks intermittently. Three races:
1. `clearGuestDataAfterMigration` wipes Redux before backend refetch repopulates it
2. RTK Query `refetchOnMountOrArgChange:false` — won't refetch again unless forced
3. 1-second debounce may not have fired before login click — Redux has stale values

## Decision
Single async IIFE inside the migration `useEffect`. No new effects, no new refs, no coordination flags. Respects Rule 8 (no useEffect chains).

## Pattern

```js
// Inside migration useEffect — async IIFE, not a chain
(async () => {
  flushSave();                                    // sync Redux flush (guest path only)
  const success = await migrateGuestDataToBackend(cartId, checkoutDataFromRedux);
  if (!success) return;
  hasLoadedBackendDataRef.current = false;        // allow backend-merge to re-run
  const result = await refetchBackendData();      // inline await — RTK Query fulfilled action
  if (result?.data) {
    const converted = convertBackendDataToRedux(result.data);
    if (converted) {
      // dispatch merge inline — no second effect
      Object.entries(converted.tripInfo || {}).forEach(([id, td]) =>
        dispatch(saveTripInfo({ itemId: id, tripData: td }))
      );
      if (converted.passengers?.length) dispatch(savePassengers(converted.passengers));
      if (converted.contact?.email || converted.contact?.phone) dispatch(saveContact(converted.contact));
      if (Object.keys(converted.passengerAssignments || {}).length)
        dispatch(savePassengerAssignments(converted.passengerAssignments));
      hasLoadedBackendDataRef.current = true;
    }
  }
  clearGuestDataAfterMigration(dispatch, clearCheckoutData, setIsGuestMode);
})();
```

## Key Constraints
- `flushSave()` is synchronous for guest users (Redux-only dispatch, no backend call)
- `refetchBackendData` returns RTK Query fulfilled action — `result.data` has the payload
- Clear Redux ONLY AFTER dispatch merge — `Passengers.js` has `enableReinitialize={true}`, any Redux clear = form reset
- `flushSave` must guard `isAuthenticated === false` internally to prevent backend save on guest path

## Files
- `helpers/checkoutPersistence.js` — `flushSave` exposed from `useCheckoutAutoSave`
- `helpers/checkoutBackendLoad.js` — `refetchBackendData` exposed from `useBackendCheckoutData`
- `pages/checkout/index.js:511-550` — migration effect with async IIFE

## Related
- [[checkout-guest-mode-flow]]
- [[infofields-data-flow]]
