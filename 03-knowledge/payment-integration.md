# Payment Integration — Thai Payment Methods

## Summary
Thai payment methods via Omise. PromptPay, CC/debit, mobile banking, e-wallets. Canonical charge tracking + recoverable failure states.

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
Timestamp fields (`payment_finalized_at`, `payment_notification_sent_at`) as sentinel. `WHERE field IS NULL` before acting. Set inside atomic transaction. Already set → skip. Timestamp > boolean: audit visibility at zero cost. Reusable: any exactly-once side effect system.

## Amount Locking for Deferred Payments
QR/redirect methods have gap between charge creation + user completion. `locked_amount` field set on first QR creation, reset on expire/cancel. Without it: user generates QR for 1000 THB, then 500 THB, both could complete.

## Webhook Audit Outside Transaction
Save audit/log records outside `transaction.atomic()` → survive rollbacks. Business logic fails (race, constraint) → raw event still available for debugging + manual reconciliation.

## Checkout Architecture — 5 Core Principles

**1. Webhook = source of truth.** Frontend redirect MUST NOT finalize. Only webhook marks paid, creates booking items, finalizes settlement.

**2. One active payment attempt.** One order → one pending intent → one amount snapshot. Prevents duplicate charges, conflicting QR codes.

**3. Immutable payment snapshot.** Charge created → amount, items, discounts, method frozen. `CheckoutSnapshot` created after charge.

**4. Cart locked during `payment_pending`.** ALL cart mutations blocked (PATCH/DELETE, add, coupon). Backend `409 PAYMENT_PENDING`. Frontend amber warning.

**5. Explicit cancel-and-recreate.** Expire charge → unlock → user selects new method → new intent. Never mutate active payment.

**State machine:**
```
editable → payment_pending → paid
editable → payment_pending → expired/cancelled → editable
```

**Implemented patterns (frontend):**
- `getBillingAndOrder.js`: 409 maps `payment_pending` → `PAYMENT_PENDING`, `amount_locked` → `AMOUNT_LOCKED`
- `usePaymentInitialization.js`: idempotency key `cartId:total`
- `PaymentComponent.js`: `handleCancelPendingPayment()` → expire + refetch
- `expirePendingCharge()` + `getReconcileOrder()` in `getBillingAndOrder.js`
- Cross-tab sync: `cart_version` storage key + listener in `store/index.js`
- formData sessionStorage: persists form state, validates freshness (30min) + cartId match

28-use-case ref: `docs/features/payment/PAYMENT_CHECKOUT_ARCHITECTURE_REVIEW.md`

## QR Expiry — Parent/Child State

**Omise webhook gap:** `charge.complete` for success only. `charge.expire` = Barcode Alipay only. PP + MB expiry has NO webhook — relies on Celery `sync_pending_charges` (every 10 min). E-wallets reconciled after 30 min stale threshold.

**Three expiry paths (all send notification):**
1. `sync_pending_charges` (Celery 10 min) — PP expired + `finalize_payment_failed`; MB + e-wallets reconciled
2. `ExpirePendingChargeView` (user cancel) — `_send_payment_failed_notifications` → reset to `ordering`
3. `expire_stale_payments` mgmt command — same pattern

`qrExpired` lives in `QRPaymentForm` via `useQRPolling`. Parent never learns about expiry unless told via callback — `qrState.authorizeUri` stays set, navigation guards armed.

**Pattern:** Child components with terminal states must emit upward via callbacks. Parent clears its own state in response.

Implementation: `onExpired` prop. `qrExpired=true && !isRetrying` → calls `onExpired?.()`. Parent clears `qrState` + `onQRPaymentStateChange(false)`.

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

`resetCart()` sets `state.cart.cartId = null` — correct. `withCartValidation` HOC only mechanism creating new cart. Trip detail + search pages NOT wrapped → BookButton reads `null`, fails.

**Fix:** Order detail pages call `createCart()` after `resetCart()` — fire-and-forget:
```js
dispatch(cartActions.resetCart({ items: [], total: 0 }));
createCart({ email }).unwrap()
  .then(res => { if (res?.id) dispatch(cartActions.setCartId(res.id)); })
  .catch(() => {}); // HOC recovers on next booking page
```

**Auth email:** `session?.user?.email` (NOT `session?.email`)
**Guest email:** `router.query.email ? decodeURIComponent(router.query.email) : null`
**Files:** `pages/orders/[orderid].js`, `pages/guest-order/[orderId].js`

## NextAuth Session Shape

`{ id, accessToken, user: { email, name, image } }`. Custom fields at root (`id`, `accessToken`, `phoneNumber`). Email ONLY at `session.user.email` — `session?.email` always `undefined`.

**Auth check:** `session?.id`. **Email:** `session?.user?.email`.
**Guest email:** `formData?.email` (checkout) or `router.query.email` (order pages).

## Related
- [[payment-system]]
- [[checkout-flow]]
- [[orders]]
- [[backend-architecture]]
