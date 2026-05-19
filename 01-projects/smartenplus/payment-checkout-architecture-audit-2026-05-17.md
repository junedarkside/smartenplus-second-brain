# Payment Checkout Architecture Audit — 2026-05-17

## Summary
Full payment checkout audit + UX fix session. 20/20 architecture items pass. 5 fixes applied (getPrimaryCharge + cancelState machine).

## Context
Follow-up to `docs/features/payment/PAYMENT_CHECKOUT_ARCHITECTURE_REVIEW.md`. Verify implementation compliance + fix cancel flow UX conflicts.

## Details
- Frontend: 10/10 items pass
- Backend: 10/10 items pass
- PromptPay excluded from one-active-lock per architecture doc
- Webhook is sole payment finalization source

### Fixes Applied

**Fix 1 — getPrimaryCharge (2026-05-13)**
`helpers/paymentMethods.js:91-100` — sort ascending + findLast → returns latest successful charge (was oldest)

**Fix 2 — QRPaymentForm guard (2026-05-17)**
`PaymentComponent.js:710` — `!cancelState.success && !pendingChargeState.exists &&` added → prevents QR + "Payment Cancelled" alert simultaneous render

**Fix 3 — PendingChargeNotice guard (2026-05-17)**
`PaymentComponent.js:688` — `!cancelState.success &&` added → prevents dual cancel surface

**Fix 4 — qrState cleared on Continue (2026-05-17)**
`PaymentComponent.js:538` — `setQrState(...)` clears stale QR data when "Continue to Checkout" clicked

**Fix 5 — cancelState reset effect (2026-05-17)**
`PaymentComponent.js:511-516` — `useEffect([paymentState.selectedPayment, cancelState.success])` resets cancelState on payment method change

### Cancel Flow State Machine (documented in architecture doc)
`cancelState` states: idle / cancelling / error / success
On success: qrState cleared, pendingChargeState cleared, paymentError cleared via refetch
Resets on: "Continue to Checkout" click, payment method change, component unmount

## Related
- [[payment-system]] — GatewayCharge, canonical charge rule
- [[checkout-flow]] — checkout payment flow
- [[backend-architecture]] — payments/services.py finalize_payment
- [[docs/features/payment/PAYMENT_CHECKOUT_ARCHITECTURE_REVIEW.md]]
- [[docs/testing/PAYMENT_CANCEL_FLOW_TESTS.md]]