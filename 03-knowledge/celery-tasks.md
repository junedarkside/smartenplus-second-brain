# Celery Tasks — SmartEnPlus

## Summary
Django Celery + Beat. All tasks: `bind=True, max_retries=3, default_retry_delay=60`. Exponential backoff: `countdown = min(60 * (2 ** retries), 3600)`. Missing AWS SES/Telegram env vars → silent failures.

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

`bind=True` → task gets `self` for retry control + request info.

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

## Beat Schedule

### Daily
- **`reset_daily_counter`** — `0 0 * * *`. Adds `daily_counter` to `booked_count` on all Contracts, resets to 0.
- **`soft_delete_expired_ratecards`** — `0 1 * * *`. Soft-deletes `Contract_RateCard` where `rate_date < today` + `rate_date IS NOT NULL`. Preserves defaults (`rate_date=NULL`).

### Periodic
- **`sync_pending_charges`** — self-expires PP charges after TTL. MB/redirect: calls `reconcile_gateway_charge()`. E-wallets/international reconciled after 30 min stale. All paths notify via `finalize_payment_failed` or `reconcile_gateway_charge` → `_sync_order_status`. Beat: `*/10` min.
- **`send_review_invitation_emails`** — passengers `traveling_date = yesterday`. Dedup by `slug`. `@log_email_event(email_type='review')` guard.

## High-Risk Tasks (Duplicate Side-Effect on Retry)

### `send_booking_confirmation_email` (`carts/tasks.py`)
- **Guard:** `@log_email_event(email_type='booking')` (checks `UserJourneyEvent` for `email_booking_sent`).
- **Env:** `AWS_SES_REGION_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `DEFAULT_FROM_EMAIL`.
- Missing AWS creds → `ClientError` → retries → exhausted → logged.

### `send_html_email` (`carts/tasks.py`)
- **Guard:** `@log_email_event(email_type='order')`.
- **Used by:** `finalize_payment()` on order success. SES order confirmation.
- **Env:** same as above.

### `send_booking_data` (`orders/tasks.py`)
- **No task-level guard.** Duplicate risk accepted — dispatch endpoint migrating.
- **Env:** `AUTO_SMARTENPLUS_API_URL` (required), `AUTO_SMARTENPLUS_API_KEY` (optional).
- Missing URL → logs warning + returns. No retry.

### Telegram Tasks (`payments/tasks.py`)
- `send_booking_data_by_telegram` / `send_email_success_telegram` / `send_booking_email_success_telegram` — `@log_telegram_event` guard. Env: `SEP_NOTIFY_bot` + `SEP_GROUP_ID`.
- `send_orphaned_cleanup_telegram` — when ≥5 orphans found.
- Missing config → logs warning + returns `{"status": "skipped", "reason": "missing_config"}`.

## Cleanup Tasks

### `cleanup_orphaned_cart_items` (`orders/tasks.py`)
- Catches cart items missed during normal payment processing.
- Every 2h via beat. Finds paid orders (last 48h) with carts, deletes remaining `CartItem` entries.
- Telegram alert if ≥5 orphans. Stats cached (2h TTL), daily aggregate.

## Email Env Vars (Required)

```bash
AWS_SES_REGION_NAME=ap-southeast-1
AWS_SES_REGION_ENDPOINT=email.ap-southeast-1.amazonaws.com
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
DEFAULT_FROM_EMAIL=noreply@smartenplus.co.th
```

Missing any → silent failure.

## Related
- [[backend-architecture]]
- [[payment-system]]
- [[orders]]