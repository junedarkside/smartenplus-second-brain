# Booking → Checkout → Payment E2E Audit (2026-06-11)

## Summary

Full-flow audit (frontend booking/cart + checkout + payment, backend order/payment). 3 Explore agents + hand-verification of every candidate (debug-mantra recheck on the big one). Result: **4 confirmed bugs (1 LOW new), 2 candidates pending repro, 2 hardening recommendations, payment layer verified clean, 3 explorer claims overturned.**

**Second-pass falsification audit (2026-06-11, debug-mantra):** every root cause survived active disproof. Key double-confirmation: backend emits zero `stable_id` anywhere (`grep` over backend `*.py` ex-migrations — only a legacy log string at `bookings/services.py:223`), so bugs 1/2 cannot be masked by a computed serializer field. Refinements recorded inline below.

## Scope

- Frontend: BookButton → cart (RTK Query) → `/checkout` → order creation → Omise payment → order pages.
- Backend: carts → `/order-billing/` → Order state machine → GatewayCharge → webhook/polling/reconcile → expiry.
- Method: explorer findings treated as candidates only; each verified by direct read before classification (lesson from [[people-also-book-checkout-audit]]: most explorer findings overturn).

## Confirmed Bugs

### 1. MEDIUM — dead change-detection in cart sync
`smartenplus-frontend/hooks/checkout/useCartSync.js:41-42` compares `i.stable_id` only, but backend dropped the column (migration `carts/0012_remove_cartitem_stable_id`, 2026-02-13). Maps are always `[null, null, …]`, so a same-length cart change (delete item A + add item B) is treated as "no change" and passenger-assignment sync is skipped.
**Fix:** compare by `item.id`.
**Falsification notes (2nd pass):** Effect 2 cannot rescue — assignments object unchanged when cart swaps same-length, so `JSON.stringify` equals `lastValidatedAssignmentsRef.current` and Effect 2 early-returns (`useCartSync.js:201-203`); sync fully skipped. Precondition: manifests only when ONE refetch delivers a same-length changed `cart_item` array (item replacement or batched delete+add); sequential ops with separate refetches escape via length difference. Side effect: early return also skips the `previousCartItemsRef` update (line 144 unreached), so the next comparison runs against a stale baseline.

### 2. MEDIUM — dead removed-item cleanup
`useCartSync.js:147-177` builds `previousStableIds`/`currentStableIds` from `String(i.stable_id)` → every entry is `"undefined"` → `removedItemIds` always empty → `clearTripInfo` never dispatched and stale trips never pruned from formData when an item is deleted. Effect 3 only covers cart→empty, not partial removal.
**Fix:** key both sets by `item.id`.
**Falsification note (2nd pass):** `useCartSync.js:155` is the SOLE `clearTripInfo` dispatch site in source (grep ex-`.next`, ex-tests) — no alternate pruning path exists; dead path means stale trips are never pruned anywhere.

### 3. LOW — stable_id remnants (tech debt)
9 source files still reference `stable_id`; the `String(item.stable_id || item.id)` fallback works but is dead code, and useCartSync Effect 6 (id→stable_id migration, lines 317-357) can never migrate anything. Files: `PassengerAssignment.js`, `Passengers.js`, `Confirmation.js`, `useCartSync.js`, `useStepValidation.js`, `pages/checkout/index.js`, `checkoutPersistence.js`, `savePassengerAssignmentsToCart.js`, `checkout-slice.js`. Plus 3 test files needing same sweep (verified 2026-06-11 audit-of-audit): `__tests__/hooks/useCheckoutAutoSave.test.js`, `__tests__/helpers/savePassengerAssignmentsToCart.test.js`, `__tests__/helpers/checkoutPersistence.test.js`.
**Fix:** sweep to `item.id`; delete Effect 6.

### 4. LOW — misused lazy query hook in BookButton
`components/UI/BookButton.js:41-43`: `useLazyCheckCartIdQuery({ cartId, email }, { refetchOnMountOrArgChange: true })` — lazy queries take no args and return a `[trigger, result]` tuple; object-destructuring yields `data`/`checkCartLoading` = undefined. Harmless (trigger never fires, no request) but dead. Line 44 is the correct usage.
**Fix:** delete lines 41-43.

## Candidates — require repro before promotion (user ruling)

