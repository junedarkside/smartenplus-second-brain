# Guest "Clear My Data" must clear every guest data holder

## Summary
The checkout banner's "Clear My Data" only reset the Redux checkout slice. Form values also live in `formData` state and sessionStorage, so the data came back, and the guest was bounced to login. Fixed in FE `6e63398f` (merged develop `aab555a7`, pushed).

## Context
Banner text: "Guest checkout active. Your data is saved locally for 48 hours." (`GuestModeBanner.js`, handler `handleClearGuestData` in `pages/checkout/index.js`). Guest data has more than one home, see [[checkout-state-persistence]] and [[redux-persist-checkout-no-owner]].

## Problem
1. Handler dispatched `clearCheckoutData()` + `setIsGuestMode(false)` only. `formData` (React state in `useCheckoutFormData`) and `sessionStorage['checkout_formData']` (30 min TTL) stayed. `buildInitialValues` merges `formData` into Formik and `useCheckoutAutoSave` wrote it back to Redux, so values reappeared; refresh restored them too.
2. `isGuestMode=false` while unauthenticated on step 1+ made `ProtectedComponent allowGuest={false}` call `router.push('/account/login')`. Guest thrown out, step lost.
3. Success alert was hardcoded English.

## Details
Guest data holders (clear all together):

| Holder | Cleared by |
|---|---|
| Redux `checkout` slice (persisted, key `root-sep-7`, 48h) | `clearCheckoutData()` |
| `formData` React state | `clearFormData()` (new, `useCheckoutFormData.js`) |
| `sessionStorage['checkout_formData']` | `clearFormData()` |
| Formik values | step 0 reset unmounts Passengers step; re-init from cleared sources |

Handler now, in one synchronous batch: `clearCheckoutData`, `setIsGuestMode(false)`, `cart.clearFormData()`, `ui.setCompletedSteps([0])` (initial value is `[0]`, not `[]`), `ui.setFormStep(0)`, translated alert `checkout.guestBanner.cleared` (en + th). Next click hits `blockedByAuthGate` and shows the guest/login choice. Cart items stay: a cart is not personal data.

Autosave race is already safe: `formData` change re-runs the autosave effect, cleanup clears the 1s debounce timer, new run exits on falsy values.

## Decision
Return to step 0 instead of staying a guest on an empty form. Reason: `isGuestMode` must flip false (reducer does it anyway) and guest-only steps cannot render without it.

## Tradeoffs
- QR payment open: `setFormStep(0)` skips the QR leave-guard dialog. Rare for a guest, left.
- Autosave `previousValuesRef` is not reset: retyping identical values may skip the Redux save (`formData` still holds them). Minor.
- `paymentSuccess` handler removes the storage key but leaves `formData` state. Separate, not fixed.
- Banner says 48h, sessionStorage copy is 30 min. Left.

## Verified
Jest: characterization (new test for storage wipe + step 0), `useCheckoutFormData`, i18n parity pass; build ok; same 37 pre-existing failing suites as develop. Chrome guest flow: after clear Redux empty, sessionStorage key gone, step 1, no login redirect, still empty after wait + refresh, Next opens guest/login dialog.

## Lesson
`npm run build` overwrites `.next` and breaks a running `next dev` (every page 500, "Cannot find module ./chunks/vendor-chunks/@mui.js"). Stop dev first or restart it after: `rm -rf .next && npm run dev`.

## Related
[[checkout-state-persistence]], [[redux-persist-checkout-no-owner]], [[checkout-guest-migration-async-iife-pattern]], [[checkout-formdata-persist-guard-pattern]]
