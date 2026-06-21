---
name: prod-capacity-celery-audit
description: Prod-capacity audit of the small EC2 box — web 2-slot + celery 1-serial both at floor; 24 celery tasks/7 apps; sync_pending_charges is the heaviest recurring blocker; beat schedule lives in prod DB (DatabaseScheduler) not code. Fix for both tiers = bigger instance, not a flag.
metadata:
  type: knowledge
  status: active
  date: 2026-06-21
  source: source-verified (smartenplus-backend, docker-compose-rds.yml = prod)
---

# Prod-Capacity / Celery Audit

> **Source-verified 2026-06-21.** Surfaced while answering "EC2 too small → why poll?" for CS ([[cs-architecture-decision]]). Production = `docker-compose-rds.yml`.

## TL;DR

The small prod box is **capacity-constrained on the worker tier as much as the web tier.** Both are at floor:
- **Web:** 2 Gunicorn slots (`--workers 1 --threads 2`), 256MB cap.
- **Celery:** 1 worker, `--concurrency=1` = ONE task at a time (serial queue), 150MB child-recycle.

The only lever that relieves either is a **bigger instance** — no config flag adds capacity without more RAM. If the site feels slow under load, the likely culprit is the single worker stalling behind `sync_pending_charges`, not the web tier.

## Topology (docker-compose-rds.yml)

| Service | Config | line | Constraint |
|---|---|---|---|
| web (gunicorn) | `--workers 1 --threads 2 --timeout 30`, `mem_limit 256m` | :13-14 | 2 concurrent requests |
| celery-worker | `--concurrency=1 --prefetch-multiplier=1 --max-memory-per-child=150000`, `mem_limit 256m` | :57,:80 | 1 serial task, recycle at 150MB RSS |
| celery-beat | `celery beat` | :94 | scheduler only |
| redis | `maxmemory 100mb allkeys-lru --save ""` | :49 | tiny, evicting, no persistence |
| nginx | `mem_limit 64m`, no WS upgrade headers | :22-30 | — |

`scripts/run.sh` uwsgi:9000 = **dead** (nginx proxies web:8000 only).

## Task inventory — 24 tasks / 7 apps

| App | Task | Decorator notable |
|---|---|---|
| payments | `sync_pending_charges` | `time_limit=540` (9-min hard cap), max_retries=3 |
| products | `update_route_query_counts` · `clear_old_query_logs` · `precompute_contract_recommendations` · `precompute_popular_contracts` · `precompute_all_active_contracts` · `cleanup_expired_recommendation_cache` · `precompute_contract_on_create` · `get_cache_statistics` | precompute retries exp-backoff `60*(2^n)` / `30*(2^n)` |
| operators | `reset_daily_counter` · `soft_delete_expired_ratecards` · `revalidate_frontend_isr` | ISR revalidate (#129) |
| bookings | `send_review_invitation_emails` · `send_booking_data` · `send_booking_data_by_telegram` | SES + Telegram |
| cards | `fetch_forex_rates` | external API, retry_delay=300 |
| carts | `send_html_email_list` · `send_html_email` · `send_booking_confirmation_email` · `send_booking_email_success_telegram` · `send_email_success_telegram` · `cleanup_orphaned_cart_items` · `send_orphaned_cleanup_telegram` · `test_func` | SES + Telegram heavy |
| orders | (tasks.py present) | — |

## Scheduled load (⚠️ celery.py = FALLBACK, not authoritative)

**`CELERY_BEAT_SCHEDULER = django_celery_beat.schedulers:DatabaseScheduler`** (`settings.py:552`). The live schedule is in the **prod DB** (`django_celery_beat.PeriodicTask` table), NOT `celery.py`. The static `app.conf.beat_schedule` dict is fallback only. **You cannot audit true task cadence from the repo — read the prod DB.** (This is the #134 code/prod drift.)

Code-fallback schedule (verify against prod DB):

| Task | Fallback cadence | Load |
|---|---|---|
| `payments.sync_pending_charges` | **every 10 min** | **heaviest** — 9-min cap, Omise call per pending charge |
| `products.get_cache_statistics` | every 30 min | light |
| `products.precompute_popular_contracts` | every 6h | fans ≤100 children, skip-if-fresh → mostly near-zero |
| `products.cleanup_expired_recommendation_cache` | 3 AM daily | moderate |
| `bookings.send_review_invitation_emails` | 8 AM daily | SES loop |
| `products.update_route_query_counts` | weekly Mon 00:30 | no retry, no index on QueryLog (debt) |
| `cards.fetch_forex_rates` | (prod-DB only) | external API |

## Three real findings

1. **Single worker is the actual bottleneck (not Gunicorn).** `--concurrency=1` = every task serial. `sync_pending_charges` (9-min cap, every 10 min) can occupy the worker ~90% of a window during payment spikes; all other tasks (email, precompute, forex, Telegram) queue behind it. Same single-worker constraint that ruled out Supabase two-write for CS chat ([[cs-architecture-decision]] R1).

2. **No memory headroom to add concurrency via flag.** Worker recycles at 150MB RSS inside a 256MB cap. A 2nd worker process needs ~another 150MB the box doesn't have. **Adding `--concurrency=2` would OOM.** Real fix = bigger instance.

3. **Schedule lives in prod DB, not code.** DatabaseScheduler means repo audit is incomplete; the true cadence + any extra registered tasks (`daily_counter`/`reset_daily_counter` registered in prod DB only — drift) require reading `django_celery_beat.PeriodicTask` in prod.

## Known deferred debt (master-state TASK-1VCPU-MONITOR)
- `update_route_query_counts` — no retry + no index on `QueryLog.query_time`
- `daily_counter`/`reset_daily_counter` — registered prod-DB only, not in `celery.py` (code/prod drift)
- CloudWatch CPU-credit drain monitoring (burstable vCPU) — verify post-#139

## Recommendation
- **Instance-size up is the only real lever** for both web + worker tiers. Quantify before/after with CloudWatch CPU-credit balance + worker queue depth.
- Before scaling, **read prod `django_celery_beat.PeriodicTask`** to confirm true schedule (repo is fallback).
- Cheap mitigations independent of instance size: index `QueryLog.query_time`; ensure `sync_pending_charges` can't pile (already has 9-min cap < 10-min schedule).

## Related
- [[cs-architecture-decision]] — same small-box constraint (why CS uses polling, not WS/Supabase)
- [[master-state|Master State]] — TASK-1VCPU-MONITOR loose end
- [[update-route-query-counts-audit]] · [[celery-unregistered-task-stale-worker]]
