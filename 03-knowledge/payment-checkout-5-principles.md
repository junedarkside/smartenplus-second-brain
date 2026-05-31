# Payment Checkout — 5 Architecture Principles

## Summary
5 core architecture principles governing SmartEnPlus checkout. Immutable snapshot, webhook-only finalization, single active attempt, cart lock, explicit cancel-recreate.

## Context
Extracted from [[payment-integration]]. Canonical reference for checkout architecture decisions. Full 28-use-case doc: `docs/features/payment/PAYMENT_CHECKOUT_ARCHITECTURE_REVIEW.md`.

## Details

**1. Webhook = source of truth.** Frontend redirect MUST NOT finalize. Only webhook marks paid, creates booking items, finalizes settlement.

**2. One active payment attempt.** One order → one pending intent → one amount snapshot. Prevents duplicate charges, conflicting QR codes.

**3. Immutable payment snapshot.** Charge created → amount, items, discounts, method frozen. `CheckoutSnapshot` created after charge.

**4. Cart locked during `payment_pending`.** ALL cart mutations blocked (PATCH/DELETE, add, coupon). Backend `409 PAYMENT_PENDING`. Frontend amber warning.

**5. Explicit cancel-and-recreate.** Expire charge → unlock → user selects new method → new intent. Never mutate active payment.

### State Machine
```
editable → payment_pending → paid
editable → payment_pending → expired/cancelled → editable
```

### Implemented Patterns (Frontend)
- `getBillingAndOrder.js`: 409 maps `payment_pending` → `PAYMENT_PENDING`, `amount_locked` → `AMOUNT_LOCKED`
- `usePaymentInitialization.js`: idempotency key `cartId:total`
- `PaymentComponent.js`: `handleCancelPendingPayment()` → expire + refetch
- `expirePendingCharge()` + `getReconcileOrder()` in `getBillingAndOrder.js`
- Cross-tab sync: `cart_version` storage key + listener in `store/index.js`
- formData sessionStorage: persists form state, validates freshness (30min) + cartId match

## Related
- [[payment-integration]] — parent note
- [[payment-gateway-charge-architecture]] — GatewayCharge model + finalize_payment() SSOT
- [[payment-checkout-architecture-audit]] — 20/20 audit findings
- [[checkout-flow]] — cart, SSR-disabled checkout, guest mode
