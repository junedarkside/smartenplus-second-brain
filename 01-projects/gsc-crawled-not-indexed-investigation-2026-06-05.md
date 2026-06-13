# GSC Crawled-Not-Indexed Investigation 2026-06-05

## Summary
Multi-session investigation into 52,400 URLs "Crawled – Currently Not Indexed" on smartenplus.co.th. Three specialist teams run. Root causes identified, safe fix order established. No code deployed yet — data collection required first.

## Context
Google Search Console shows 52,400+ pages crawled but refused indexing. Initial dev team conclusion (URL pollution = primary cause) overturned by adversarial specialist review. Real primary cause is thin/empty ISR pages + structural duplicates.

## Problem

Five root causes ranked by confidence:

| Rank | Cause | Confidence |
|------|-------|------------|
| 1 | Empty inventory trip pages returning 200 OK, no noindex, cached by ISR | 88/100 |
| 2 | `/locations/` + `/destinations/` dual-URL structure, no cross-canonical | 72/100 |
| 3 | URL pollution (fbclid, utm_*, double params) consuming crawl budget | 65/100 |
| 4 | Sitemap pollution (non-indexable pages: `/dev/`, `/account/`, `/bookings`) | 60/100 |
| 5 | Thin blog tag pages, trailing slash inconsistency | 45/100 |

## Critical Finding: `notFound: true` is DANGEROUS

**Do NOT deploy blanket `notFound: true` when `routes.length === 0`.**

Reason: **14 of 62 proven popular routes involve Koh Lipe** (confirmed in `helpers/routeConstants.js`). Koh Lipe ferries close May–October (monsoon). `notFound: true` in June → Google deindexes by July → peak season opens October → no indexed pages → competitor takes position 3 for "hat yai to koh lipe ferry" permanently.

### Five Inventory States — Correct Treatment

| State | Treatment |
|-------|-----------|
| Route does not exist in DB | `notFound: true` — safe, no equity at stake |
| Route exists, zero schedules today | `noindex: true` on page — preserve link equity, fast recovery |
| Operator temporarily suspended | Keep page + banner notice — never 404 |
| Seasonal route (Koh Lipe monsoon) | Keep indexed year-round with seasonal messaging |
| API failure / timeout | Return stale props — **NEVER `notFound` in catch block** |

### Three-Tier Model (correct architecture, needs backend change)

- **Tier 1** — Route pair not in DB → `notFound: true` (only after backend returns HTTP 404)
- **Tier 2** — Route exists, zero active schedules → 200 + `noindex: true` + `revalidate: 3600`
- **Tier 3** — Route exists + active inventory → fully indexed (current behavior)

**Blocker:** Django API currently returns `{ routes: [] }` for BOTH Tier 1 and Tier 2. Frontend cannot distinguish them without backend change. Required: Django returns HTTP 404 for nonexistent pairs, HTTP 200 `{ routes: [], route_exists: true }` for existing-but-empty.

### API Failure Rule (CRITICAL)
```js
// NEVER in catch block:
return { notFound: true }  // ← destroys ISR cache during Django restart

// ALWAYS in catch block:
return { props: { data: [], error: '...' }, revalidate: 30 }
```

## Decision — Safe Implementation Order

### Phase 0 — Data Collection (no code changes, 2 days)

Required before ANY production change:

**1. GSC baseline** — GSC → Performance → filter `/trips/` → export. Count pages with impressions currently.

**2. Seasonal gap SQL:**
```sql
SELECT DISTINCT dep.location_id, arr.location_id, MAX(t.end_date) AS last_inventory_date
FROM trips_trip t
JOIN stations_station dep ON t.departure_station_id = dep.id
JOIN stations_station arr ON t.arrival_station_id = arr.id
WHERE NOT EXISTS (
  SELECT 1 FROM trips_trip t2
  WHERE t2.departure_station_id = t.departure_station_id
    AND t2.arrival_station_id = t.arrival_station_id
    AND t2.end_date >= NOW()
)
GROUP BY dep.location_id, arr.location_id
HAVING MAX(t.end_date) > NOW() - INTERVAL '180 days';
```
If >20 routes returned → seasonal risk is material. Do not deploy notFound without protection.

**3. Critical cross-reference** — GSC impressions last 90 days × zero current inventory. Any route in both = confirmed business risk. Exclude from any 404/noindex policy.

**4. Truly dead routes:**
```sql
SELECT dep_slug, arr_slug FROM routes
WHERE last_inventory_date < NOW() - INTERVAL '365 days' OR last_inventory_date IS NULL;
```
Only these (+ zero GSC impressions) are safe `notFound` candidates.

**5. API error rate in prod logs** — catch block hit rate. If >0.5% of `getStaticProps` calls → `notFound` in catch would cause measurable deindexation from infra failures.

