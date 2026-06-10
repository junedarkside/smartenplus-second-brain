# Django M2M Location JOIN for Recommendations

## Pattern

Non-transport contracts use `primary_location` (FK) + `service_areas` (M2M to Location). To find all contracts at a given location:

```python
Contract.objects.filter(
    Q(primary_location=location) | Q(service_areas=location),
    ...
).distinct()  # REQUIRED — M2M join produces duplicate rows without it
```

## Why `.distinct()` is required

`service_areas` is M2M. A contract in 3 service areas that all match returns 3 rows. Without `.distinct()`, the same contract appears multiple times in results.

## Location bridge from transport contract

```python
arrival_location = source_contract.trip.route.arrival_station.location_name
# location_name is FK to Location, not a string field
```

Station → Location FK = `station.location_name` (confusingly named, it's a FK).

## Proven pattern

Same `Q(primary_location=loc) | Q(service_areas=loc)` used in `products/views.py:462-475` for location search filtering. Reused in `find_activity_contracts` (products/services.py).

## Context
SmartEnPlus cross-sell engine, 2026-06-10. `find_activity_contracts` function.
