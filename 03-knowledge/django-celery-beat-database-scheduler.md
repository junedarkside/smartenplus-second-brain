# Django Celery Beat: DatabaseScheduler

## Summary
`DatabaseScheduler` stores beat schedule in DB (via Django admin UI), not in `settings.py` `beat_schedule`. Changes take effect without deploy or restart.

## Setup
```python
# settings.py
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
# No CELERY_BEAT_SCHEDULE dict needed
```

## Managing Schedules
Django admin → Periodic Tasks → Add/Edit `PeriodicTask`. Set task name (dotted path), interval, enabled flag. Changes live on next beat tick.

## vs Static Schedule
```python
# Static (NOT used with DatabaseScheduler):
CELERY_BEAT_SCHEDULE = {
    'my-task': {'task': 'myapp.tasks.do_thing', 'schedule': crontab(minute='*/10')}
}
```
Static requires redeploy on every schedule change. DatabaseScheduler avoids this.

## Operational Notes
- Beat container down → no tasks fire → time-sensitive flows (payment expiry, etc.) silently stall
- Check last run: `SELECT last_run_at FROM django_celery_beat_periodictask WHERE task='...'`
- `max_retries` / `default_retry_delay` on `@shared_task` has no effect unless `self.retry()` is explicitly called

## SmartEnPlus Usage
`smartenplus/settings.py:549` — `sync_pending_charges` schedule via admin.

## Related
- [[celery-beat-payment-scheduling]] — SmartEnPlus-specific scheduling
- [[celery-tasks]] — bind=True, retry, beat patterns
