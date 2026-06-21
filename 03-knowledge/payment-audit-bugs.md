# Payment Audit Bugs — 2026-06-11

## Summary
Full E2E audit (booking → checkout → payment, backend order → charge → webhook) uncovered 4 confirmed bugs: 2 MEDIUM (cart sync dead code), 2 LOW (stable_id cleanup ✅ resolved 2026-06-21, lazy query). Candidates C1/C2 since fixed (`cb817d9`).

## Context
Second audit pass with debug-mantra falsification on root causes. Every root cause verified surviving active disproof. Backend confirmed zero `stable_id` emission (legacy removed 2026-02-13). Full E2E audit report: `/01-projects/booking-payment-e2e-audit-2026-06-11.md` (includes scope, design confirmations, overturned findings).

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

### 3. ✅ RESOLVED — stable_id remnants (sweep completed)
**Status (verified 2026-06-21 against frontend):** `stable_id` removed from backend 2026-02-13 (migration `carts/0012`). Source sweep done — `stable_id` now comment-only in ~4 source files (e.g. `store/checkout-slice.js:20`); 2 test files still reference it. Cart item key is `item.id` (frontend CLAUDE.md). `useCartSync` Effect 6 (formerly the id→stable_id migration at lines 317-357) was rewritten to a formData-initialization effect (`hooks/checkout/useCartSync.js:317`) — the dead migration path no longer exists.
**Remainder:** 2 test files + incidental comments. No functional impact — no further action needed.

### 4. LOW — Dead lazy query hook in BookButton
**File:** `smartenplus-frontend/components/UI/BookButton.js:41-43`
**Problem:** `useLazyCheckCartIdQuery({ cartId, email }, { refetchOnMountOrArgChange: true })` — lazy queries take no args. Object-destructuring yields `data`/`checkCartLoading` = undefined. Harmless (trigger never fires) but dead. Line 44 is correct usage.
**Fix:** Delete lines 41-43.

## Candidates — Status

**C1: Checkout formData restore broken on hard refresh — FIXED**
`pages/checkout/index.js:187-201` + `107-124`. Root cause: PersistGate doesn't wrap `<Component>` → checkout mounts before Redux-persist rehydration. Mount: restore effect skips, clear effect guts formData, restore permanently blocked.
**Fixed:** `cb817d9` on develop. Added `isCartLoaded` gate (`!!data`) to prevent clear effect on mount.
**Source:** `[[checkout-formdata-persist-guard-pattern]]`

**C2: Transient errors incorrectly clear cartId — FIXED**
`components/HOC/check-and-createcart.js:67-72`. Root cause: catch on cart validation clears `cartId` for ANY failure (network blip, 429, 500). Only 404 means cart invalid.
**Fixed:** `cb817d9` on develop. Added `error?.status === 404` guard.
**Source:** `[[checkout-formdata-persist-guard-pattern]]`

## Related
- [[booking-payment-e2e-audit-2026-06-11]] — full audit report, design confirmations, overturned findings
- [[payment-integration]] — known open issues section links here
- [[payment-checkout-5-principles]]
- [[payment-gateway-charge-architecture]]
