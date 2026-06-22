---
name: payment-polling-fallback-triple
description: Triple fallback for payment webhook delivery failure: client-side QR code polling → manual payment-status refresh → staff force-expiry. Covers Omise webhook downtime, missed events, redirect-method expiry paths.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: payment-deep-review
---

# Payment Polling Fallback — Triple Redundancy

## Summary
Triple fallback for webhook delivery failure: QR code polling (auto) → payment-status refresh (manual) → staff force-expiry (admin). Covers Omise downtime, missed webhooks, redirect-method expiry.

## Why It Matters
Webhooks can fail ( downtime, spam filters, misconfigured URLs ). Customers need a recovery path to complete payment without support intervention.

## Detail
**Fallback 1 (automatic — client-side QR polling):**
```jsx
// useQRPolling.js pattern
const POLL_INTERVAL = 3000; // every 3s
const MAX_POLLS = 40; // 2 minutes
// Poll GET /api/payments/status/{charge_id}
// Stop when charge.status != 'pending'
```

**Fallback 2 (manual — customer action):**
"Payment taking longer? Refresh page." Button re-checks status via GET `/orders/{order_id}/`.

**Fallback 3 (admin — staff override):**
`ExpirePendingChargeView` — DELETE `/payments/expire/{pending_charge_id}/` (staff-only). Force-mark expired → allow retry.

**Webhook failures covered:**
- Omise downtime → QR polling succeeds
- Missed webhook event → manual refresh catches paid status
- Redirect-method expiry (e.g., PromptPay timeout) → staff force-expire → customer retries

## Constraints / Gotchas
QR polling MUST use `setTimeout` recursion (not `setInterval`) → avoids request stacking on slow response. Tab idle → stop polling (respect `requestAnimationFrame` or `Page Visibility API`).

## Related
- [[payment-deep-review]] — M8 finding (webhook reliability gap)
- [[useQRPolling]] — frontend polling pattern (reused in chat widget)
