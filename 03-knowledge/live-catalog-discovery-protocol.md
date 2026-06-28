# Live-Catalog Discovery Protocol

## Summary
Step-by-step recipe for enumerating the SmartEnPlus live production catalog across sitemap, public APIs, and admin DB. Three independent layers, converged into a gap matrix.

## Context
Live site at https://www.smartenplus.co.th. Audit started 2026-06-28 for transportation (Join/Private/Charter) + Experiences + Activities coverage gap analysis. See [[products-live-catalog-audit]].

## Details

### Step 1 — Sitemap (single fetch)
```
GET https://www.smartenplus.co.th/sitemap.xml
```
Server-generated via `pages/server-sitemap.xml/index.js`. Yields paired `/locations/{slug}` + `/destinations/{slug}` per [[locations-destinations-product-split]]. Gives complete station list + union of published pages. Respect filter rules in [[sitemap-filter-by-inventory-or-recency]].

### Step 2 — Public APIs (polite, 1 req/sec, cache locally)

| Endpoint | Returns |
|---|---|
| `/locations/?summary=true&has_trips=true` | Alphabetical station list |
| `/locations/?has_trips=true&destinations_page=true` | Destinations with route counts |
| `/contract/?service_category={X}` | Contracts per category (10 choices) |
| `/front-page/` | Homepage payload — `popular_experiences[]` (8 items, `-booked_count`) + `airport_routes[]` |

10 service_category values: TRANSPORTATION, TRANSFER, DAY_TOUR, MULTI_DAY_TOUR, SPA_WELLNESS, EVENT_TICKET, ATTRACTION_TICKET, FOOD_DINING, ACCOMMODATION, OTHER.

Cache responses locally. Never re-hit within same session.

### Step 3 — Admin DB (prod read-only Django shell)

```python
from django.db.models import Q, Count
from django.utils import timezone
from operators.models import Contract
from products.models import Route, Station

stations = Station.objects.values('station_name', 'station_type', 'iata_code')

routes = Route.objects.filter(is_actived=True).values(
    'departure_station__station_name',
    'arrival_station__station_name',
    'query_count',
)

contracts = Contract.objects.filter(
    Q(is_actived=True) & (Q(end_date__isnull=True) | Q(end_date__gt=timezone.now()))
).values(
    'service_category', 'contract_type',
    'trip__route__departure_station__station_name',
    'trip__route__arrival_station__station_name',
    'operator__operator_name',
)

# Coverage pivot — route × contract_type
coverage_pivot = contracts.values(
    'trip__route__departure_station__station_name',
    'trip__route__arrival_station__station_name',
    'contract_type',
).annotate(count=Count('id'))

# Activity hub pivot — service_category × departure_station
activity_pivot = contracts.values(
    'service_category',
    'trip__route__departure_station__station_name',
).annotate(count=Count('id'))
```

### Step 4 — Cross-reference matrix

Three layers per (location / route / activity):

| Layer | Source | Tells us |
|---|---|---|
| Reference | Curated location set | What *should* exist |
| Live | sitemap + APIs | What we *actually* sell |
| Admin | Django shell | What operators *have loaded* |

**Gap** = Reference yes, Live no. **Sub-gap** = Admin yes, Live no.

## Decision
Use 3-layer matrix + 5-lens coverage tagging (Join/Private/Charter/Experiences/Activities). One gap entry can have multiple lens statuses — e.g. route has Join covered but Charter missing.

## Tradeoffs

- **Public APIs only**: Lower infra access, stable schemas. Misses operator-only Contracts (admin layer exposed via Django shell).
- **Sitemap over HTML crawl**: Sitemap is server-generated, stable, complete. HTML changes break extraction.
- **Django shell over ORM dump**: Live queries, freshest data, no stale exports.

## Field gotchas (assert in audit script)

- `is_actived` (with 'd') on Route/Trip/Contract → see [[django-is-actived-vs-is-active-field-name-gotcha]]
- `station_type='airport'` filter — see [[station-type-airport-first-class-iata-restriction]]
- `service_category=TRANSFER` independent of airport filter — see [[transfer-category-vs-airport-filter-independence]]

## Related
- [[sitemap-filter-by-inventory-or-recency]]
- [[locations-destinations-product-split]]
- [[transportation-category-audit]]
- [[three-layer-gap-coverage-matrix]]
- [[thailand-location-coverage-framework]]
- [[operator-outreach-question-template]]
- [[products-live-catalog-audit]]