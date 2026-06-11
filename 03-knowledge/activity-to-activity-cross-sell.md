# Activity-to-Activity Cross-Sell

## Summary

Activity contracts (DAY_TOUR, SPA_WELLNESS, etc.) can now cross-sell other activities at the same location via `find_nearby_activities()`.

## Problem

Original `find_activity_contracts()` is transport→activity only: derives location from `trip.route.arrival_station`. Activity-source contracts either have `arrival_station=None` or no `trip` at all — both return empty.

## Solution

`find_nearby_activities(source_contract, limit)` — pivots on `primary_location` / `service_areas` fields (exist on all Contract types, documented "for upselling").

### Dispatch Logic (services.py)

```python
if rec_type == 'activity':
    if (source_contract.trip and source_contract.trip.route
            and source_contract.trip.route.arrival_station):
        find_activity_contracts()   # transport → activity
    else:
        find_nearby_activities()    # activity → activity
```

**Critical:** must check `arrival_station` not just `trip + route`. Activity contracts have `trip + route` but `arrival_station=None`. Checking only `trip and route` routes to wrong function → empty results.

### Scoring (base 50, max ~110, relative sort only)

| Signal | Points | Field |
|--------|--------|-------|
| Location match | 50 | base — guaranteed by query filter |
| Same `service_category` | +30 | strongest intent signal |
| Quality | 0–20 | `contract.score` × 2 (0–10 scale) |
| Exact primary_location | +10 | vs service_areas fallback |

Dropped: `difficulty_level` (null in most SE Asia contracts), `tour_duration_days` (weak vs quality score).

## Debugging Pattern

If "People Also Book" shows empty:
1. Check `contract.primary_location` — if null AND `service_areas` empty → no anchor → returns `[]`
2. Check candidate count: `Contract.objects.filter(Q(primary_location=anchor)|Q(service_areas=anchor), service_category__in=ACTIVITY_CATEGORIES, is_actived=True).exclude(id=source.id).count()`
3. If count > 0 but API returns empty → check dispatch condition (arrival_station check)

## Related

[[recommendation-type-selection-by-service-category]] · [[recommendation-system]] · [[cross-sell-placement-strategy]]
