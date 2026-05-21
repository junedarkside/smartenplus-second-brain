# Recommendation System

## Summary
Pre-computation via Celery. 4 recommendation types × 3 limits, cached in Redis (24h TTL). Signal warmup + hourly/nightly batch.

## Recommendation Types

| Type | Description |
|------|-------------|
| `similar` | Similar contracts by route/operator |
| `alternatives` | Alternative options |
| `packages` | Package deals |
| `hybrid` | Hybrid scoring algorithm |

**Cache limits:** 8, 12, 20 results per type.

## Tasks

### Signal: `precompute_contract_on_create(contract_id)`
On Contract creation. Warms `hybrid:8`, `hybrid:12`, `similar:8`. 15-min TTL.

### Hourly: `precompute_popular_contracts()`
Top 100 contracts (`booked_count ≥ 50` OR `daily_counter ≥ 10`). Queues individual tasks.

### Nightly 2am: `precompute_all_active_contracts()`
All active contracts in batches of 50.

### Weekly: `update_route_query_counts()`
Aggregates `QueryLog` (last 7 days) → `Route.query_count`.

### Daily 3am: `cleanup_expired_recommendation_cache()`
Placeholder. Redis handles TTL automatically.

### Maintenance: `clear_old_query_logs()`
Deletes `QueryLog` records >1 week.

### Monitoring: `get_cache_statistics()`
Samples 100 active contracts, checks cache key presence. Returns `{total_contracts, cached_contracts, cache_hit_rate, sample_size}`.

## Cache Key Format
`recommendations:{contract_id}:{rec_type}:{limit}`. TTL: 24h (pre-computed), 15min (on-demand).

## Popular Routes Admin Dashboard

Read-only analytics page. Route popularity by query count.

**Backend:** `HomeViewSet` in `products/views.py` — annotates `lowest_price` + `operator_count`. `HomeSerializer`: `slug`, `query_count`, `lowest_price`, `operator_count`.
**Admin:** `pages/routemanagement/popular-routes/index.js` — DataGrid, server-side pagination, sorted `query_count` desc.
**API:** `getPopularRoutes` in `store/api/routesApi.js` — `GET /admin-dashboard-routes/home/`.

## Related
- [[operators]]
- [[celery-tasks]]
- [[admin-dashboard]]
