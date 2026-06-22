---
name: transfer-category-vs-airport-filter-independence
description: `TRANSFER` service_category and airport filter are independent. Airport filter never checks service_category. Architecture clarification: airport stations can be transfers, piers, buses — filter type ≠ category.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: transportation-category-audit
---

# TRANSFER Category vs Airport Filter Independence

## Summary
`TRANSFER` service_category and airport filter are INDEPENDENT. Airport filter never checks `service_category`. Architecture: airport stations can be transfers, piers, buses. Filter type ≠ category.

## Why It Matters
Confusion assumption: "Airport filter = transfers only". Wrong. Airport filter means "pick-up at airport" — could be transfer, pier pickup, bus meeting point. Category independence.

## Detail
**Two classification axes:**

**Axis 1 — station_type (location type):**
- `airport` (IATA airport)
- `bus_station` (bus terminal)
- `pier` (ferry pier)
- `place` (generic)

**Axis 2 — service_category (transport mode):**
- `TRANSFER` (private van)
- `SHARED` (shared minivan)
- `FERRY` (boat)
- `BUS` (bus)

**Independence:**
```python
# Airport filter (by location)
stations = Station.objects.filter(station_type='airport')
# Returns ALL airport stations (transfers, piers, buses)

# Service category filter (by mode)
stations = Station.objects.filter(service_category='TRANSFER')
# Returns ALL transfer stations (airports, piers, bus stations)
```

**Combined:**
```python
# Airport transfers ONLY
stations = Station.objects.filter(
    station_type='airport',
    service_category='TRANSFER'
)
```

**Why independent:** Transfer can start from pier (hotel pickup) OR airport (arrival). Both valid transfers.

## Constraints / Gotchas
Homepage "Airport Transfer" label conflates axes. Clarify in UI: "Airport transfer" = airport station + TRANSFER category.

## Related
- [[station-type-airport-first-class-iata-restriction]] — companion architecture fact
- [[transportation-category-audit]] — parent audit (decision framework)