### C1. MEDIUM — checkout formData restore suspected broken on hard refresh
`pages/checkout/index.js:187-201` vs `107-124`. Key fact: `_app.js:90-97` — **PersistGate wraps only RefreshTokenHandler/DevTools, NOT `<Component>`** → checkout mounts before Redux-persist rehydration. Mount sequence: restore effect skips (`isCheckoutRehydrated=false`, `cartId=null`); mixed-counts clear effect runs anyway (`hasMixedPassengerTypes([])=false`, `passengerTypeHelper.js:34`) → `setFormData(prev => ({...prev, passengerAssignments:{}}))` turns `undefined` into `{passengerAssignments:{}}` → restore effect permanently blocked by `formData !== undefined` guard (line 108) → after rehydration the inline saver (lines 127-135) overwrites `checkout_formData` with the gutted object. Redux checkout-slice restore may mask part of the loss — needs runtime confirmation.
**Repro:** mixed cart (2 items, different passenger counts) → fill passengers + customize assignments → hard refresh `/checkout` → form data / assignments gone = confirmed.
**Fix if confirmed:** skip clear effect until cart data loaded (`if (!data) return;` before line 188); consider also guarding with `isCheckoutRehydrated`.
**Falsification note (2nd pass):** mount-state assumptions confirmed — `cart-slice.js:7` initial `cartId: null`; `isCheckoutRehydrated = state._persist?.rehydrated ?? false` (`checkout/index.js:51`). Both falsy at mount → restore skips, clear effect guts formData. Mechanism intact; runtime repro remains the gate.

### C2. MEDIUM — transient error nukes cartId
`components/HOC/check-and-createcart.js:67-72`: catch on cart validation clears `cartId` for ANY failure (network blip, 429 — CartThrottle exists, 500). Only 404 means the cart is actually invalid. Code-trace confirmed; runtime repro pending.
**Fix:** clear only when `error.status === 404`.

## Design Confirmations (not bugs — prevents future re-flagging)

### Order lookup by order_id + email is intended product design
`smartenplus-backend/orders/views.py:617` filters guest lookups by `email` without `user__isnull=True` (strict version deliberately commented out at 616). **User ruling 2026-06-11: intentional possession-based lookup (PNR+lastname pattern), NOT an IDOR. No authorization change.** Hardening recommended:
- Rate limiting: `OrderDetailsViewSet` is `AllowAny` with no `throttle_classes` (`views.py:571-573`); pattern available at `CouponThrottle` (line 1168).
- `secrets.choice()` instead of `random.choice()` for future order IDs (`orders/utils.py:34-47`; current entropy ~37 bits is adequate, RNG is not crypto-grade).
- Minor note, no change recommended: `reconcile` (line 677) filters `user__isnull=True` while the main lookup doesn't — a registered user's order opened via guest link can be viewed but not manually reconciled.

### Other intentional patterns
- `WebhookEvent` created outside `transaction.atomic` (`payments/views.py:204`) — audit trail survives rollback, by design.
- CheckoutSnapshot validation log-only (`payments/services.py:317`) — intentionally non-blocking.
- sessionStorage `checkout_formData` cleared only on `paymentSuccess` (`checkout/index.js:138-144`) — not on logout; stale guest data can surface across accounts (design note, low risk).
- Guest redirect builds `?email=${formData?.email || ''}` (`PaymentComponent.js:330`) — empty email yields broken guest-order link if formData stale (minor).

## Verified Clean

Frontend payment layer complies with every CLAUDE.md gotcha: no `resetCart` in `useOmisePayment`; both order pages reset + reprovision cart (`createCart({email})` + `setCartId`); polling checks `'successful' || 'paid'`; backend `expires_at` everywhere (no hardcoded timing); `cancelState.success` guards on all three surfaces; `?email=` guest-only in `expirePendingCharge`; 409 mappings complete; `isPaymentLocked` manual-clear only; session structure correct throughout.

Backend: canonical charge = latest `GatewayCharge` (`orders/views.py:640`, `691`); expire-charge auth correct (`payments/views.py:370-377` — email path only for unauthenticated); state machine recoverable paths correct (`payment_failed → ordering → paid`); cross-cart pending lock via `select_for_update` (`services.py:645-664`); QR→redirect proactive expiry correct (`services.py:580-616`); webhook idempotent via `last_webhook_event_id` + row lock.

## Overturned Findings (explorer + own claims — record per audit discipline)

1. "useCartSync migration refs never set, Effect 2 never runs" — FALSE: set at lines 295/311 (Effect 5) and 331/349/355 (Effect 6).
2. "BookButton loading state stuck after invalid-cartId early return" — FALSE: `isLoading` comes from `useCreateCartItemMutation` (line 45); early return precedes `addItem`, mutation never starts.
3. Own candidate "withCartValidation isMounted misuse permanently disables cart creation" — DEMOTED to code smell: early returns (`check-and-createcart.js:105-112`) register no cleanup, so the first status transition has no cleanup to fire; `dataFetchedRef` blocks later calls regardless. Unreachable as a bug.
4. Own first hypothesis for C1 ("PersistGate guarantees rehydration before mount") — FALSE: PersistGate does not wrap `<Component>` (`_app.js:90-97`). Debug-mantra falsification flipped this twice; final state is the C1 description above.

## Related

[[payment-checkout-architecture-audit]] · [[multitab-payment-race-condition-fixes]] · [[checkout-flow]] · [[payment-integration]] · [[people-also-book-checkout-audit]] · [[cart-reprovision-after-reset]] · [[payment-gateway-charge-architecture]] · [[payment-status-enums]]
