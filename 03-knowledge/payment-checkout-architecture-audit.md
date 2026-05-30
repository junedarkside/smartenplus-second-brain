# Payment Checkout Architecture Audit

## Summary
20/20 audit pass. 5 fixes applied: getPrimaryCharge sort direction, cancelState guards, qrState clear, cancelState reset effect.

## Context
Verify implementation compliance against architecture doc. Fix cancel flow UX conflicts.

## Details

### Fix1 — getPrimaryCharge sort direction
`helpers/paymentMethods.js` — sort ascending + findLast → returns latest successful charge (was oldest).

### Fix 2 — QRPaymentForm guard
`!cancelState.success && !pendingChargeState.exists &&` added → prevents QR + "Payment Cancelled" alert simultaneous render.

### Fix 3 — PendingChargeNotice guard
`!cancelState.success &&` added → prevents dual cancel surface.

### Fix 4 — qrState cleared on Continue
`setQrState(...)` clears stale QR on "Continue to Checkout" click.

### Fix 5 — cancelState reset effect
`useEffect([paymentState.selectedPayment, cancelState.success])` resets cancelState on payment method change.

### Cancel Flow State Machine
`cancelState` states: idle / cancelling / error / success
On success: qrState cleared, pendingChargeState cleared, paymentError cleared via refetch.
Resets on: "Continue to Checkout" click, payment method change, component unmount.

## Decision
PromptPay excluded from one-active-lock per architecture doc. Webhook = sole payment finalization source.

## Tradeoffs
- Cancel state machine: additional useEffect dependency. Worth it for UX correctness.
- Simultaneous QR + cancel alert: both guard conditions needed (Fix 2 + Fix 3).

## Consequences
- getPrimaryCharge now returns chronologically last successful charge
- Cancel flow cannot surface simultaneously with QR or pending charge
- Payment method change resets cancel state cleanly

## Related
- [[payment-gateway-charge-architecture]]
- [[payment-integration]]
- [[checkout-flow]]