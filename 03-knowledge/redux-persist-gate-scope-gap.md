# Redux PersistGate Scope Gap

## Summary

In smartenplus-frontend, `PersistGate` does NOT wrap `<Component>` (`pages/_app.js:90-97`) — every page mounts BEFORE redux-persist rehydration, so mount-time effects see initial Redux state (e.g., `cartId: null`), not persisted state.

## Context

`_app.js` gates only `RefreshTokenHandler` + `DevToolsProvider` inside `PersistGate`; the page tree renders immediately. This is intentional (no flash of blocked UI) but every page effect must assume pre-rehydration state on first run.

## Rules

1. **Guard restore effects with the rehydration flag:**
   ```js
   const isRehydrated = useSelector((s) => s._persist?.rehydrated ?? false);
   useEffect(() => {
     if (!isRehydrated || !cartId) return;
     // safe to read persisted state / sessionStorage keyed by it
   }, [isRehydrated, cartId]);
   ```
   Live pattern: `pages/checkout/index.js:51,108`.

2. **Clearing/reset effects are the dangerous ones.** An effect that "clears stale state" runs at mount against EMPTY data (API not loaded, Redux not rehydrated) and can initialize state that later blocks a `state !== undefined` restore guard — then a persistence effect saves the gutted object over the good copy. This exact chain is candidate C1 in [[booking-payment-e2e-audit-2026-06-11]]. Clearing effects must also wait for API data (`if (!data) return;`).

3. **First mount sequence to assume:** initial Redux state → effects run → (async) REHYDRATE action → effects re-run with persisted state. Any one-shot guard (`formData !== undefined`, refs) set in the first pass survives into the second.

## Related

[[booking-payment-e2e-audit-2026-06-11]] · [[checkout-flow]] · [[session-storage-restoration]]
