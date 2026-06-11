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
2. Poll every 10s (backend-driven `polling_interval` field, default 10,000ms) while `expires_at` in future
3. Check BOTH `status === 'successful' || status === 'paid'` (domain vocab differs)
4. Success: redirect to order page (auth) or guest order page (guest)
5. Never redirect to `authorizeUri` for QR (empty for PP)
6. See [[promptpay-no-webhook-on-expiry]] for expiry handling (Celery sync + ExpirePendingChargeView + mgmt command)

## Canonical Charge Rule
LATEST charge per order only. Historical charges must NOT trigger finalization or display. User may retry with different method — old failed charges ≠ current state.

## Recoverable Failure
`payment_failed` NOT terminal. `finalize_payment_failed()` does NOT set `payment_finalized_at` — only success sets sentinel. Don't count as lost revenue until cancelled/expired.

## Double-Click Protection
Disable pay button + show "Processing..." state after click via `isProcessingPayment` flag. `setIsProcessingPayment(true)` prevents duplicate charges (UI-level guard; backend has 409 duplicate checks). `useOmisePayment.js`, `PaymentComponent.js`.

## Idempotency via Sentinel Fields
Timestamp sentinels as exactly-once guards. Reusable beyond payments — any high-risk side effect (email, booking confirm). See [[payment-sentinel-idempotency]].

## Amount Locking for Deferred Payments
`locked_amount` set on first QR, reset on expire/cancel. Prevents retries with different amounts: if new charge amount ≠ `locked_amount`, backend raises 409 `amount_locked` error. Same amount allowed (idempotent).  `payments/services.py:305` checks on webhook finalization.

## Webhook Audit Outside Transaction
Save audit/log records outside `transaction.atomic()` → survive rollbacks. Business logic fails (race, constraint) → raw event still available for debugging + manual reconciliation.

## Checkout Architecture — 5 Core Principles

Webhook SSOT, single active attempt, immutable snapshot, cart lock during pending, explicit cancel-recreate. State machine + implemented patterns extracted to atomic note.
→ See [[payment-checkout-5-principles]]

## QR Expiry — Parent/Child State

PP + MB expiry has NO Omise webhook. Expiry paths: backend Celery `sync_pending_charges`, `ExpirePendingChargeView` POST, management command `expire_stale_payments`. See [[promptpay-no-webhook-on-expiry]] for full details.

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

## Omise Documents API — Not Applicable

Omise Documents API (`/disputes/{id}/documents`) = dispute evidence upload only (PNG/JPG/PDF, max 10MB). Used for chargeback resolution, not payment receipts/invoices. No integration needed.

## Known Open Issues

**C1: Checkout formData restore broken on hard refresh** — mixed carts lose passenger assignments on `/checkout` reload before Redux-persist rehydration. Repro: 2-item mixed cart → fill passengers + customize → hard refresh → data gone. [[booking-payment-e2e-audit-2026-06-11]], candidate section. Fix: guard clear effect with `!isCheckoutRehydrated`.

**C2: Transient errors incorrectly clear cartId** — `check-and-createcart.js` catches ANY failure (network, 429, 500) and clears `cartId`. Only 404 means cart is actually invalid. Fix: `error.status === 404` guard. [[booking-payment-e2e-audit-2026-06-11]], candidate section.

## Related
- [[payment-audit-bugs-2026-06-11]] — confirmed bugs + audit methodology
- [[payment-checkout-5-principles]] — core architecture 5-point framework
- [[promptpay-no-webhook-on-expiry]] — expiry notifications (3 paths)
- [[nextauth-session-shape]] — guest vs auth email sourcing
- [[checkout-formdata-persist-guard-pattern]] — C1/C2 form restoration fixes
- [[omise-webhook-security]] — Event.retrieve() verification pattern
- [[payment-exception-catalog]] — exception→HTTP code mapping
- [[payment-finalize-deep-dive]] — finalize_payment() 6 non-obvious behaviors

**See also:** Full booking→checkout→payment audit in `/01-projects/booking-payment-e2e-audit-2026-06-11.md`