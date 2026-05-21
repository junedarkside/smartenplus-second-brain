# Payment Integration — Thai Payment Methods

## Summary
Patterns for integrating Thai payment methods via Omise. Covers PromptPay, credit/debit cards, mobile banking, e-wallets. Key lesson: payment systems need canonical charge tracking and recoverable failure states.

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
`OMISE_SOURCE_TYPES` maps backend `payment_type` to Omise source types. Frontend stores raw `payment_type` from backend — no normalization.

## QR Polling Pattern (PromptPay)
1. Create charge → get QR code + `expires_at`
2. Poll status while `expires_at` in future
3. Check BOTH `status === 'successful' || status === 'paid'` (domain status vocab differs)
4. On success: redirect to order page (auth) or guest order page (guest)
5. Never redirect to `authorizeUri` for QR (empty for PromptPay)

## Canonical Charge Rule
Always use LATEST charge per order. Historical charges must NOT trigger finalization or display. Rationale: user may retry with different method — old failed charges are not the current state.

## Recoverable Failure
`payment_failed` is NOT terminal. User can retry. `finalize_payment_failed()` does NOT set `payment_finalized_at` — only success sets that sentinel. Analytics should not count as lost revenue until order cancelled/expired.

## Double-Click Protection
Disable pay button + show "Processing..." for 10s after click. Use `setPaymentTriggerEffect(true)`, not toggle. Prevents duplicate charge creation.

## Idempotency via Sentinel Fields
Use timestamp field (`payment_finalized_at`, `payment_notification_sent_at`) as sentinel. Check `WHERE field IS NULL` before acting. Set inside same atomic transaction. If already set, skip. Why timestamp over boolean: audit visibility (when did this happen?) at zero extra cost. Reusable: any system needing exactly-once side effects in concurrent environment.

## Amount Locking for Deferred Payments
QR/redirect payment methods have gap between charge creation and user completion. During this window, prevent amount-changing operations (retry with different amount, cart modification). Implementation: `locked_amount` field set on first QR creation, reset on expire/cancel. Enforcement at charge creation time. Without it, user could generate QR for 1000 THB, then another for 500 THB, and both could complete.

## Webhook Audit Outside Transaction
Save audit/log records outside `transaction.atomic()` so they survive rollbacks. If business logic transaction fails (race condition, constraint violation), raw event still available for debugging and manual reconciliation.

## Checkout Architecture Review

Five core principles governing the MVP payment lifecycle. All implemented as of 2026-05-16.

**1. Webhook is source of truth.** Frontend redirect MUST NOT finalize payment — only webhook may mark order paid, create booking items, finalize settlement. Frontend can be closed, refreshed, or manipulated; webhook is authoritative.

**2. One active payment attempt at a time.** One order → one pending payment intent → one active amount snapshot. Prevents duplicate charges, conflicting QR codes, reconciliation confusion.

**3. Immutable payment snapshot.** Once charge created: amount, items, discounts, payment method all frozen. Payment amount must always match order items and gateway charge amount. Backend creates `CheckoutSnapshot` after charge creation.

**4. Cart locked during `payment_pending`.** ALL cart mutations blocked (PATCH/DELETE items, add item, coupon changes). Backend returns `409 PAYMENT_PENDING`. Enforced in backend, not frontend only. Frontend shows amber warning: "Payment in progress. Cancel payment to edit cart."

**5. Explicit cancel-and-recreate to change payment method.** Expire charge → unlock checkout → user selects new method → create new intent. Never mutate active payment intent.

**State machine:**
```
editable → payment_pending → paid
editable → payment_pending → expired/cancelled → editable
```

**Implemented patterns (frontend):**
- `getBillingAndOrder.js`: 409 maps `payment_pending` → `PAYMENT_PENDING`, `amount_locked` → `AMOUNT_LOCKED`
- `usePaymentInitialization.js`: idempotency key scoped to `cartId:total` snapshot
- `PaymentComponent.js`: `handleCancelPendingPayment()` → expire + refetch flow
- `expirePendingCharge()` + `getReconcileOrder()` in `getBillingAndOrder.js`
- Cross-tab sync: `cart_version` storage key + listener in `store/index.js`
- formData sessionStorage: persists form state, validates freshness (30min) + cartId match

