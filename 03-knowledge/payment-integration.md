# Payment Integration — Thai Payment Methods

## Summary
Thai payment via Omise. PromptPay, CC/debit, mobile banking, e-wallets. Canonical charge tracking + recoverable failure states.

## Thai Payment Methods

| Method | Type | Flow |
|--------|------|------|
| Credit Card | CC | Direct charge via Omise.js |
| Debit Card | DEBIT_CARD | Same as CC flow |
| PromptPay | PP | QR code + polling |
| Mobile Banking | INTERNET_BANKING | Redirect to bank |
| TrueMoney | EWALLET | Redirect |
| Rabbit LinePay | EWALLET | Redirect |

## Omise Source Types
`OMISE_SOURCE_TYPES` maps backend `payment_type` → Omise source types. Frontend stores raw `payment_type` — no normalization.

## QR Polling Pattern (PromptPay)
1. Create charge → get QR + `expires_at`
2. Poll while `expires_at` in future
3. Check BOTH `status === 'successful' || status === 'paid'` (domain vocab differs)
4. Success: redirect to order page (auth) or guest order page (guest)
5. Never redirect to `authorizeUri` for QR (empty for PP)

## Canonical Charge Rule
LATEST charge per order only. Historical charges must NOT trigger finalization or display. User may retry with different method — old failed charges ≠ current state.

## Recoverable Failure
`payment_failed` NOT terminal. `finalize_payment_failed()` does NOT set `payment_finalized_at` — only success sets sentinel. Don't count as lost revenue until cancelled/expired.

## Double-Click Protection
Disable pay button + "Processing..." for 10s after click. `setPaymentTriggerEffect(true)`, not toggle. Prevents duplicate charges.

## Idempotency via Sentinel Fields
Timestamp sentinels as exactly-once guards. Reusable beyond payments — any high-risk side effect (email, booking confirm). See [[payment-sentinel-idempotency]].

## Amount Locking for Deferred Payments
`locked_amount` set on first QR, reset on expire/cancel. Prevents duplicate amounts completing.

## Webhook Audit Outside Transaction
Save audit/log records outside `transaction.atomic()` → survive rollbacks. Business logic fails (race, constraint) → raw event still available for debugging + manual reconciliation.

## Checkout Architecture — 5 Core Principles

Webhook SSOT, single active attempt, immutable snapshot, cart lock during pending, explicit cancel-recreate. State machine + implemented patterns extracted to atomic note.
→ See [[payment-checkout-5-principles]]

## QR Expiry — Parent/Child State

PP + MB expiry has NO Omise webhook. See [[promptpay-no-webhook-on-expiry]] for all 3 expiry paths.

`qrExpired` lives in `QRPaymentForm` via `useQRPolling`. Parent never learns unless told via callback. Pattern: child components with terminal states must emit upward via `onExpired` prop. Parent clears `qrState` + `onQRPaymentStateChange(false)`.

## QR → Redirect Method Switch (C3b)

Backend `initiate_order_charge()` has `C3b`: proactively expires pending PP when redirect-method charge created. Frontend does NOT need to expire before switching. Only user "cancel" flows need explicit expire.

Switching PP → MB + PAY NOW just works — backend handles stale PP charge.

## Auth-Conditional Query Params

`expirePendingCharge()` must NOT send `?email=` when authenticated. Backend routes by param presence — auth uses Bearer token only. `?email=` on auth call → URL signature mismatch → guest routing.

**Rule:** Condition query param on `!token` (not `!!email`). Token presence = auth context.

## Dual Cancel Surface — Mutual Exclusion

Two UI elements canceling same charge (PAYMENT_PENDING alert + PendingChargeNotice) → must be mutually exclusive. Both firing: first 200, second 400.

**Guard:** Render `PendingChargeNotice` only when `paymentError?.type !== 'PAYMENT_PENDING'`.

## Centralized Payment Error Detection

4 components handle 409 `payment_pending` from cart mutations: `EditableCartItem.js` (PATCH), `InlinePassengerSelector.js` (inline), `BookButton.js` (add), `EnhancedTripCard.js` (DELETE).

**Extracted:** `helpers/handleCartMutationError.js` — `isPaymentPendingError(error)`. Checks `error?.status === 409 && error?.data?.error === 'payment_pending'`. Each component handles own UI.

**Latent bug:** `BookButton.js` bare `error?.status === 409` matched ALL 409 variants. Fixed by `isPaymentPendingError()`.

## Cross-Boundary Alert State Threading

Alert state in `index.js` not accessible to `PaymentComponent.js` (3 levels deep). Thread `setAlert` prop: `index.js → PaymentStep → PaymentComponent`. Call `setAlert?.({ show: false })` in cancel success handler.

**Rule:** Don't patch symptoms. Thread state to where action originates.

## sessionStorage Restore Timing

`useState` initializers run at module init — Redux-persist `cartId` is `null` (rehydration async). Restore logic checking `cartId` sees `null`, fails match, deletes valid data.

**Pattern:** Restore logic depending on Redux-persist state → `useEffect` gated on `isCheckoutRehydrated && cartId`, NOT `useState` initializer.

## Idempotency Key Scope

Scope to `cartId:total` snapshot. Regenerate when total changes. Without total-scoped regeneration: user applies coupon, same key, backend returns old order at old amount.

## Positional Language in Alerts

Never "above"/"below" — DOM position not guaranteed. Use element names: "Use the 'Cancel This Payment' button."

## Cart Reprovisioning After Reset

`resetCart()` nulls `cartId`. Order pages must fire `createCart()` immediately after. See [[cart-reprovision-after-reset]] for full pattern + email sources.

## NextAuth Session Shape

`session?.email` always undefined. See [[nextauth-session-shape]] for full shape + guest email sources.

## Related
- [[payment-system]]
- [[checkout-flow]]
- [[orders]]
- [[backend-architecture]]