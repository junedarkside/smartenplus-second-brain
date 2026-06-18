# Celery "Received Unregistered Task" = Stale Worker

## Summary

`KeyError: '<task path>'` + `Received unregistered task of type '<task path>'` means the **running
Celery worker started before that task existed in code**. Its task registry is stale. The web process
(newer code) enqueues the task → broker → old worker pops it → not in registry → **message discarded,
no retry**. Fix: **restart the worker.** Not a code bug.

## Symptom Signature

```
Received unregistered task of type 'operators.tasks.revalidate_frontend_isr'.
The message has been ignored and discarded.
...
KeyError: 'operators.tasks.revalidate_frontend_isr'
  File ".../celery/worker/consumer/consumer.py", line 642, in on_task_received
    strategy = strategies[type_]
```

## Why It Happens

`app.autodiscover_tasks()` (`Smartenplus/celery.py:21`) scans every app's `tasks.py` **once, at worker
boot**. Add or rename a `@shared_task`, and a worker already running never learns it. **Reloading the
web process is not enough — the worker is a separate process and must be restarted too.**

Rule: **any deploy / branch-switch that adds or renames a `@shared_task` requires a worker restart.**

## Silent Data Loss

Unregistered messages are **discarded, not retried**. A restart does not replay them. While a worker is
stale, every enqueue of the new task is lost. With ISR revalidation that means operator Contract/RateCard
edits silently skip their frontend revalidate call.

## This Incident (2026-06-18, local)

`revalidate_frontend_isr` shipped same day (#129, commit `0f2d108`). Local bare worker not restarted
after pull → the error above (origin `gen33983@MacBook-Air-5.local`). **Benign in dev**, triple-guarded:
1. Worker stale → discarded.
2. Even if registered: local `.env` sets no `REVALIDATION_SECRET` → default `''` (`settings.py:376`) →
   guard `tasks.py:70` `if not slug or not secret: return` no-ops the task.
3. Even if it ran: frontend routinely down during admin-dashboard testing → POST would fail anyway.

Nothing lost in dev; just log spam. Cleanup = restart worker.

## Local vs Production

- **Local dev = HIGH risk.** Worker is a bare process (`activate.sh`). `git pull` does NOT restart it.
  Manual restart required: `source deactive.sh && source activate.sh`.
- **Prod = SAFE with a normal deploy.** Worker is the `celery-worker` container
  (`docker-compose-deploy.yml:34`, `build:` from image). `docker compose up -d --build` recreates it →
  fresh process → task registered. **At-risk only** if someone restarts `web` alone and leaves the
  worker on the old image.
- **Verify prod:** (a) grep prod `celery-worker` logs for `unregistered task` after the deploy —
  present = recreate with `--build`; (b) confirm prod sets `REVALIDATION_SECRET` non-empty (else ISR
  silently never fires). `FRONTEND_URL` default `https://www.smartenplus.co.th` is correct (www, per
  [[frontend-url-canonical-www-not-apex]]).

## Not To Be Confused With (real code bugs)

Same/similar error, different cause — check these only after confirming the worker is current:
- Wrong `task=` name in `apply_async`/beat schedule (routing typo).
- Relative imports breaking the dotted task path.
- App not in `INSTALLED_APPS` so `autodiscover_tasks()` skips its `tasks.py`.

## Side Hardening (separate item)

`celery-worker` and `celery-beat` lack `restart: always` in `docker-compose-deploy.yml` — a worker
crash won't auto-recover.

## Related
- [[celery-task-over-bare-thread-django-signals]] — design-time twin (why Celery for signal side effects)
- [[on-demand-revalidation-api-route]] — the #129 endpoint this task POSTs to
- [[docker-standalone-isr-revalidate-gap]] — the ISR gap this whole feature closes
- [[frontend-url-canonical-www-not-apex]] — FRONTEND_URL must be www
- [[celery-tasks]] — bind/retry/beat patterns
