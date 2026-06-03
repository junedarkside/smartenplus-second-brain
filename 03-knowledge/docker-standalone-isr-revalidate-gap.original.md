# Docker Standalone ISR Revalidate Gap

## Summary

Next.js ISR `revalidate: 300` broken in Docker standalone. No background worker to fire timer. Admin update → Redis clears → ISR HTML never notified.

## Problem

`/trips/detail/[slug]` uses ISR. After admin saves, page serves stale HTML for hours. Hard refresh doesn't help. Only redeploy clears Docker volume.

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

## Fix

On-demand revalidation via API route. See [[on-demand-revalidation-api-route]] + [[celery-task-over-bare-thread-django-signals]].

## Related
- [[on-demand-revalidation-api-route]]
- [[celery-task-over-bare-thread-django-signals]]
- [[isr-csr-overlay-stale-fields]]
- [[docker-production]]