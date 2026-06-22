---
name: station-type-airport-first-class-iata-restriction
description: `station_type='airport'` is first-class classification (IATA code restricted to airport only). Architecture fact: airport stations can only be created with valid IATA code, not generic "airport" string. Guarantees data quality.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: transportation-category-audit
---

# Station Type Airport — First-Class IATA Restriction

## Summary
`station_type='airport'` is first-class classification. IATA code restricted to airport only. Architecture: airport stations require valid IATA code, not generic "airport" string.

## Why It Matters
Prevents bogus airport records. Guarantees every "airport" station maps to real IATA airport code (BKK, CNX, HKT). Data quality for routing.

## Detail
**Model constraint:**
```python
class Station(models.Model):
    station_type = models.CharField(choices=[...])
    iata_code = models.CharField(max_length=3, blank=True)

    def clean(self):
        if self.station_type == 'airport' and not self.iata_code:
            raise ValidationError("Airport stations require IATA code")
```

**Business rule:** ONLY airports have `iata_code` (3-letter IATA). Bus stations, piers, ports have `place_id` or `name` only.

**Creation flow:**
1. User selects `station_type='airport'`
2. System prompts for IATA code (required)
3. Validation: code must match real IATA airport list (optional, but recommended)

**Why first-class:** Airport = highest-importance station type (flight connections, international routing). Strict enforcement prevents degradation.

## Constraints / Gotchas
Migration: existing stations marked `airport` without IATA code → require manual data entry OR reclassify to `bus_station`/`pier`.

## Related
- [[transfer-category-vs-airport-filter-independence]] — companion architecture fact
- [[transportation-category-audit]] — parent audit (3-level classification)