Full 28-use-case reference: `docs/features/payment/PAYMENT_CHECKOUT_ARCHITECTURE_REVIEW.md` in smartenplus-frontend.

## QR Expiry — Parent/Child State Propagation

**Omise webhook gap (2026-05-18):** Omise sends `charge.complete` for successful charges only. `charge.expire` fires for Barcode Alipay only. PromptPay and mobile banking expiry has NO webhook — relies entirely on Celery `sync_pending_charges` task (every 10 min). E-wallets/international methods (not in `METHOD_EXPIRY`) reconciled after 30 min stale threshold.

**Three expiry paths, all send notification:**
1. `sync_pending_charges` (Celery every 10 min) — PP marked expired + `finalize_payment_failed`; MB + e-wallets reconciled via Omise
2. `ExpirePendingChargeView` (user manual cancel) — calls `_send_payment_failed_notifications` before resetting order to `ordering`
3. `expire_stale_payments` management command — same notification pattern as view

**Lesson:** When integrating a payment gateway, verify which events trigger webhooks for each payment method. Omise docs confirm `charge.complete` = successful completion, `charge.expire` = Barcode Alipay only. Never assume all terminal states produce webhooks.

`qrExpired` state lives inside `QRPaymentForm` via `useQRPolling`. Parent (`PaymentComponent`) never learns about expiry unless told via callback — parent's `qrState.authorizeUri` stays set, keeping navigation guards armed.

**Pattern:** Child components with terminal states (expired, failed, paid) must emit upward via callbacks. Parent clears its own state in response.

Implementation: `onExpired` prop on `QRPaymentForm`. When `qrExpired=true && !isRetrying`, calls `onExpired?.()`. Parent clears `qrState` + calls `onQRPaymentStateChange(false)` → navigation guards deactivate, PAY NOW button restores.

## QR → Redirect Method Switch (C3b)

Backend `initiate_order_charge()` (`payments/services.py`) has `C3b` logic: proactively expires pending PromptPay charge when a redirect-method (mobile banking, e-wallet) charge is created. Frontend does NOT need to expire before switching payment method. Only user-initiated "cancel" flows need explicit expire call.

**Implication:** Switching radio from PP to MB bank and clicking PAY NOW just works — backend handles the stale PP charge.

## Auth-Conditional Query Params

`expirePendingCharge()` must NOT send `?email=` when user is authenticated. Backend routes by param presence — authenticated endpoint uses Bearer token only. Sending `?email=` on an authenticated call causes URL signature mismatch and can trigger guest routing path.

**Rule:** Always condition query param on `!token` (not `!!email`). Token presence determines auth context.

## Dual Cancel Surface — Mutual Exclusion Required

When two UI elements can both cancel the same charge (e.g., PAYMENT_PENDING amber alert + PendingChargeNotice), they must be mutually exclusive. Both elements firing expire on the same chargeId: first succeeds (200), second gets 400.

**Guard pattern:** Render `PendingChargeNotice` only when `paymentError?.type !== 'PAYMENT_PENDING'`. When PAYMENT_PENDING alert is active, it owns the cancel action exclusively.

## Centralized Payment Error Detection

4 components handle 409 `payment_pending` from cart mutations: `EditableCartItem.js` (PATCH), `InlinePassengerSelector.js` (inline update), `BookButton.js` (add to cart), `EnhancedTripCard.js` (DELETE). Same detection logic was duplicated inline in all 4.

**Extracted:** `helpers/handleCartMutationError.js` — `isPaymentPendingError(error)`. Pure function checking `error?.status === 409 && error?.data?.error === 'payment_pending'`. Each component handles its own UI (setError, toast, CancelPaymentDialog).

**Latent bug caught:** `BookButton.js` had bare `error?.status === 409` — matched ALL 409 variants (amount_locked, ORDER_ALREADY_PAID), not just payment_pending. Showed cancel dialog for non-payment-pending errors. Fixed by using `isPaymentPendingError()`.

**Lesson:** When same error check duplicated 3+ times, extract — even if each consumer handles UI differently. Prevents subtle bugs (bare 409 vs specific payment_pending) and keeps error vocabulary consistent.

