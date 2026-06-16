# n8n Webhook Resend Operator — Implementation Post-mortem

**Date:** 2026-05-25
**Branch:** `feat/n8n-resend-webhook`
**Commits:** `fa687cb`, `4285e70`, `8d88ba3`, `2bdf31b`
**Status:** Merged to develop

---

## Summary

Added n8n webhook forwarding to "Resend Operator" button in admin-dashboard. Button triggers `send_booking_data` Celery task → POSTs booking JSON to external targets. New target: `N8N_WEBHOOK_URL` (plain webhook, no auth). Enables n8n automation workflows to receive booking data on demand.

---

## Architecture

```
Resend Operator btn → POST /admin-dashboard/booking-send/ {slug}
  → SendBookingViewSet.create() (bookings/views.py:369)
    → send_booking_data_for_booking() (bookings/views.py:398)
      → send_booking_data.delay(context) (carts/tasks.py → now bookings/tasks.py)
        → POST to AUTO_SMARTENPLUS_API_URL (if configured)
        → POST to N8N_WEBHOOK_URL (if configured)
        → one failing → retry entire task (all targets re-sent)
```

---

## Commits

| SHA | Description |
|-----|-------------|
| `fa687cb` | refactor: move send_booking_data to bookings/tasks.py + add n8n multi-target loop |
| `4285e70` | hotfix: orders/services.py import split + remove orphaned try block |
| `8d88ba3` | hotfix: orders/views.py import split |
| `2bdf31b` | fix: N8N_WEBHOOK_URL default=None — prevent Celery crash on missing env |

---

## Bug 1 — Import crash (orders/views.py + orders/services.py)

**Symptom:** `send_booking_confirmation_email` imported from `bookings.tasks` — NOT defined there, lives in `carts.tasks:220`. Crashes with `ImportError` at Django load.

**Root cause:** Refactor moved `send_booking_data` to `bookings.tasks` but NOT `send_booking_confirmation_email` (stays in `carts.tasks`). Import incorrectly pulled all three from `bookings.tasks`.

**Fix:** Split import in both files:
```python
from bookings.tasks import send_booking_data, send_booking_data_by_telegram
from carts.tasks import send_booking_confirmation_email
```

**Files:** `orders/services.py:8-12`, `orders/views.py:25`

---

## Bug 2 — Orphaned try block (carts/tasks.py)

**Symptom:** Bare `try` block with Telegram code (169 lines) outside any function after comment `# Bookings dispatch tasks moved to bookings/tasks.py`. Executes at import time — syntax/runtime error.

**Root cause:** Incomplete cleanup when moving tasks. Removed function definitions, left body.

**Fix:** Deleted orphaned code block (lines 499-665).

---

## Bug 3 — N8N_WEBHOOK_URL default=None missing

**Symptom:**
```
decouple.UndefinedValueError: N8N_WEBHOOK_URL not found. Declare it as envvar or define a default value.
```
Celery crashed every startup. Django couldn't load settings.

**Root cause:** `config('N8N_WEBHOOK_URL')` no default → raises immediately if env var absent. All other optional URL env vars in `settings.py` use `default=None`.

**Fix:**
```python
N8N_WEBHOOK_URL = config('N8N_WEBHOOK_URL', default=None)
```

---

## Key Files

| File | Role |
|------|------|
| `Smartenplus/settings.py:588` | N8N_WEBHOOK_URL env var |
| `bookings/tasks.py:128` | `send_booking_data` — multi-target forwarding loop |
| `bookings/tasks.py:163` | `send_booking_data_by_telegram` — Telegram notification |
| `orders/services.py:15` | `dispatch_booking_notifications` — triggers all notification tasks |
| `orders/views.py:369` | `SendBookingViewSet.create()` — Resend Operator endpoint |

---

## Env Var

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `N8N_WEBHOOK_URL` | No | `None` | Plain webhook URL for n8n automation |

Auth: none. Not set → task logs warning, returns cleanly.

---

## Retry Behavior

`send_booking_data` has `bind=True, max_retries=3, default_retry_delay=60`. Any target raises network exception → `raise self.retry(exc=e)` → task re-queued (all targets re-sent). HTTP non-200 → logs error only, no retry.

**Important:** n8n network failure → primary AUTO_SMARTENPLUS_API_URL also re-sends on retry. Acceptable for n8n (external sink). If unacceptable → split into separate tasks.

---

## Post-mortems

### N8N_WEBHOOK_URL Celery crash (commit 2bdf31b)

**Root cause:** `config('N8N_WEBHOOK_URL')` no `default=` → raises UndefinedValueError when env var absent. All other optional URL env vars use `default=None` — new var didn't follow pattern.

**Fix:** `default=None` added.

**Why slipped:** Didn't follow existing pattern. No CI gate tests Django startup without all optional env vars.

---

## Related

[[master-state]] — updates: n8n webhook implementation tracked
[[payment-checkout-architecture-audit]] — Celery task location history (was carts/tasks.py, now bookings/tasks.py)
[[site-url-config-pattern]] — all optional env vars must use `default=None`