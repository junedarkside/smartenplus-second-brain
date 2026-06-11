# Payment QR Polling Mechanics

## Summary
`useQRPolling` handles 4 response formats, 3 status signals, guest vs auth request signatures, and a final status check after QR expiry. 10s default interval from backend field.

## Context
`hooks/useQRPolling.js`. Polls order status while user scans QR code. Stops on terminal status or expiry. Backend controls polling interval to allow future tuning without frontend deploys.

## Polling Interval (useQRPolling.js:186)
```js
const pollingInterval = orderDetails?.polling_interval || 10000  // 10s default
```
`polling_interval` from order response. Backend can return different intervals per order type. Frontend fallback = 10s.

## Request Signatures (useQRPolling.js:94-115)

### Authenticated
```js
headers: { Authorization: `Bearer ${token}` }
// No query params for auth
```

### Guest
```js
// No auth header
params: { email: guestEmail }
```
Condition: `!token && guestEmail` (not `!!guestEmail` — prevents leaking auth context if token somehow absent). See [[nextauth-session-shape]] for `expirePendingCharge` auth rule.

## Response Fallback Chain (useQRPolling.js:140-175)
4 formats handled in priority order:
```js
// Format 1: array response
if (Array.isArray(response.data)) {
  order = response.data.find(o => o.order_id === targetOrderId)
}
// Format 2: booking-nested
else if (response.data?.booking?.orders) {
  order = response.data.booking.orders.find(o => o.order_id === targetOrderId)
}
// Format 3: direct order object
else if (response.data?.order_id) {
  order = response.data
}
// Format 4: direct response is the order
else if (response.data?.status) {
  order = response.data
}
```
Fails silently if none match — logs warning, continues polling.

## Stop Conditions (useQRPolling.js:195-215)

### Primary: `should_stop_polling` field
```js
if (order?.should_stop_polling === true) {
  stopPolling()
  handleTerminalStatus(order)
}
```
Backend controls stop signal. Preferred path — decouples frontend from status enum knowledge.

### Secondary: `currentChargeStatus`
```js
TERMINAL_STATUSES = ['paid', 'failed', 'expired', 'refunded']
if (TERMINAL_STATUSES.includes(order?.currentChargeStatus)) {
  stopPolling()
}
```

### Tertiary: `orderStatus` (legacy)
```js
if (order?.orderStatus === 'paid') stopPolling()
```
Kept for backwards compat with old response shape.

## Final Status Check on Expiry (useQRPolling.js:238-262)
```js
const handleQrExpiry = async () => {
  if (finalStatusChecked.current) return  // guard prevents double-check
  finalStatusChecked.current = true

  const finalStatus = await pollOnce()  // single immediate request
  if (finalStatus?.order?.status === 'paid') {
    // User paid in bank app after QR visually expired
    handleSuccess(finalStatus.order)
  } else {
    setQrExpired(true)
    stopPolling()
  }
}
```
**Why:** PromptPay 10-min TTL can elapse while user is mid-transaction. QR shows "expired" but payment may have landed microseconds before expiry. Final check recovers this case.

`finalStatusChecked.current` ref (not state) prevents double-check on strict-mode double-invoke or retry.

## Polling Lifecycle
```
createCharge success
  → setQrState({ qrCodeUrl, expiresAt, chargeId })
  → startPolling(interval)
      ↓ every {pollingInterval}ms
    pollOrderStatus()
      → check should_stop_polling → stop if true
      → check currentChargeStatus → stop if terminal
      ↓
  Countdown hits 0
    → handleQrExpiry()
      → finalStatusChecked = true
      → pollOnce()
        → paid? → handleSuccess
        → not paid? → setQrExpired, stopPolling
```

## Cleanup
```js
useEffect(() => {
  return () => {
    clearPolling()  // clears interval
    clearTimer()    // clears countdown
    // does NOT call expirePendingCharge on unmount
    // user may navigate back; charge survives
  }
}, [])
```
Charge NOT expired on component unmount — user could re-open QR page. Explicit cancel only via Cancel button → `expirePendingCharge()`.

## Related
- [[payment-frontend-flow-mechanics]] — how QR state is set, retry sequence
- [[payment-gateway-charge-architecture]] — GatewayCharge expiry paths
- [[payment-celery-expiry-strategy]] — backend expiry on QR timeout
- [[promptpay-no-webhook-on-expiry]] — why final check matters
