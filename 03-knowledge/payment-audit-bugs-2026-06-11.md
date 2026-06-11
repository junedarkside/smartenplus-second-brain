# Payment Audit Bugs — 2026-06-11

## Summary
Full E2E audit (booking → checkout → payment, backend order → charge → webhook) uncovered 4 confirmed bugs: 2 MEDIUM (cart sync dead code), 2 LOW (stable_id cleanup, lazy query). All fixes straightforward. 2 open candidates pending runtime repro.

## Context
Second audit pass with debug-mantra falsification on root causes. Every root cause verified surviving active disproof. Backend confirmed zero `stable_id` emission (legacy removed 2026-02-13). See [[booking-payment-e2e-audit-2026-06-11]] for full scope, design confirmations, and overturned findings.

## Confirmed Bugs

### 1. MEDIUM — Dead change detection in cart sync
**File:** `smartenplus-frontend/hooks/checkout/useCartSync.js:41-42`
**Problem:** Compares `item.stable_id` only, but backend dropped `stable_id` column (migration `carts/0012_remove_cartitem_stable_id`, 2026-02-13). All entries map to `[null, null, …]` → same-length cart changes (delete A + add B) treated as "no change" → passenger-assignment sync skipped silently.
**Consequence:** Stale passenger assignments in formData when user replaces cart items without changing count.
**Fix:** Replace both set comparisons at lines 149 and 151 with `item.id` instead of `stable_id`.
**Second-pass verification:** Effect 2 cannot rescue — assignments unchanged when map equals, so early return at line 203 blocks sync entirely.

### 2. MEDIUM — Dead removed-item cleanup
**File:** `smartenplus-frontend/hooks/checkout/useCartSync.js:147-177`
**Problem:** Builds `previousStableIds`/`currentStableIds` from `String(i.stable_id)` → all entries `"undefined"` → `removedItemIds` always empty → `clearTripInfo` never dispatched → stale trips never pruned from formData when item deleted. Effect 3 only covers cart→empty.
**Consequence:** Orphaned trip data in formData after partial cart deletions.
**Fix:** Key both sets by `item.id` instead of `stable_id`.
**Second-pass verification:** Line 155 is SOLE `clearTripInfo` dispatch site in source (grep ex-tests confirms). No alternate pruning path exists.

### 3. LOW — stable_id remnants (tech debt)
**Files affected:** 9 source, 3 test files still reference `stable_id`. Fallback `String(item.stable_id || item.id)` works but is dead code. Effect 6 (id→stable_id migration, lines 317-357) can never migrate.
**Fix:** Sweep all 12 files to `item.id` only. Delete Effect 6.
**Files:**
- Source: `PassengerAssignment.js`, `Passengers.js`, `Confirmation.js`, `useCartSync.js`, `useStepValidation.js`, `pages/checkout/index.js`, `checkoutPersistence.js`, `savePassengerAssignmentsToCart.js`, `checkout-slice.js`
- Tests: `__tests__/hooks/useCheckoutAutoSave.test.js`, `__tests__/helpers/savePassengerAssignmentsToCart.test.js`, `__tests__/helpers/checkoutPersistence.test.js`

### 4. LOW — Dead lazy query hook in BookButton
**File:** `smartenplus-frontend/components/UI/BookButton.js:41-43`
**Problem:** `useLazyCheckCartIdQuery({ cartId, email }, { refetchOnMountOrArgChange: true })` — lazy queries take no args. Object-destructuring yields `data`/`checkCartLoading` = undefined. Harmless (trigger never fires) but dead. Line 44 is correct usage.
**Fix:** Delete lines 41-43.

## Open Candidates — Require Runtime Repro

**C1: Checkout formData restore broken on hard refresh**
`pages/checkout/index.js:187-201` + `107-124`. PersistGate wraps only RefreshTokenHandler, NOT `<Component>` → checkout mounts before Redux-persist rehydration. Mount: restore effect skips (isCheckoutRehydrated=false, cartId=null); clear effect runs on mixed cart (hasMixedPassengerTypes([])=false) → sets formData={{passengerAssignments:{}}} → restore permanently blocked by `formData !== undefined` guard → after rehydration the inline saver overwrites with gutted object.
**Repro:** mixed cart (2 items, different passenger counts) → fill passengers + customize assignments → hard refresh `/checkout` → form data / assignments gone.
**Fix if confirmed:** Skip clear effect until cart loaded (`if (!data) return;`); consider guarding with `isCheckoutRehydrated`.

**C2: Transient errors incorrectly clear cartId**
`components/HOC/check-and-createcart.js:67-72`. Catch on cart validation clears `cartId` for ANY failure (network blip, 429, 500). Only 404 means cart invalid.
**Fix:** Clear only on `error.status === 404`.

## Related
- [[booking-payment-e2e-audit-2026-06-11]] — full audit report, design confirmations, overturned findings
- [[payment-integration]] — known open issues section links here
- [[payment-checkout-5-principles]]
- [[payment-gateway-charge-architecture]]
