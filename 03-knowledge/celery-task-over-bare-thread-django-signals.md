# Celery Task Over Bare Thread for Django Signals

## Summary

Django signals should trigger side effects via Celery tasks, not bare threads. Bare threads have no retry/monitoring/backpressure and die with Django restart.

## Why Not Bare Thread

- No retry on failure
- No monitoring/observability
- No backpressure
- Die with Django restart
- No deduplication

## Why Celery

Celery already configured:
- `Smartenplus/celery.py` — Celery app
- `django_celery_results` + `django_celery_beat` in INSTALLED_APPS
- `celery-worker` + `celery-beat` services in `docker-compose-deploy.yml`
- Existing retry patterns in `bookings/tasks.py`

## Celery Task Pattern

```python
@shared_task(bind=True, max_retries=3, ignore_result=True)
def trigger_isr_revalidation(self, slug):
    """Trigger Next.js ISR revalidation for a contract slug."""
    from django.conf import settings
    import requests

    frontend_url = 'http://localhost:3000' if settings.DEBUG else 'https://smartenplus.co.th'
    revalidate_url = f"{frontend_url}/api/revalidate"

    try:
        response = requests.post(
            revalidate_url,
            json={"slug": slug},
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"ISR revalidation triggered for contract/{slug}")
    except Exception as e:
        logger.error(f"ISR revalidation failed for {slug}: {e}")
        raise self.retry(exc=e, countdown=60)
```

## Properties

- `bind=True` — access `self` for retry
- `max_retries=3` — fail-safe
- `ignore_result=True` — don't store result in DB
- Retry backoff: 60s
- Deduplication: slug-based task_id prevents rapid-save flood

## Signal Wiring

```python
# operators/signals.py
if instance.slug:
    trigger_isr_revalidation.delay(instance.slug)
```

## Network Path

Backend (separate Docker compose) → public URL `https://smartenplus.co.th`. Same pattern as `bookings/tasks.py:37`.

## Related
- [[docker-standalone-isr-revalidate-gap]]
- [[on-demand-revalidation-api-route]]
- [[celery-tasks]]