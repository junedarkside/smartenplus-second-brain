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

## 3-Tier Empty-Page Model (gsc-investigation 2026-06-05)

For ISR pages with potentially-empty inventory, use a three-tier protection (NOT blanket `notFound: true`):

| Tier | Condition | Response | Revalidate |
|------|-----------|----------|------------|
| 1 | Route not in DB | `notFound: true` (404) | 300 |
| 2 | Route exists, zero active schedules | 200 + `noindex: true` (thin content) | 3600 |
| 3 | Active inventory | Fully indexed | 3600 |

Backend must distinguish: 404 for nonexistent, 200 `{routes: [], route_exists: true}` for empty. See [[tiered-empty-page-noindex-strategy]] for full pattern. **Catch blocks must NEVER return `{notFound: true}`** — see [[never-notfound-in-catch-block]].

**Production timeout requirement:** `getStaticProps` `fetchData()` needs explicit 8s timeout when `fallback: 'blocking'` is enabled, else slow API = 500 cascade. See [[getstaticprops-fetch-timeout-isr-blocking]].

## Related
- [[docker-standalone-isr-revalidate-gap]]
- [[on-demand-revalidation-api-route]]
- [[tiered-empty-page-noindex-strategy]]
- [[never-notfound-in-catch-block]]
- [[getstaticprops-fetch-timeout-isr-blocking]]
- [[nextjs-patterns]]