### Phase 1 — Sitemap filter (1 hour, lowest risk, deploy first)

Filter `generateRoutesSitemap()` in `pages/server-sitemap.xml/index.js`:
```js
const activeRoutes = allRoutes.filter(route =>
  route.avaliable_routes_count > 0 ||
  new Date(route.updated_at) > new Date(Date.now() - 365 * 24 * 60 * 60 * 1000)
);
```
**Why first:** Removing from sitemap does NOT deindex already-indexed pages. Stops feeding Googlebot new thin URLs. Fully reversible.

Requires backend endpoint to return `avaliable_routes_count` or `updated_at` — verify before deploying.

**Go/no-go for Phase 2:** Wait 2–3 weeks. Confirm GSC crawl stats show reduced thin-page discovery.

### Phase 2 — noindex for confirmed dead routes only (2 weeks after Phase 1)

Apply `noindex: true` ONLY to routes where:
- Zero inventory for 12+ months (SQL query above)
- Zero GSC impressions in last 90 days

Change `seoConfig.js` line 41 from hardcoded `noindex: false` to accept prop:
```js
noindex: props.noInventory === true
```
Pass `noInventory: true` from `getStaticProps` when route is confirmed dead.

**Not a blanket noindex.** Surgical only.

**ISR gotcha:** Must clear `smartenplus_next_cache` Docker volume on deploy (per CLAUDE.md). Otherwise noindex tag persists on cached pages for days.

### Phase 3 — Three-tier model with backend change (4+ weeks after Phase 2 stable)

Only after:
- Backend deploys `route_exists` field or HTTP 404 for nonexistent pairs
- Phase 2 stable for 2+ weeks with zero indexed-page regression

```js
const res = await fetch(routeUrl);
if (res.status === 404) {
  return { notFound: true, revalidate: 300 }; // Tier 1 only
}
if (!res.ok) {
  return { props: { data: [], error: '...' }, revalidate: 30 }; // API failure — never notFound
}
const response = await res.json();
if (!response?.routes?.length) {
  return { props: { data: [], noInventory: true }, revalidate: 3600 }; // Tier 2
}
// Tier 3 — has inventory, current behavior
```

Add kill-switch env var:
```js
const ENABLE_TIER1_NOTFOUND = process.env.ENABLE_TIER1_NOTFOUND === 'true';
```
Allows instant rollback via env var without code deploy.

## Confidence Scores Per Recommendation

| Recommendation | Confidence |
|----------------|------------|
| Sitemap filter only, no page changes | 82/100 |
| noindex for empty pages (no 404) — surgical | 61/100 |
| `notFound: true` for ALL empty pages | 11/100 — DO NOT DEPLOY |
| Three-tier model with backend API change | 74/100 |
| Do nothing, collect data first | 58/100 |

## Tradeoffs

**notFound: true (blanket):**
- Pro: cleanest signal to Google, recaptures crawl budget
- Con: destroys seasonal route rankings every monsoon season, API failure risk, 2–6 month ranking recovery time

**noindex (surgical):**
- Pro: preserves link equity, fast recovery when inventory returns, no UX degradation
- Con: Google still crawls noindex pages (crawl budget partially wasted), requires accurate dead-route data

**Sitemap filter only:**
- Pro: zero deindexation risk, stops new thin-page submission
- Con: doesn't fix already-crawled thin pages, Google keeps recrawling them

## Key Files

| File | Relevance |
|------|-----------|
| `pages/trips/[...slug].js:99–101` | Empty inventory returns thin 200 — root cause |
| `helpers/routeConstants.js` | 14 Koh Lipe routes = seasonal risk |
| `pages/server-sitemap.xml/index.js` | `generateRoutesSitemap()` submits all routes unfiltered |
| `components/SEO/seoConfig.js:41` | `noindex: false` hardcoded — needs to accept prop |
| `hooks/useRouteSeo.js:12` | Canonical strips query strings correctly (not the bug) |
| `public/robots.txt` | Missing `Disallow: /_next/image` — low priority |

## Related

- [[locations-destinations-product-split]] — confirmed different products, never consolidate
- [[production-url-rename-cost-framework]] — URL cost framework
- [[docker-standalone-isr-revalidate-gap]] — ISR Docker volume clear requirement
- [[isr-csr-overlay-stale-fields]] — ISR caching behavior patterns
- [[structured-data-schema-patterns]] — server-sitemap.xml crawl budget patterns

## Related Atoms (Extracted 2026-06-13)
- [[tiered-empty-page-noindex-strategy]] — 3-tier: notFound:300 / noindex:3600 / fully indexed
- [[never-notfound-in-catch-block]] — ISR catch must never return `{notFound: true}`; serves stale props
- [[sitemap-filter-by-inventory-or-recency]] — pre-flight filter: `available_routes_count>0 || updated_at>365d`
