# Persisted checkout state has no owner

## Summary
Guest checkout data (passengers, contact, tripInfo) lives in the Redux `checkout` slice, saved by redux-persist to localStorage, with no user or cart key. Only some logout paths clear it.

## Context
Found reviewing `GUEST-PASSENGER-CARRYOVER` (#532): after login, passenger 1 showed the guest passenger typed earlier in the same browser.

## Details
- Store: `store/index.js:173` whitelists `checkout`, persist key `root-sep-7`, expiry 48h (`expiresAt`) only. The sessionStorage copy `checkout_formData` is keyed by `cartId`, 30 min TTL, fine.
- Login: `/logincart` merges cart ITEMS only. Passengers move via `migrateGuestData` (`useCheckoutBackendData.js:56-66`) only when `isGuestMode`; otherwise the persisted blob hydrates the form. Same-browser carryover is expected.
- Clears: only `ProfileButton.js:90` `clearStore()` (`persistor.purge()` + `RESET_APP_STATE`). Not cleared by `performFallbackLogout` (10 s timeout), `authUtils.handleAuthError`, session expiry, `/api/auth/force-logout`.
- BE `CartItemCheckoutInfoViewSet` is `IsAuthenticated` and user-scoped (reads filter `user=request.user`), so no cross-user leak there. `CartItemCheckoutInfo.cart_item` is OneToOne.

## Problem
Shared browser: user A passengers, email and phone can prefill for user B; with `isGuestMode` still true they are migrated into B's account via `/cart-checkout-info/save/`.

## Decision
Built and merged to FE `develop` `501f1503` (2026-10-22): `checkoutOwner` in the slice (absent in old blobs = null, guest data still migrates), `syncCheckoutOwner` reducer (claim if null, clear on mismatch), `useCheckoutOwnerGuard` gates the checkout page, `clearStore()` added to `performFallbackLogout`, guest migration gated on the owner being resolved. No `useEffect` chain in the reducer. Verified with a real two-account Chrome test. Guest to login transfer of cart and passengers is by design.

## Tradeoffs
Clearing on every auth change would break guest-to-login migration; owner null = guest keeps data.

## Related
[[checkout-state-persistence]], [[checkout-guest-migration-async-iife-pattern]], [[redux-persist-gate-scope-gap]], [[be-cartitem-lookup-ignores-cart-id-ticket]]
