# ORM Annotation Aggregate Min Rate

## Summary
For DRF `ContractViewSet` to support `-average_rating` and `min_price`/`max_price` ordering, annotate `avg_rating = Avg('review__rating')` and `min_rate = Min('ratecards__selling_rate', filter=Q(ratecards__is_active=True)).distinct()` — never raw JOIN (N+1 risk).

## Context
Marketplace listing pages sort and filter by aggregated fields (avg review rating, min active rate card price, max rate). The naive approach — `.order_by('-review__rating')` or joining ratecards inline — produces duplicate rows and triggers N+1 queries when a contract has multiple ratecards. During the 2026-06 experiences redesign, `Contract.objects.order_by('-average_rating')` returned 3× rows for contracts with 3 ratecards.

## Problem
Two failure modes:
1. **Row duplication:** joining `ratecards` multiplies contracts by ratecard count; pagination breaks and `count()` is wrong.
2. **N+1 on sort:** ordering by a related aggregate without `annotate` falls back to per-row subqueries.

The fix is annotation + filter + `distinct()`, in that order.

## Details
The canonical queryset pattern:

```python
from django.db.models import Avg, Min, Q

queryset = Contract.objects.annotate(
    avg_rating=Avg('review__rating'),
    min_rate=Min(
        'ratecards__selling_rate',
        filter=Q(ratecards__is_active=True),
    ),
).distinct()
```

Then in the viewset's `filter_backends` or `get_queryset`:
- `-average_rating` ordering works because `avg_rating` is annotated.
- `min_price` / `max_price` filters translate to `min_rate__gte` / `min_rate__lte` (or use a `django-filter` `NumberFilter` with the annotation as field name).

Always pass the filter inside the aggregate — `Min('ratecards__selling_rate')` without the `is_active` filter returns inactive (legacy) rates and ruins min-price search.

## Decision
Annotation + conditional aggregate + `distinct()` is the only acceptable pattern. Raw `.values()` joins are banned in code review.

## Tradeoffs
- `distinct()` adds a sort step in some DB engines (PostgreSQL handles it efficiently; MySQL is fine with composite indexes).
- If a contract has zero active ratecards, `min_rate` is `None` — filter these out at the API layer or order them last explicitly.
- `Avg` over an empty `review` set returns `None`; sortable as `NULLS LAST` semantics in PG, but MySQL is implementation-defined — be explicit.

## Consequences
Reusable for any product model with related pricing: `HotelPackage` with `room_types__nightly_rate`, `Tour` with `departures__price`, etc. New listing endpoints MUST use annotation-based aggregates, never raw JOIN ordering. The N+1 audit (`grep "order_by.*__"` in `viewsets/`) catches drift.

## Related
- [[recommendation-anchor-first-transport-rule]] — same contract surface area; sort/filter pipeline converges.
- [[recommendation-type-selection-by-service-category]] — listing query shape per service type; aggregates vary by domain.
