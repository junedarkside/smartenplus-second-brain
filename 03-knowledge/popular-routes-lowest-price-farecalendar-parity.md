# Popular Routes lowest_price ↔ FareCalendar Parity

## Summary
`/front-page/` `lowest_price` annotation must mirror FareCalendar `display_rates` logic exactly — one subquery was insufficient; requires two subqueries + `Least()`.

## Problem
`products/views.py` annotated `lowest_price` with a single subquery that had no filter on contract type or ratecard value. This picked the globally cheapest `selling_rate` across ALL contract types including PRIVATE/CHARTER VEHICLE ratecards (per-vehicle price). Homepage Popular Routes card showed wrong rate vs SlideCalendar.

## FareCalendar logic (source of truth)
`FareCalendarViewSet.list` (line ~1918):
```python
if contract.type in ('PRIVATE', 'CHARTER') and rv == 'VEHICLE':
    display_rates.append(rc.selling_rate)
elif contract.type not in ('PRIVATE', 'CHARTER') and rv == 'ADULT':
    display_rates.append(rc.selling_rate)
result[str(d)] = float(min(display_rates)) if display_rates else None
```
Takes min across BOTH groups.

## Fix — two subqueries + Least()
```python
from django.db.models import Value, DecimalField
from django.db.models.functions import Coalesce, Least

_sentinel = Value(999999999, output_field=DecimalField())
_join_lowest = Subquery(
    Contract_RateCard.objects.filter(
        contract__trip__route=OuterRef('pk'),
        contract__is_actived=True,
        is_active=True,
        selling_rate__gt=0,
        ratecard__value='ADULT',
    ).exclude(contract__type__in=['PRIVATE', 'CHARTER']).filter(
        Q(contract__end_date__isnull=True) | Q(contract__end_date__gt=today)
    ).order_by('selling_rate').values('selling_rate')[:1]
)
_private_lowest = Subquery(
    Contract_RateCard.objects.filter(
        contract__trip__route=OuterRef('pk'),
        contract__is_actived=True,
        contract__type__in=['PRIVATE', 'CHARTER'],
        is_active=True,
        selling_rate__gt=0,
        ratecard__value='VEHICLE',
    ).filter(
        Q(contract__end_date__isnull=True) | Q(contract__end_date__gt=today)
    ).order_by('selling_rate').values('selling_rate')[:1]
)
queryset = queryset.annotate(
    lowest_price=Least(
        Coalesce(_join_lowest, _sentinel),
        Coalesce(_private_lowest, _sentinel),
    ),
)
# Post-process: sentinel → None
for route_obj in evaluated_routes:
    if route_obj.lowest_price is not None and route_obj.lowest_price >= 999999999:
        route_obj.lowest_price = None
```

## Why single subquery fails
A single Django `Subquery` can't do conditional filtering (IF type=PRIVATE use VEHICLE ELSE use ADULT). `Least(Coalesce(...sentinel), Coalesce(...sentinel))` is the canonical pattern.

## Wrong fix (do not repeat)
`contract__type='JOIN'` alone excludes PRIVATE/CHARTER entirely — diverges from FareCalendar which includes charter vehicle rates.

## Frontend guard
`homepagev2.js` filters `route.lowest_price > 0` before rendering Popular Routes cards. Routes with no displayable price are hidden entirely (not shown with blank "From").

## Related
- `products/views.py` `FrontPageRouteViewSet` annotate block (~line 1197)
- `FareCalendarViewSet.list` (~line 1918) — source of truth
- [[slidecalendar2-farecalendar-prop-pattern]]
