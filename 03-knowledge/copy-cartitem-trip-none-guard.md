# copy_cartitem_to_bookingitem — trip=None Guard

## Summary
`carts/utils.py:copy_cartitem_to_bookingitem()` crashed with `AttributeError: 'NoneType' object has no attribute 'route'` when booking non-transport contracts where `contract.trip = None`.

## Problem
Lines 100–104 assumed `contract.trip` always non-null:
```python
route_name=cartitem.contract.trip.route,
departure_station=cartitem.contract.trip.route.departure_station,
...
```
Non-transport contracts (DAY_TOUR, SPA_WELLNESS, EVENT_TICKET, ACCOMMODATION, etc.) have `trip=None` by design.

## Fix
Extract trip-dependent values with null guards before `BookingItem.objects.create()`:
```python
_trip = cartitem.contract.trip
_route = _trip.route if _trip else None
_route_name = str(_route) if _route else None
_departure_station = str(_route.departure_station) if _route and _route.departure_station else None
_arrival_station = str(_route.arrival_station) if _route and _route.arrival_station else None
_departure_time = _trip.departure_time if _trip else None
_arrival_time = _trip.arrival_time if _trip else None
```
All 5 BookingItem fields are already `null=True, blank=True` — no migration needed.

## Key Facts
- `Route.__str__()` returns `route.route_name` (CharField)
- `BookingItem.departure_station` / `arrival_station` are `CharField` (not FK) — store station name string
- Transport contracts still populate all fields normally — guard only fires when `trip=None`
- File: `carts/utils.py` ~line 83 (before `BookingItem.objects.create()`)

## Related
[[contract-trip-null-non-transport-pattern]]
[[checkout-confirmation-payment-crash-2026-06-03]]
[[checkout-null-contract-scan-2026-06-03]]
