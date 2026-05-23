# ISR CSR Overlay — Stale Fields

## Summary

Trip detail pages use ISR (5min) + CSR overlay. CSR covers some fields. Others stay stale.

## CSR Overlay — Covered ✅

`useCheckContractQuery` refreshes on mount:
- `ratecard`
- `start_date`
- `end_date`
- `stop_sale_dates`
- `is_actived`
- `operational_days`

## Stale Regardless — No CSR Fallback ❌

- Product name
- Description
- Route info
- Images
- Timeline
- Operator name
- Policies
- JSON-LD schemas (Product, TouristTrip, BreadcrumbList, FAQPage, LocalBusiness, Organization)
- Meta tags, OpenGraph, canonical URL
- Twitter Card
- Breadcrumb path

## SEO Impact

Googlebot may index stale titles/descriptions/prices for:
- 5 min on trips pages (revalidate: 300)
- 1 hour on activities pages (revalidate: 3600)

## Fix

On-demand revalidation — admin save triggers Celery task → frontend `/api/revalidate` → ISR cache invalidated immediately.

See [[on-demand-revalidation-api-route]] + [[docker-standalone-isr-revalidate-gap]].

## Related
- [[docker-standalone-isr-revalidate-gap]]
- [[on-demand-revalidation-api-route]]
- [[nextjs-patterns]]