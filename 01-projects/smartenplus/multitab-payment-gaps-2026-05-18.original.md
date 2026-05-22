# Multi-Tab Payment Gaps — Resolution (2026-05-18)

## Summary

All 7 multi-tab payment race conditions identified and resolved across frontend + backend.

## Context

Identified during payment refactor (branch `260513-refactor/payment`). Research doc: `docs/features/payment/MULTITAB_PAYMENT_RESEARCH.md`.

## Problem

Multiple browser tabs on same checkout could cause: duplicate QR codes, stale processing banners, silent cart delete failures, session email regression.

## Decisions

### GAP-2: Cart-wide pending order check
- **What:** `select_for_update()` inside `transaction.atomic()` in `initiate_order_charge()` — queries `payment_pending` orders by `cart_id`, not just `order_id`
- **Why:** C3 check only queried charges on same order. Two tabs could create separate orders → two QR codes
- **Tradeoff:** Small perf cost on charge initiation. Acceptable — rare path, serialization is correct
- **File:** `payments/services.py`

### GAP-4: CheckoutSnapshot validation
- **What:** `finalize_payment()` calls `is_valid_for_cart()` — log-only on mismatch
- **Why:** Method existed in model, never called. Cart drift between charge creation and webhook undetectable
- **Tradeoff:** Log-only — does not block payment. Chosen because blocking = paid charge not confirmed = worse outcome
- **File:** `payments/services.py`, `orders/models.py`

### GAP-1: isPaymentProcessing banner
- **What:** `setPaymentProcessing` dispatched after charge creation. `reconcileStaleProcessing` reducer clears 30min-stale persisted state on rehydration
- **Why:** Redux action existed but was never dispatched. Banner was dead code
- **File:** `store/paymentStatusSlice.js`, `hooks/useOmisePayment.js`

### PAY NOW lock on PAYMENT_PENDING
- **What:** `onPaymentLocked` callback prop chain: `checkout/index.js` → `PaymentStep` → `PaymentComponent`
- **Why:** `isPaymentLocked` only set from step 2→3 passenger save path. Payment step PAY NOW had no equivalent
- **File:** `pages/checkout/PaymentComponent.js`, `components/checkout/steps/PaymentStep.js`, `pages/checkout/index.js`

## Tradeoffs

- GAP-6 (cross-tab cancel signal): SKIPPED — QR polling detects expiry within 10s, acceptable UX
- GAP-5 (isGuestMode cross-tab): already handled by existing `checkout/index.js:483` auth+empty-data reset

## Consequences

- Production build unblocked (daytrip SEO build fix)
- 242 Django payment tests pass
- Double-charge risk from concurrent tabs eliminated at DB level

## Related

[[payment-system]] — GatewayCharge lifecycle
[[checkout-flow]] — checkout payment flow
[[session-structure]] — session?.user?.email (not session?.email)
