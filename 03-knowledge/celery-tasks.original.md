# Celery Tasks — SmartEnPlus

## Summary
Django Celery + Beat. All tasks: `bind=True, max_retries=3, default_retry_delay=60`. Exponential backoff: `countdown = min(60 * (2 ** retries), 3600)`. Missing AWS SES or Telegram env vars → silent failures.

---

## Standard Pattern

```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def task_name(self, arg):
    try:
        # work
    except Exception as exc:
        countdown = min(60 * (2 ** self.request.retries), 3600)
        raise self.retry(exc=exc, countdown=countdown)
```

`bind=True` — task gets `self` for retry control + request info.

---

## Apps with Tasks

| App | Tasks |
|-----|-------|
| `orders` | `sync_pending_charges`, `send_booking_data` |
| `bookings` | `send_review_invitation_emails` |
| `operators` | `reset_daily_counter`, `soft_delete_expired_ratecards` |
| `carts` | `send_html_email`, `send_booking_confirmation_email` |
| `payments` | `send_booking_data_by_telegram`, `send_email_success_telegram`, `send_booking_email_success_telegram`, `cleanup_orphaned_cart_items`, `send_orphaned_cleanup_telegram` |
| `products` | `precompute_contract_on_create` (signal), `precompute_popular_contracts` (hourly), `precompute_all_active_contracts` (nightly 2am), `update_route_query_counts` (weekly), `cleanup_expired_recommendation_cache` (daily 3am), `clear_old_query_logs`, `get_cache_statistics` |
| `cards` | `fetch_forex_rates` (Omise Forex API → ForexData, 11 currencies: aud/chf/cny/dkk/eur/gbp/hkd/jpy/sgd/thb/usd) |

---

## Beat Schedule

### Daily Tasks
- **`reset_daily_counter`** — `0 0 * * *` (midnight). Adds `daily_counter` to `booked_count` on all Contracts, then resets counter to 0.
- **`soft_delete_expired_ratecards`** — `0 1 * * *` (1am). Soft-deletes `Contract_RateCard` where `rate_date < today` and `rate_date IS NOT NULL`. Preserves default rate cards (`rate_date=NULL`).

### Periodic / On-Demand
- **`sync_pending_charges`** — self-expires PromptPay charges after TTL (`METHOD_EXPIRY[OmiseMethod.PROMPTPAY]`). For mobile banking/redirect methods, calls `reconcile_gateway_charge()` to poll Omise. E-wallets/international methods (not in `METHOD_EXPIRY`, excluding CC/debit) reconciled after 30 min stale threshold. All paths trigger notification via `finalize_payment_failed` or `reconcile_gateway_charge` → `_sync_order_status`. Beat schedule: every 10 min (`crontab(minute='*/10')`).
- **`send_review_invitation_emails`** — sends invite to passengers whose `traveling_date = yesterday`. Deduplicates by `slug`. Uses `@log_email_event(email_type='review')` guard.

---

## High-Risk Tasks (Duplicate Side-Effect on Retry)

### `send_booking_confirmation_email` (`carts/tasks.py`)
- **Guard:** `@log_email_event(email_type='booking')` decorator (checks `UserJourneyEvent` for `email_booking_sent`).
- **Env vars required:** `AWS_SES_REGION_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `DEFAULT_FROM_EMAIL`.
- **Silent failure:** if AWS creds missing → `ClientError` → retries → exhausted → logged as error.

### `send_html_email` (`carts/tasks.py`)
- **Guard:** `@log_email_event(email_type='order')` decorator.
- **Used by:** `finalize_payment()` on order success. Sends order confirmation via SES.
- **Env vars required:** same as above.
- **Silent failure:** same pattern.

### `send_booking_data` (`orders/tasks.py`)
- **No task-level guard.** Duplicate risk accepted — dispatch endpoint migrating.
- **Env vars:** `AUTO_SMARTENPLUS_API_URL` (required), `AUTO_SMARTENPLUS_API_KEY` (optional).
- **Silent failure:** if `AUTO_SMARTENPLUS_API_URL` not set → logs warning + returns without error. Does NOT retry.

### Telegram Tasks (`payments/tasks.py`)
- **`send_booking_data_by_telegram`** — `@log_telegram_event` guard. Uses `SEP_NOTIFY_bot` + `SEP_GROUP_ID` env vars.
- **`send_email_success_telegram`** — `@log_telegram_event` guard. Not retried on config errors (logged and skipped).
- **`send_booking_email_success_telegram`** — `@log_telegram_event` guard.
- **`send_orphaned_cleanup_telegram`** — sent when ≥5 orphaned cart items found.
- **Silent failure:** if bot token or chat ID not configured → logs warning + returns `{"status": "skipped", "reason": "missing_config"}`.

---

## Cleanup Tasks

### `cleanup_orphaned_cart_items` (`orders/tasks.py`)
- **Purpose:** catches cart items not cleaned during normal payment processing (webhook + polling).
- **Runs:** every 2 hours via beat.
- **Logic:** finds paid orders from last 48 hours with carts, deletes any remaining `CartItem` entries.
- **Alerts:** sends Telegram if ≥5 orphans found (via `send_orphaned_cleanup_telegram`).
- **Stats:** cached to `last_orphaned_cleanup_result` + `last_orphaned_cleanup_timestamp` (2h TTL), daily aggregate to `orphaned_cleanup_stats_{date}`.

---

## Email Env Vars (Required for All Email Tasks)

```bash
AWS_SES_REGION_NAME=ap-southeast-1
AWS_SES_REGION_ENDPOINT=email.ap-southeast-1.amazonaws.com
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
DEFAULT_FROM_EMAIL=noreply@smartenplus.co.th
```

Missing any → silent failure (task logs error, doesn't raise, exhausts retries silently).

---

## Related
- [[backend-architecture]]
- [[payment-system]]
- [[orders]] (source of `sync_pending_charges` + `send_booking_data`)