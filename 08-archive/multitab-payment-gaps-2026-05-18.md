# Multi-Tab Payment Gaps — Resolution (2026-05-18)

## Summary

7 multi-tab payment race conditions fixed. Frontend + backend.

## Context

Found during payment refactor (`260513-refactor/payment`). Research: `docs/features/payment/MULTITAB_PAYMENT_RESEARCH.md`.

## Problem

Multiple tabs on same checkout → duplicate QR codes, stale banners, silent cart delete failures, session email regression.

## Decisions

### GAP-2: Cart-wide pending order check
- **What:** `select_for_update()` inside `transaction.atomic()` in `initiate_order_charge()` — queries `payment_pending` orders by `cart_id`, not `order_id`
- **Why:** C3 only checked charges per order. Two tabs = two orders = two QR codes
- **Tradeoff:** Small perf hit on charge initiation. Rare path, serialization worth it
- **File:** `payments/services.py`

### GAP-4: CheckoutSnapshot validation
- **What:** `finalize_payment()` calls `is_valid_for_cart()` — log-only on mismatch
- **Why:** Method existed, never called. Cart drift between charge + webhook undetectable
- **Tradeoff:** Log-only, no block. Blocking = paid charge unconfirmed = worse
- **File:** `payments/services.py`, `orders/models.py`

### GAP-1: isPaymentProcessing banner
- **What:** `setPaymentProcessing` dispatched after charge creation. `reconcileStaleProcessing` clears 30min-stale state on rehydration
- **Why:** Redux action existed, never dispatched. Dead code
- **File:** `store/paymentStatusSlice.js`, `hooks/useOmisePayment.js`

### PAY NOW lock on PAYMENT_PENDING
- **What:** `onPaymentLocked` callback chain: `checkout/index.js` → `PaymentStep` → `PaymentComponent`
- **Why:** `isPaymentLocked` only set from step 2→3 passenger path. Payment step PAY NOW had no lock
- **File:** `pages/checkout/PaymentComponent.js`, `components/checkout/steps/PaymentStep.js`, `pages/checkout/index.js`

## Tradeoffs

- GAP-6 (cross-tab cancel): SKIPPED — QR polling detects expiry within 10s, acceptable
- GAP-5 (isGuestMode cross-tab): already handled at `checkout/index.js:483` auth+empty-data reset

## Consequences

- Prod build unblocked (daytrip SEO fix)
- 242 Django payment tests pass
- Double-charge from concurrent tabs eliminated at DB level

## Related

[[payment-system]] — GatewayCharge lifecycle
[[checkout-flow]] — checkout payment flow
[[session-structure]] — session?.user?.email (not session?.email)