# api.smartenplus.co.th — Public API Endpoint Inventory

## Summary
Canonical reference for SmartEnPlus public REST API endpoints (production). Verified 2026-06-28 during [[products-live-catalog-audit]] Phase 1.

## Context
Inventory built for catalog audit work. Frontend source of truth: `helpers/constants.js:29` — `baseURL = process.env.NEXT_PUBLIC_API_URL` → resolves to `https://api.smartenplus.co.th` on prod.

## Details

### Verified endpoints (HTTP 200, 2026-06-28)

| Endpoint | Returns | Notes |
|---|---|---|
| `GET /locations/?summary=true&has_trips=true&limit=256` | Location summary list (route/trip/station counts) | Used by `/locations` index |
| `GET /locations/?has_trips=true&destinations_page=true` | Destination shape (stations with route counts) | Used by `/destinations` index |
| `GET /contract/` | All contracts paginated (count=1224, page_size=10 default) | Total across all service_category |
| `GET /contract/?service_category={X}&page_size=100` | Filtered by service_category | 10 valid values |
| `GET /contract/?service_category=TRANSPORTATION&page=N&page_size=100` | Paginated | 1191 total, 12 pages |
| `GET /front-page/` | Homepage payload | 8 keys: hero_banners, locations, home_routes, categories, top_reviews, stations, airport_routes, popular_experiences |

### Service category enum (10 values)

| Value | Live count (2026-06-28) |
|---|---|
| TRANSPORTATION | 1191 |
| TRANSFER | 0 |
| DAY_TOUR | 29 |
| MULTI_DAY_TOUR | 0 |
| SPA_WELLNESS | 4 |
| EVENT_TICKET | 0 |
| ATTRACTION_TICKET | 0 |
| FOOD_DINING | 0 |
| ACCOMMODATION | 0 |
| OTHER | 0 |

Total: 1224.

### Contract record schema (top-level fields)

```
id, slug, operator, trip, type, duration, tour_duration_days,
advance_hr, extra, ratecard, transport_composit, image,
checkin_info, info_fields, cancellation_policy, timeline,
route_info, stop_sale_dates, general_information, all_info,
all_info_by_operator, cancellation_policies, baggage_policy,
is_actived, score, average_rating, review_count, booked_count,
name, service_category, service_category_display,
booking_count_30d, booking_count_yesterday,
instant_confirmation, mobile_ticket_enabled, operational_days
```

### What is NOT exposed (admin-only)

- **Station FK IDs** (only `trip` integer + parseable name string)
- **query_count** (Route demand signal)
- **end_date field** (filtering silently ignored)
- **is_actived=false result set** (filter ignored — see [[public-api-filter-silent-ignore]])
- Operator FK beyond name (only operator_name + slug)
- Internal admin flags

## Decision
Use these endpoints for Live-layer catalog audit work. Do NOT rely on admin-style filters (`?is_actived=`, `?end_date__gte=`) — they silently ignore. Use Django shell for any Reference/Admin layer work.

## Tradeoffs

- **Pro:** Stable endpoints, predictable schema, public access
- **Pro:** 1 req/sec polite scraping is fine (no rate limiting observed)
- **Con:** No station FK pivot → route gap analysis is name-string-based, approximate
- **Con:** Admin filters ignored → cannot detect sub-gaps

## Related

- [[live-catalog-discovery-protocol]]
- [[public-api-filter-silent-ignore]]
- [[transportation-category-audit]]
- [[products-live-catalog-audit]]
- [[vault-protocol]]