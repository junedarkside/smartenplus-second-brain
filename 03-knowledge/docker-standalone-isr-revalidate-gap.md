# Docker Standalone ISR Revalidate Gap

## Summary

Next.js ISR `revalidate: 300` broken in Docker standalone. No background worker to fire timer. Admin update → Redis clears → ISR HTML never notified.

## Problem

`/trips/detail/[slug]` uses ISR. After admin saves, page serves stale HTML for hours. Hard refresh doesn't help. Only redeploy clears Docker volume.

**Also confirmed on `/activities/detail/[...slug]` (2026-06-17, debug-mantra trace).** Same gap, worse window: `pages/activities/detail/[...slug].js:150` is `revalidate: 3600` (1h vs trips' 5min). User-reported symptom: admin updates contract in admin-dashboard, production activity page never reflects it. Full chain verified end-to-end this session:
- Admin PATCH → `operators/views.py:946` real `instance.save()` (the M2M/related writes above it use `.set()`/`.save()` on related rows, but the Contract itself genuinely saves) → `post_save` fires.
- `operators/signals.py:33` `cache.delete_pattern("product_detail_v1_{slug}_*")` deletes the exact key built at `products/views.py:858`. Redis bust = real (django_redis `DefaultClient` supports `delete_pattern`).
- Frontend ISR HTML never notified → stale. Backend is **innocent**; the missing bridge is the bug.
- Client RTK refetch does NOT save it: `DayTripDetailPage` skips the contract refetch when `preloadedContract` exists; only `reviews` refetch client-side. Contract/price/policy fields stay stale (matches [[isr-csr-overlay-stale-fields]]).

## Root Cause

ISR timer fires on-request-after-staleness. No background worker to proactively revalidate. Admin update → Redis cache clears → **ISR HTML cache never notified**. Pages serve stale until next traffic triggers revalidate.

## Architecture

```
Admin Dashboard → PATCH API → Django saves Contract
                              ↓
                      post_save signal
                              ↓
                  cache.delete_pattern (Redis) ✅ works
                              ↓
                  Next.js ISR cache ❌ never notified
                              ↓
                  Page serves stale HTML from Docker volume
```

## Docker ISR Setup

```
Dockerfile: COPY --from=builder /app/.next/standalone ./
           mkdir -p /app/.next/cache

docker-compose.prod.yml: volumes: next_cache:/app/.next/cache

deploy-ghcr.sh: docker volume rm smartenplus_next_cache ← cleared on deploy
```

Next.js 14.2.5 standalone mode. Volume mounts to `/app/.next/cache/`.

## Workaround

Deploy script clears `smartenplus_next_cache` Docker volume on every deploy. Forces fresh ISR on next visit.

## Side Finding — `daily_counter` Self-Save Trashes Backend Cache (2026-06-17)

`products/views.py:882-883` — every product-detail GET does `contract.daily_counter += 1; contract.save()`. That `.save()` fires the `post_save` signal → `cache.delete_pattern("product_detail_v1_{slug}_*")` on **every read**. Net effect: the 30-min Redis cache (`views.py:896`) is self-invalidated on each view, so backend caching for this endpoint is near-useless AND every page view spams the contract cache-invalidation signals (`contracts_*`, `recommendations_*`, etc.).

Not the cause of the stale-page bug (it makes backend *fresher*, sharpening ISR as the sole culprit), but it's a real perf smell: write-on-read + signal storm. Fix candidates: `update(daily_counter=F('daily_counter')+1)` (no signal, atomic) or move the counter off the hot path. Tech-debt flag.

## Fix

On-demand revalidation via API route. See [[on-demand-revalidation-api-route]] + [[celery-task-over-bare-thread-django-signals]].

**Note (2026-06-17):** the code in [[on-demand-revalidation-api-route]] is written App-Router but this repo is Pages Router — use `res.revalidate(path)`, not `request.revalidatePath`. Corrected snippet now in that note. Revalidate path for activities: `/activities/detail/${slug}`.

## Related
- [[on-demand-revalidation-api-route]]
- [[celery-task-over-bare-thread-django-signals]]
- [[isr-csr-overlay-stale-fields]]
- [[docker-production]]