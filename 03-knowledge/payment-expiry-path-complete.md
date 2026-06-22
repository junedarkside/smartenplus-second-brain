---
name: payment-expiry-path-complete
description: Complete expiry-path coverage for all payment methods: redirect-method cards (3DS, OTP), off-site banks, PromptPay QR. Celery Beat schedule (every 5m) + manual force-expiry + webhook expiry. No method leaves hanging orders.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: payment-deep-review
---

# Payment Expiry Path — Complete Coverage

## Summary
Expiry paths for all payment methods: redirect-method cards (3DS/OTP), off-site banks, PromptPay QR. Celery Beat (5-min) + manual force-expiry + webhook expiry. Full coverage.

## Why It Matters
Unexpired `payment_pending` orders lock inventory. Without expiry, stock unavailable forever. Every method needs reliable timeout.

## Detail
**Redirect-method cards (3DS, OTP):**
- User redirects to bank auth → returns to site
- Webhook `charge.complete` → `finalize_payment`
- **Expiry:** Celery Beat checks pending >15min → calls Omise API → if paid, finalize; if expired, mark `expired`

**Off-site banks:**
- User redirects → pays → returns
- Same webhook path
- **Expiry:** Celery Beat same 15-min check

**PromptPay QR:**
- QR generated → displayed → customer pays (external app)
- No redirect back
- **Expiry:** Celery Beat checks status → if paid, finalize; if >15min pending, mark `expired`

**Manual expiry (staff):**
`ExpirePendingChargeView` — DELETE `/payments/expire/{pending_charge_id}/` — force immediate expiry, allow retry.

**Webhook expiry:**
Charge `expired` event received → mark order `payment_expired` (fallback if Beat missed).

## Constraints / Gotchas
Celery Beat task (`expire_pending_charges`) must be idempotent and tolerant of concurrent webhooks. Use `select_for_update(skip_locked=True)` to prevent race.

## Related
- [[payment-deep-review]] — expiry path coverage gap
- [[payment-pending-deadlock-heal]] — paid-but-unfinalized deadlock
