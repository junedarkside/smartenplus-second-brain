# ISR Stale Data Audit — Trip Detail Page

## Summary

Next.js ISR `revalidate: 300` broken in Docker standalone. No background worker to fire timer. Admin update → Redis clears → ISR HTML never notified. On-demand revalidation API route proposed as fix.

## Root Cause

ISR fires on-request-after-staleness. No background worker to proactively revalidate. Admin update → Redis cache clears → **ISR HTML cache never notified**. Pages serve stale until next traffic.

## Team Findings

- **19 ISR pages site-wide** (10s–86400s revalidate)
- **Celery, not bare thread** — already configured, use `trigger_isr_revalidation(slug)` task
- **Network path** — public URL works across separate Docker compose projects
- **CSR overlay covers:** ratecard, start/end dates, stop_sale_dates, is_actived, operational_days ✅
- **Stale regardless:** name, description, route_info, images, timeline, JSON-LD schemas, meta tags ❌

## Decision

Option A (on-demand revalidation) selected. 1 file frontend + 30 lines backend + Celery task.

## Implementation

See atomic notes:
- [[docker-standalone-isr-revalidate-gap]]
- [[on-demand-revalidation-api-route]]
- [[celery-task-over-bare-thread-django-signals]]
- [[isr-csr-overlay-stale-fields]]

## Deployment Order

1. Frontend first — `pages/api/revalidate.js` (idle until backend wires in, zero risk)
2. Backend second — add Celery task, wire to signal, deploy
3. Verify — admin edits contract → ISR page updates on next visit (seconds, not hours)