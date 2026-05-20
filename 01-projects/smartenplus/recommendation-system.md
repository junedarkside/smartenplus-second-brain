# Recommendation System

## Summary
Product recommendation pre-computation via Celery. Contracts pre-compute 4 recommendation types × 3 limits, cached in Redis with 24h TTL. Signal-based warmup on contract creation. Hourly + nightly batch recomputation.

---

## Recommendation Types

| Type | Description |
|------|-------------|
| `similar` | Similar contracts by route/operator |
| `alternatives` | Alternative options |
| `packages` | Package deals |
| `hybrid` | Hybrid scoring algorithm |

**Cache limits:** 8, 12, 20 results per type.

---

## Tasks

### Signal-Based: `precompute_contract_on_create(contract_id)`
Triggered on `Contract` creation (via signals). Warms cache for new contracts immediately.

Cache keys warmed: `hybrid:8`, `hybrid:12`, `similar:8`. Standard 15-min TTL.

---

### Hourly: `precompute_popular_contracts()`
Processes top 100 contracts where `booked_count ≥ 50` OR `daily_counter ≥ 10`.

Queues individual `precompute_contract_recommendations(contract_id)` tasks.

---

### Nightly 2am: `precompute_all_active_contracts()`
Batch processes all active contracts in batches of 50. Ensures cache is warm for all contracts by morning.

---

### Weekly: `update_route_query_counts()`
Aggregates `QueryLog` (last 1 week) → `Route.query_count`. Updates popularity tracking for all routes.

After run: calls `clear_old_query_logs()` asynchronously.

---

### Daily 3am: `cleanup_expired_recommendation_cache()`
Maintenance placeholder. Redis handles TTL automatically. Placeholder for custom cleanup if needed.

---

### Maintenance: `clear_old_query_logs()`
Deletes `QueryLog` records older than 1 week.

---

### Monitoring: `get_cache_statistics()`
Samples up to 100 active contracts, checks `recommendations:{id}:hybrid:8` cache key presence. Returns `{total_contracts, cached_contracts, cache_hit_rate, sample_size}`.

---

## Cache Key Format

```
recommendations:{contract_id}:{rec_type}:{limit}
```

Example: `recommendations:42:hybrid:12`

TTL: 24h (pre-computed), 15min (on-demand).

---

## Popular Routes Admin Dashboard

Read-only analytics page showing route popularity by query count. Consumes `GET /admin-dashboard-routes/home/`.

### Backend

- **View:** `HomeViewSet` in `products/views.py` — annotates `lowest_price` (min active contract price) + `operator_count` (distinct operators with active contracts). Filters contracts by `is_active=True`.
- **Serializer:** `HomeSerializer` in `products/serializers.py` — fields: `slug`, `query_count`, `lowest_price`, `operator_count`.
- **Beat:** weekly `update-route-query-counts` in `celery.py` — aggregates `QueryLog` (last 7 days) → `Route.query_count`.
- **Migration:** `0008_add_query_count_index.py` — `db_index=True` on `Route.query_count` for sort performance.

### Admin Dashboard

- **Page:** `pages/routemanagement/popular-routes/index.js` — DataGrid, server-side pagination, sorted by `query_count` desc. Columns: rank, route (departure → arrival), query count, lowest price, operator count. Mobile-responsive column reduction.
- **API:** `getPopularRoutes` endpoint in `store/api/routesApi.js` — `GET /admin-dashboard-routes/home/` with `page` + `page_size` params.
- **Nav:** Route Management → Popular Routes (`TimelineOutlined` icon), between Routes and Trips.

## Related
- [[operators]] (Contract model)
- [[celery-tasks]] (celery task patterns)
- [[admin-dashboard]] (admin dashboard overview)