# API Mirroring Pattern for New Features

## Summary
New data variant on existing endpoint: mirror fetch method with filtered queryset. `_fetch_X_data` naming. Reuse existing serializer. No new endpoints.

## Context
`airport-transfer-redesign-2026.md` (2026-05-30). Backend added `_fetch_airport_routes_data()` mirroring `_fetch_home_routes_data()`.

## Problem
Old airport transfer section: station grid (name only, no routes, no prices). Zero booking intent. Options:
- A: Static hardcoded routes — prices stale, maintenance burden
- B: Filter `home_routes` client-side — brittle, station_type not guaranteed
- C: New `airport_routes` key in FrontPage API — **chosen**

## Decision

### Pattern: `_fetch_X_data` Method
```python
# FrontPageViewSet (pages_info/views.py)

def _fetch_home_routes_data(self, request, parsed_query_limit):
    # Existing method
    queryset = Route.objects.filter(...)
    return queryset[:parsed_query_limit]

def _fetch_airport_routes_data(self, request, parsed_query_limit):
    # New method — mirrors structure
    queryset = Route.objects.filter(
        departure_station__station_type='airport'
    ).filter(
        # must have active Trip + active non-expired Contract
    ).annotate(
        lowest_price=Subquery(...),
        operator_count=Count(...)
    ).order_by('-query_count')
    return queryset[:parsed_query_limit]
```

### Add to list() response
```python
response_data["airport_routes"] = self._fetch_airport_routes_data(request, parsed_query_limit)
```

### Reuse Existing Serializer
Uses `HomeSerializer` — same shape as `home_routes`. No new serializer.

### Frontend Consumption
```jsx
// homepagev2.js
const airportRoutes = frontPageData?.airport_routes;

// AirportTransferSection.js props
<AirportTransferSection airportRoutes={airportRoutes} error={error} />
```

## Details

### Filtering Requirements
- `departure_station__station_type='airport'` — station type filter
- Active Trip + active non-expired Contract — operational validity
- `lowest_price` via Subquery on Contract_RateCard — price anchor
- `operator_count` — trust signal
- Order by `-query_count` — most popular first
- Default limit: 4

### Reuse Audit (Airport Transfer)
| Asset | Reused From | Notes |
|-------|-------------|-------|
| `HomeSerializer` | `products/serializers.py` | Same shape as home_routes |
| `Section`, `ContentCard` | `components/common/` | Unchanged |
| `capitalizeWords` | `helpers/textDecoration.js` | |
| `isGTMEnabled`, `sendGTMEvent` | `helpers/gtmUtils.js` | GTM pattern from PopularRoutesSection |
| `formatPrice` | Inline (pattern from PopularRouteImageCard) | 7 lines |

### Tech Debt: 0
- No hardcoded data
- No new serializers
- No new endpoints
- No new dependencies
- Component size <60 lines each

## Tradeoffs
- Single method vs. separate endpoint — API surface stays small
- Shared cache TTL (300s) — airport prices may need shorter TTL if volatile
- ISR refreshes every 60s — acceptable for homepage discovery

## Consequences
- Frontend gets dedicated `airport_routes` array — no client-side filtering
- Backend cache reusable — same frontpage cache TTL
- Pattern repeatable for other station types (e.g., `port_routes`, `bus_station_routes`)

## Related
- [[nextjs-patterns]] — ISR patterns
- [[airport-transfer-redesign-2026]] — full redesign doc