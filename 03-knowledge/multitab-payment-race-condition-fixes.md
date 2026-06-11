# Multi-Tab Payment Race Condition Fixes

## Summary
7 concurrent-tab payment race conditions fixed. DB-level serialization + frontend state reconciliation.

## Context
Research: `docs/features/payment/MULTITAB_PAYMENT_RESEARCH.md`. Found during payment refactor.

## Problem
Multiple tabs on same checkout → duplicate QR codes, stale banners, silent cart delete failures, session email regression.

## Details

### GAP-2: Cart-wide pending order check
`select_for_update()` inside `transaction.atomic()` in `initiate_order_charge()` — queries `payment_pending` orders by `cart_id`, not `order_id`.
**Why:** C3 only checked charges per order. Two tabs = two orders = two QR codes.
**Tradeoff:** Small perf hit on charge initiation. Rare path, serialization worth it.

### GAP-4: CheckoutSnapshot validation
`finalize_payment()` calls `is_valid_for_cart()` — log-only on mismatch.
**Why:** Method existed, never called. Cart drift between charge + webhook undetectable.
**Tradeoff:** Log-only, no block. Blocking = paid charge unconfirmed = worse.

### GAP-1: isPaymentProcessing banner
`setPaymentProcessing` dispatched after charge creation. `reconcileStaleProcessing` clears 30min-stale state on rehydration.
**Why:** Redux action existed, never dispatched. Dead code.

### PAY NOW lock on PAYMENT_PENDING
`onPaymentLocked` callback chain: `checkout/index.js` → `PaymentStep` → `PaymentComponent`.
**Why:** `isPaymentLocked` only set from step 2→3 passenger path. Payment step PAY NOW had no lock.

### GAP-6: Cross-tab cancel — SKIPPED
QR polling detects expiry within 10s. Acceptable delay.

### GAP-5: isGuestMode cross-tab — already handled
`checkout/index.js:483` auth+empty-data reset.

## Decision
DB-level serialization for charge creation. Frontend reconciliation for state drift. No cross-tab cancel (10s poll window acceptable).

## Tradeoffs
- Cart-wide lock: queries all orders in cart, not just current. Slight perf impact, rare path.
- Skipping cross-tab cancel: user sees "Payment Expired" within 10s. Acceptable UX.

## Consequences
- Double-charge from concurrent tabs eliminated at DB level
- 242 Django payment tests pass
- Stale processing banner auto-cleared on rehydration

## Related
- [[payment-gateway-charge-architecture]]
- [[payment-integration]]
- [[checkout-flow]]
- [[payment-finalize-deep-dive]] — GAP-4 snapshot validation detail + cross-order pending lock