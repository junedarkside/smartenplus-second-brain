# Django Filter Gotcha — _parse_int_list Returns [] on Text Input → .none()

## Summary

`_parse_int_list(value)` in `products/views.py` safely returns `[]` for non-integer inputs (e.g. `"Phuket"`). But the caller branches to `queryset.none()` when the list is empty — returning ZERO results silently. Any filter built on this pattern fails completely for text input.

## Problem

```python
location_ids = self.request.query_params.get('location')
if location_ids:
    location_ids_list = _parse_int_list(location_ids)  # "Phuket" → []
    if location_ids_list:
        queryset = queryset.filter(service_areas__id__in=location_ids_list)
    else:
        queryset = queryset.none()  # ← ZERO RESULTS for any string
```

`_parse_int_list` is intentionally safe — no exception on bad input. The dangerous assumption is in the caller: empty list = "bad input, return nothing". But empty list also means "text input" — and text is valid when users type location names.

## Fix

Add a text-search fallback for the `else` branch:

```python
from django.db.models import Q

location_ids = self.request.query_params.get('location')
if location_ids:
    location_ids_list = _parse_int_list(location_ids)
    if location_ids_list:
        queryset = queryset.filter(
            Q(service_areas__id__in=location_ids_list) |
            Q(primary_location__id__in=location_ids_list)
        ).distinct()
    else:
        # Text fallback
        queryset = queryset.filter(
            Q(service_areas__location_name__icontains=location_ids) |
            Q(service_areas__city__icontains=location_ids) |
            Q(service_areas__province__icontains=location_ids) |
            Q(primary_location__location_name__icontains=location_ids)
        ).distinct()
```

## Rule

Any Django filter using `_parse_int_list` must handle the empty-list case explicitly. "Empty list" means text input — not an error. Branching to `.none()` is always wrong unless input is guaranteed to be integers only.

## Cache Warning

`products.ContractViewSet` caches response for 1 hour (`contract_list_v1_{md5(params)}`). After deploying the fix, clear cache:
```python
cache.delete_pattern("contract_list_v1_*")  # or cache.clear()
```

## SmartEnPlus Instance

`smartenplus-backend/products/views.py:446-453` — location filter on `ContractViewSet`. Fixed in `260601-fix/activities-browse-audit`. Note: `status=active` param sent by frontend is silently ignored by this viewset — it hardcodes `is_actived=True`. Param is harmless but misleading.

## Related

- [[activities-location-search-bug]] — RC-1 root cause chain
- [[backend-architecture]] — `products` app = public API; this is different from `operators` viewset
