# PromptPay No Webhook on Expiry

## Summary
Omise sends NO webhook when PromptPay or mobile banking charges expire — only Celery handles expiry.

## Why It Matters
If you add a new expiry path and forget to call `_send_payment_failed_notifications()`, users never get notified. All 3 expiry paths must explicitly trigger notifications.

## Detail
Omise webhook gap:
- `charge.complete` → success only
- `charge.expire` → Barcode Alipay only
- **PromptPay + mobile banking expiry = NO webhook**

Three expiry paths (all must call `_send_payment_failed_notifications()`):
1. `sync_pending_charges` Celery task (every 10 min) — PP expired → `finalize_payment_failed`
2. `ExpirePendingChargeView` (user cancel) → reset to `ordering`
3. `expire_stale_payments` management command

E-wallets: reconciled after 30 min stale threshold (no TTL from Omise).

## Constraints / Gotchas
- QR → redirect method switch: backend `C3b` proactively expires pending PP — frontend does NOT need to expire before switching
- Only explicit user "cancel" flows need `expirePendingCharge()` on frontend

## Related
- [[payment-integration]]
- [[payment-system]]
- [[celery-tasks]]
