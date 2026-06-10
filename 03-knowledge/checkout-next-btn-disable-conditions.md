# Checkout Next Button Disable Conditions

**Context:** `components/forms/FormCard.js` — `shouldDisableNext` for Step 0 (Itinerary)

## Current Logic (post #90 fix)

```js
const shouldDisableNext = currentStep >= paymentStep ||
    (currentStep === 0 && (!isCurrentStepValid || isAdvanceBookingError || isAuthLoading)) ||
    isPaymentLocked;
```

## Condition Breakdown

| Condition | Source | Justification |
|---|---|---|
| Empty cart | `useStepValidation` `validationData.length === 0` | Nothing to proceed with |
| Zero passengers on any item | `useStepValidation` `hasZeroPassengers` | Incomplete selection |
| Null/orphaned contract | `useStepValidation` `hasMissingContracts` | Data corruption, backend rejects |
| `is_actived === false` | `useStepValidation` `hasInactiveItems` | Backend rejects inactive contracts |
| Over capacity | `useStepValidation` + `capacityValidationHelper` | Backend rejects |
| Advance hour passed | `FormCard` `hasPassedAdvanceHour` → `isAdvanceBookingError` | Shows warning; button disable = real-time feedback as deadline expires in open tab |
| Stop-sale date | `FormCard` `hasStopSaleDate` → `isAdvanceBookingError` | Same |
| Auth loading | `FormCard` `isAuthLoading = status === 'loading'` | Auth check in `handleNavbarNavigation:773` is skipped when `status==='loading'` — unauthenticated user falls through to step 1 |
| Payment locked | `FormCard` `isPaymentLocked` | Pending charge must be resolved first |

## History

- `92bf653` (2026-02-27) accidentally dropped `isAdvanceBookingError` from `shouldDisableNext` while adding inactive-contract check. Discovered 2026-06-10 via git bisect.
- `isAuthLoading` gap found by 2-agent strict/permissive debate in #90.

## Deferred Gaps (low priority)

- `isFetching` during background refetch — stale data window
- `is_actived !== true` (null/undefined passes strict `=== false` check)
- Null `traveling_date` silent pass
- QR active forward nav parity
