# Payment Frontend Flow Mechanics

## Summary
Frontend has two distinct payment paths (Card vs Source). 14 non-obvious mechanics: canContinue gate, NO_CONTINUE_METHODS, pendingChargeState vs qrState split, amountLocked UX, JPY scaling, QR retry sequence, navigation guards.

## Context
`hooks/useOmisePayment.js`, `components/PaymentComponent.jsx`. Card flow is fully client-side (Omise.js modal). Source flow requires server redirect.

## Card vs Source Flow

### Card Flow
```js
OmiseInstance.card.open({
  frameLabel: 'SmartEnPlus',
  onCreateTokenSuccess: (nonce) => {
    dispatch(createCharge({ nonce, method: 'card' }))
  }
})
```
- Omise.js renders embedded modal
- User enters card → Omise returns token (nonce)
- Token sent to backend, backend calls Omise API
- **No redirect.** Payment resolves in-page.

### Source Flow (PromptPay, mobile banking, e-wallets)
```js
OmiseInstance.source.createSource(method, params, (statusCode, response) => {
  dispatch(createCharge({ sourceId: response.id, method }))
})
// Backend returns: { authorize_uri: 'https://...' }
// Frontend redirects user or shows QR
```

## canContinue Logic (useOmisePayment.js:208-218)
Gate before proceeding with charge for source methods:
```js
const canContinue = !!(
  chargeResult?.authorize_uri &&
  !NO_CONTINUE_METHODS.includes(paymentMethod) &&
  (expiresAt && expiresAt > Date.now() + 60_000)
)
```
All 3 conditions must pass:
1. `authorize_uri` present in charge response
2. Method NOT in `NO_CONTINUE_METHODS`
3. Expiry more than 60s in future

### NO_CONTINUE_METHODS
```js
const NO_CONTINUE_METHODS = [
  'card', 'debit',
  'mobile_banking_scb', 'mobile_banking_kbank',
  'mobile_banking_bay', 'mobile_banking_bbl', 'mobile_banking_ktb'
]
```
Mobile banking excluded because redirect is single-use; user completes in bank app. Frontend should NOT push to `authorize_uri` on return; mobile banking uses `qrState` path.

## pendingChargeState vs qrState Split
```js
// Non-PromptPay pending charge → PendingChargeNotice component
setPendingChargeState({ exists: true, chargeId, method, expiresAt })

// PromptPay pending charge → QRPaymentForm component
setQrState({ qrCodeUrl, expiresAt, chargeId })
```
Both components guard `!cancelState.success`. Cannot show simultaneously.

## amountLocked UX (useOmisePayment.js:185-200)
```js
if (error.data?.error === 'amount_locked') {
  setAmountLockedState({
    locked: locked_amount,
    attempted: attempted_amount
  })
}
```
Displays `PendingChargeNotice` with variant `amountLocked`:
- Heading: "Cart Changed"
- Shows both amounts (locked vs attempted)
- CTA: Cancel Only (no retry)

## 409 Mapping (useOmisePayment.js:166-184)
```js
'pending_charge_exists' → pendingChargeState (PendingChargeNotice)
'amount_locked'         → amountLockedState  (PendingChargeNotice variant)
'Order already paid'    → alreadyPaidState + clearPaymentProcessing()
```
`alreadyPaid` immediately clears `isPaymentProcessing` — no user intervention needed.

## QR Retry Sequence (useOmisePayment.js:310-340)
Critical state reset order on retry (must not change):
1. `clearPolling()`
2. `clearTimer()`
3. `resetQrStates()`
4. `setIsRetrying(true)`
5. `setRetryCount(prev => prev + 1)`
Max retries: 3. After 3 → QR error state (no 4th retry).

## Navigation Guards (PaymentComponent.jsx:88-115)
Two simultaneous guards:
```js
// Guard 1: Browser back/forward
router.beforePopState(() => {
  setPendingNavigation(true)
  setShowLeaveModal(true)
  return false
})

// Guard 2: Tab close / hard navigation
window.onbeforeunload = () => 'Payment in progress. Leave?'
```
On confirm leave: `expirePendingCharge()` called best-effort (errors swallowed). Both guards removed on component unmount.

## JPY Frontend Scaling (useOmisePayment.js:251)
```js
const chargeAmount = grandTotal * (isJPY ? 1 : 100)
```
Omise requires amounts in minor units. JPY has no minor unit (1 yen = 1). All other currencies multiply × 100 (satang, cents). Applied for card flow only — Source flow: backend handles via `_to_minor_units()`.

## OmiseScriptLoader Retry Bug (OmiseScriptLoader.js:48)
Comment says "exponential backoff". Code is linear:
```js
setTimeout(retry, 1000 * (loadAttempts + 1))  // 1s, 2s, 3s, ...
// Should be: 1000 * Math.pow(2, loadAttempts)  // 1s, 2s, 4s, 8s...
```
Bug: `loadAttempts` increments before retry calculation. Net result: 2s, 3s, 4s. Not exponential.

## SOURCE_CONFIG Limits (paymentMethods.js)
```js
SOURCE_CONFIG = {
  wechat_pay:  { min: 100,  max: 15_000_000 },  // satang
  truemoney:   { min: 2000, max: 15_000_000 },
  alipay:      { min: 2000, max: 15_000_000 },
  // all others: min: 2000, max: 15_000_000
}
```
WeChat min is 100 satang (1 THB). All others: 20 THB min.

## Related
- [[payment-qr-polling-mechanics]] — QR state machine after charge created
- [[payment-exception-catalog]] — 409 backend responses that trigger above UI states
- [[payment-gateway-charge-architecture]] — canContinue flows to authorize_uri
- [[payment-status-enums]] — METHOD_EXPIRY feeds canContinue expiresAt check
