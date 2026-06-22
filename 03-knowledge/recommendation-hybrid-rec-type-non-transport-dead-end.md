---
name: recommendation-hybrid-rec-type-non-transport-dead-end
description: `hybrid` `rec_type` kills non-transport recommendations when `trip.route` is null. Regression: activity/attraction recommendations return zero because hybrid filter depends on route existence. Cross-sell revenue loss.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: recommendation-engine-completion-roadmap
---

# Recommendation Hybrid rec_type — Non-Transport Dead End

## Summary
`hybrid` `rec_type` kills non-transport recommendations when `trip.route` is null. Regression: activity/attraction recommendations return zero because hybrid filter requires route. Cross-sell revenue loss.

## Why It Matters
Hybrid recommendation type (transport + activity) broken for pure activity bookings. Customers see no cross-sell → revenue loss.

## Detail
**Bug code:**
```python
# recommendation logic
if rec_type == 'hybrid':
    recs = recs.filter(trip__route__isnull=False)  # WRONG — kills activities
```

**Hybrid intent:** Show BOTH transport + activity recommendations. Activity bookings should get activity cross-sells (transport optional).

**Fix:**
```python
if rec_type == 'hybrid':
    # Transport recs require route
    transport_recs = recs.filter(category='TRANSPORTATION', trip__route__isnull=False)
    # Activity recs NO route requirement
    activity_recs = recs.filter(category__in=['DAY_TOUR', 'ATTRACTION_TICKET'])
    recs = (transport_recs | activity_recs).distinct()
```

**OR** split `hybrid` into two modes: `hybrid_transport` (require route) + `hybrid_activity` (no route required).

## Constraints / Gotchas
Catalog data: many activity/attraction bookings have NO linked route (standalone experience). Hybrid must return them.

## Related
- [[recommendation-flat-score-finder-pollution]] — companion correctness issue
- [[recommendation-engine-completion-roadmap]] — parent (P0 regression, gap table)
