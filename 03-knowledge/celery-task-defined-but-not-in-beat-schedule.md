# celery-task-defined-but-not-in-beat-schedule

## Summary
A Celery task defined in `tasks.py` but absent from `Smartenplus/celery.py` `beat_schedule` silently never runs. No error — it just never fires. Counter accumulates since launch, rollups never happen.

## Why It Matters
Celery gives no signal for unscheduled tasks. `reset_daily_counter` was defined, correct, and never executed for months — `daily_counter` grew monotonically, `booked_count` never got the rollup. Code review + beat_schedule diff is the only detection.

## Detail
```python
# operators/tasks.py — defined
@shared_task
def reset_daily_counter(): ...

# Smartenplus/celery.py beat_schedule — MUST add
'reset-daily-counter': {
    'task': 'operators.tasks.reset_daily_counter',
    'schedule': crontab(hour=0, minute=30),  # offset from 00:00 precompute
},
```
Restart **Beat** (not just workers) — `DatabaseScheduler` syncs new entries on Beat startup. Code/prod drift: a task present in DB beat but not `celery.py` (or vice versa) means prod diverged from code.

## Constraints / Gotchas
- Offset the crontab from other heavy tasks (avoid 00:00 collision with precompute bursts on small instances).
- If the task mutates a counter (`F('x') + F('y')`), audit accumulated values + cap before enabling — monotonic growth may have inflated data since launch.

## Related
- [[precompute-popular-contracts-fix-plan]] — BUG 2 source
- [[celery-unregistered-task-stale-worker]] — related Celery gotcha (stale worker, not scheduling)
- [[celery-tasks]] — general Celery patterns
