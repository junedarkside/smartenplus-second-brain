# Celery Beat Payment Scheduling

## Summary
`sync_pending_charges` schedule is managed via Django admin UI (DatabaseScheduler), NOT in settings.py `beat_schedule`. Schedule lives in DB, not code. Changes take effect without deploy.

## Context
`smartenplus/settings.py:549`, `payments/tasks.py`. Understanding where the schedule lives matters for ops — wrong place to look causes hours of debugging why task isn't running.

## DatabaseScheduler Pattern

```python
# settings.py:549
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
# No CELERY_BEAT_SCHEDULE dict in settings.py
```

`DatabaseScheduler` reads task schedules from `django_celery_beat.models.PeriodicTask` DB table. Admin manages them via `/admin/django_celery_beat/periodictask/`.

**Not** the static `beat_schedule` dict pattern:
```python
# This is NOT how it's done here — common pattern in other Django projects
CELERY_BEAT_SCHEDULE = {
    'sync-pending-charges': {'task': '...', 'schedule': crontab(minute='*/10')}
}
```

## How to View/Change Schedule

1. Django admin → `Periodic tasks` → `Periodic Tasks`
2. Find `payments.tasks.sync_pending_charges`
3. Edit interval (e.g., every 10 minutes = `10` `minutes`)
4. Changes take effect on next beat tick — **no restart needed**

## Task: `sync_pending_charges` (`payments/tasks.py:14-97`)
```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_pending_charges(self):
    # Handles 3 charge types:
    # 1. PromptPay: self-expires locally (no Omise query)
    # 2. Mobile banking: polls Omise after TTL
    # 3. E-wallets: 30-min fallback reconciliation
```

**Critical:** `max_retries=3` and `default_retry_delay=60` are configured but `self.retry()` is **NOT called** in the exception handler. Task failures are log-only. Retry configuration is dead code. See [[payment-celery-expiry-strategy]].

## Celery Worker + Beat Setup (Docker)
```yaml
# docker-compose.yml pattern
celery-beat:
  command: celery -A smartenplus beat -l info
celery-worker:
  command: celery -A smartenplus worker -l info -Q default,payments
```
Beat and worker run as separate containers. Beat pushes tasks to queue; worker executes them. If beat container down → no periodic expiry → PromptPay charges never expire → users stuck in `payment_pending`.

## Monitoring
Check if beat is running:
```bash
celery -A smartenplus inspect scheduled
# Should show sync_pending_charges in scheduled queue
```

Check last run:
```sql
SELECT last_run_at, total_run_count FROM django_celery_beat_periodictask
WHERE task = 'payments.tasks.sync_pending_charges';
```

## Related
- [[payment-celery-expiry-strategy]] — what sync_pending_charges does per method type
- [[promptpay-no-webhook-on-expiry]] — why Celery is the only expiry path for PromptPay
- [[celery-tasks]] — general Celery patterns (bind=True, retry, beat schedule)
