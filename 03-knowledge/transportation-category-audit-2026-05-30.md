# Transportation Category Audit — 2026-05-30

## Summary
Backend audit of SmartEnPlus transportation category structure to determine whether Airport Transfers justify dedicated homepage placement. Code-only — no live DB access. Hard inventory/booking numbers require Django shell queries. Scrutinize pass applied 2026-05-30 — 8 corrections documented below.

## Context
Built `AirportTransferSection.js` homepage section (commit `1eec0aa`) using `/front-page/` API. Question: architecturally justified or remove in favor of search-only discovery?

Redesign spec added 2026-05-30 — see [[#Redesign Spec — Professional Airport Transfer Section]] below.

---

## Category Architecture

### Three levels of classification

**Level 1 — Station Type** (`stations/models.py:32`)
`Station.station_type` CharField, **26 choices** (not 25 — motel, campground, helipad, parking_lot, rest_area, service_station present in model). Transport-relevant subset:

| station_type | Transport mode |
|---|---|
| `airport` | Airport transfer routes |
| `bus_station`, `bus_stop` | Bus |
| `train_station`, `metro_station`, `light_rail_station`, `subway_station` | Rail |
| `port`, `pier`, `ferry_terminal` | Ferry/water |
| `taxi_stand`, `rideshare_pickup` | Ground transfer |
| `hotel`, `hostel`, `resort`, `motel`, `bnb`, `guesthouse` | Accommodation endpoints |
| `beach`, `park`, `campground` | Leisure destinations |
| `helipad`, `parking_lot`, `rest_area`, `service_station`, `other` | Other |

**Airport is first-class.** IATA code field on Station restricted to `station_type='airport'` only (`stations/models.py:108`). Exact validation:
```python
if self.iata_code and self.station_type != 'airport':
    raise ValidationError({'iata_code': "IATA code can only be set for stations of type 'Airport'."})
```

**Level 2 — Contract Service Category** (`operators/models.py:296`)
`Contract.service_category` CharField, 10 choices:

```
TRANSPORTATION (default) | DAY_TOUR | MULTI_DAY_TOUR | SPA_WELLNESS
EVENT_TICKET | ATTRACTION_TICKET | FOOD_DINING | ACCOMMODATION | TRANSFER | OTHER
```

`TRANSFER` separate from `TRANSPORTATION`. **`TRANSFER` category and airport filter are independent** — see Filter Architecture Note below.

**Level 3 — Vehicle Type** (`operators/models.py:135`)
`VehicleType.vehicle_type` — free text, no enum. Examples: Bus, Van, Minibus, Ferry. No hardcoded "Airport Transfer" vehicle type at this level.

---

## How Airport Transfers Are Stored

Airport Transfer is **NOT a separate category or product type**. It is a **subset of transportation routes** identified by:

```
Route → departure_station → Station.station_type == 'airport'
```

Backend filter in `pages_info/views.py:330` (`_fetch_airport_routes_data`). Simplified — see actual file for full `.select_related()`, Subquery annotations, and Exists patterns:

```python
# Simplified. Full code: pages_info/views.py:330
Route.objects.filter(
    departure_station__station_type='airport'
).filter(
    Exists(Trip.objects.filter(route=OuterRef('pk')).values('id')[:1])
).filter(
    Exists(
        Contract.objects.filter(
            trip__route=OuterRef('pk'),
            is_actived=True,
        ).filter(Q(end_date__isnull=True) | Q(end_date__gt=today)).values('pk')[:1]
    )
).annotate(
    lowest_price=Subquery(...),  # Contract_RateCard, selling_rate > 0, allow_null=True
    operator_count=Count(...)
).order_by('-query_count')[:4]  # default limit hardcoded in _fetch_airport_routes_data
```

Routes returned: BKK, HKT, HDY, CNX → any destination.

**`lowest_price` can be null.** Annotation uses `allow_null=True`. Routes with no active rate cards still surface with `lowest_price=None`. Frontend (`AirportTransferRouteCard.js:39-44`) handles this — shows "Check price" fallback. Previous claim "only routes with selling_rate > 0 surface" was wrong: filter ensures `selling_rate > 0` for annotation only, not route inclusion.

**`query_count` ordering.** `query_count` incremented asynchronously by Celery task `update_route_query_counts()` (`products/tasks.py:12`), which counts QueryLog entries from past 1 week. Not real-time. Multiple routes with `query_count=0` (new/unpopular) return in non-deterministic order — no secondary sort field in current implementation.

### Filter Architecture Note

Airport filter (`departure_station__station_type='airport'`) and `Contract.service_category='TRANSFER'` are **completely independent**:

- Route departing from airport with `service_category='TRANSPORTATION'` (not TRANSFER) **will** appear
- `TRANSFER` contract on non-airport departure station **will NOT** appear
- Code never checks `service_category` in `_fetch_airport_routes_data`

TRANSFER category existence is not architectural justification for homepage section. Justification is `station_type='airport'` being first-class.

### Arrival-Only Routes Not Covered

Filter only checks `departure_station__station_type='airport'`. Inbound transfers (hotel → airport) not surfaced. Section title "Airport Transfers" is technically outbound-only. Undocumented limitation, not necessarily a bug — but should be explicit.

---

## Route Model Has No Category Field

`products/models.py:22` — Route model fields:
`route_name`, `departure_station` (FK), `arrival_station` (FK), `slug`, `description`, `is_actived`, `query_count`

No `route_type`, `transport_type`, `category`. Transport mode always derived via FK chain:
`Route → Station.station_type` (departure-based) or `Route → Contract → VehicleType`

### Field name gotcha: `is_actived` vs `is_active`

Inconsistent across models — copy-paste carefully:

| Model | Field name |
|---|---|
| Route, Trip, Contract | `is_actived` (with 'd') |
| Contract_RateCard, BookingItem, TimeSlot | `is_active` (no 'd') |

Django won't error on wrong field name in filter — silently skips constraint.

---

## Booking Data — Category Linkage

`BookingItem` (`bookings/models.py`) has denormalized:
- `departure_station` CharField — station NAME only, NOT station_type
- `arrival_station` CharField — station NAME only
- `route_name` CharField

**No denormalized station_type on BookingItem.** Querying bookings by transport category requires multi-join:

```python
BookingItem.objects.filter(
    booking_status='Confirmed',  # exact capitalization — valid choices use Title Case
    contract__trip__route__departure_station__station_type='airport'
).count()
```

`booking_status` valid choices: `'Confirmed'`, `'No Show'`, `'Pending'`, `'Partially Refund'`, `'Fully Refund'`, `'Canceled'` — NOT uppercase.

No existing analytics endpoint groups bookings by station_type. Must be written fresh.

---

## Platform Classification

SmartEnPlus architecture supports **multi-category Travel OTA**, not pure transportation:

Evidence from `Contract.SERVICE_CATEGORY_CHOICES`:
- Tours: `DAY_TOUR`, `MULTI_DAY_TOUR`
- Experiences: `EVENT_TICKET`, `ATTRACTION_TICKET`
- Wellness: `SPA_WELLNESS`
- Food: `FOOD_DINING`
- Hotels: `ACCOMMODATION`
- Transfers: `TRANSFER`

Meaningful inventory in non-transport categories: unknown without DB access.

---

## Inventory + Booking Queries (Run in Django Shell)

```python
from products.models import Route
from bookings.models import BookingItem

total = Route.objects.filter(is_actived=True).distinct().count()
airport = Route.objects.filter(is_actived=True, departure_station__station_type='airport').distinct().count()
pct = (airport / total * 100) if total > 0 else 0
print(f"Airport routes: {airport}/{total} = {pct:.1f}%")

total_b = BookingItem.objects.filter(booking_status='Confirmed').count()
airport_b = BookingItem.objects.filter(booking_status='Confirmed', contract__trip__route__departure_station__station_type='airport').count()
pct_b = (airport_b / total_b * 100) if total_b > 0 else 0
print(f"Airport bookings: {airport_b}/{total_b} = {pct_b:.1f}%")
```

FK chain verified: `BookingItem.contract` → `Contract.trip` → `Trip.route` → `Route.departure_station` → `Station.station_type`.

---

## Homepage Recommendation

**Airport Transfers section architecturally justified:**

1. `station_type='airport'` is dedicated first-class type with IATA code support — not a tag or label
2. Filter logic works, in production, returns real routes with real pricing
3. Airport-to-destination is distinct user intent (fixed start point = airport) vs general route search
4. Frontend handles null pricing gracefully

**Not a justification:** `TRANSFER` service_category. Exists but not checked by filter. See Filter Architecture Note above.

**Decision framework thresholds:** "< 10% = demote" heuristic from original audit brief — not data-derived, not in codebase. Rough guideline only. Run queries above against production shell for hard numbers.

**Recommendation:** Keep section. If future inventory data shows airport routes < 10% AND bookings < 10%, demote to search-only.

## Decision

Kept `AirportTransferSection.js` on homepage (`1eec0aa`). Section queries `/front-page/` → `airport_routes[]` key added in `3759dc2`.

## Redesign Spec — Professional Airport Transfer Section

Full AT-1 implementation spec (card design, serializer expansion, null safety, verification) extracted to atomic note.
→ See [[airport-transfer-at1-redesign-spec]]

## Related

- [[airport-transfer-at1-redesign-spec]] — AT-1 full redesign spec (card + backend + layout)
- [[django-serializer-shadowing-pattern]] — HomeSerializer uses local StationSerializer
- [[airport-transfer-redesign-2026]] — frontend implementation notes
- [[smartenplus-product-positioning]] — platform category strategy
- [[carousel-design-standard]] — Embla carousel patterns, breakpoints, gap values