## Cross-Boundary Alert State Threading

Alert state in `index.js` is not accessible to `PaymentComponent.js` (3 levels deep). When `PaymentComponent` needs to clear it (e.g., after cancel), thread `setAlert` prop down: `index.js → PaymentStep → PaymentComponent`. Call `setAlert?.({ show: false })` in cancel success handler.

**Lesson:** Don't patch symptoms (disable PAY NOW via `alert.type === 'warning'` guard in FormCard). Thread state to where the action originates.

## sessionStorage Restore Timing

`useState` initializers run synchronously at module init — Redux-persist `cartId` is `null` at that point (rehydration is async). Restore logic that checks `cartId` match will see `null`, fail the match, and delete valid saved data.

**Pattern:** Any restore logic depending on Redux-persist state must be in a `useEffect` gated on `isCheckoutRehydrated && cartId` — not in `useState` initializer.

## Idempotency Key Scope

Scope idempotency key to `cartId:total` snapshot, not session. Regenerate when total changes (coupon applied, item removed). Backend deduplicates same key → returns existing order. Without total-scoped regeneration, user could apply coupon, get same key, and backend returns old order at old amount.

## Positional Language in Alerts

Never use "above" / "below" in alert messages unless DOM position is guaranteed. Alert from `index.js` (`AlertMessage` in FormCard) renders BELOW PaymentComponent's amber alert. If amber alert says "cancel below" but AlertMessage says "use button above" — both are wrong from opposite perspectives.

**Rule:** Use element names, not positions: "Use the 'Cancel This Payment' button to cancel it."

## Cart Reprovisioning After Payment Reset

After successful payment, `resetCart()` intentionally sets `state.cart.cartId = null` — old cart is paid and must be abandoned. This is correct behavior.

**Problem:** `withCartValidation` HOC is the only mechanism that creates a new cart. Trip detail and search pages are NOT wrapped with it — they worked before because an existing cart was present. After reset, BookButton reads `null` from Redux and fails:
```
[BookButton] Invalid cartId: null
```

**Fix:** Both order detail pages call `createCart()` immediately after `resetCart()` — fire-and-forget. By the time user navigates away, Redux (and persisted localStorage) has a fresh valid `cartId`.

```js
dispatch(cartActions.resetCart({ items: [], total: 0 }));
createCart({ email }).unwrap()
  .then(res => { if (res?.id) dispatch(cartActions.setCartId(res.id)); })
  .catch(() => {}); // HOC recovers on next booking page if this fails
```

**Auth flow:** `email = session?.user?.email ?? null`. NextAuth places email at `session.user.email` only — `session.email` is always undefined.

**Guest flow:** `email = router.query.email ? decodeURIComponent(router.query.email) : null`.

**Files:** `pages/orders/[orderid].js`, `pages/guest-order/[orderId].js`

**Lesson:** Any page that nulls shared Redux state (cartId, auth, etc.) is responsible for reprovisioning it before the user navigates away — don't rely on destination pages to recover.

## NextAuth Session Email — Root Level vs Nested

NextAuth session shape: `{ id, accessToken, user: { email, name, image }, ... }`. The session callback in `[...nextauth].js` sets custom fields (`id`, `accessToken`, `phoneNumber`, etc.) at root level — but NEVER `email`. Email flows through NextAuth's default provider pipeline into `session.user.email`.

**Correct access:** `session?.user?.email`
**Wrong access:** `session?.email` — always `undefined`

**Auth check:** `session?.id` (root level, correctly set by callback).

**Why this matters:** A wrong CLAUDE.md rule (`"Email: session?.email"`) directly caused a regression commit (`8b3151f`) that made checkout inaccessible for all auth users. The doc fix is as important as the code fix — future agents reading stale docs will re-introduce the same bug.

**Guest email sources** (never from session):
- Checkout form: `formData?.email`
- Order pages: `router.query.email` → `decodeURIComponent(email)`

**Files where this matters:** `pages/checkout/index.js`, `pages/checkout/PaymentComponent.js`, `pages/orders/[orderid].js`

## Related
- [[payment-system]]
- [[checkout-flow]]
- [[orders]]
- [[backend-architecture]]
