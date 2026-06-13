# Django Filter Gotcha — _parse_int_list Returns [] on Text Input → .none()

## Summary

`_parse_int_list(value)` in `products/views.py` returns `[]` for non-integer inputs (e.g. `"Phuket"`). Caller branches to `queryset.none()` on empty list — ZERO results silently. Any filter on this pattern fails for text input.

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

`_parse_int_list` safe by design. Dangerous assumption in caller: empty list = bad input. But empty list also means text input — valid when users type location names.

## Fix

Text-search fallback for `else` branch:

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

Any Django filter using `_parse_int_list` must handle empty-list explicitly. Empty list = text input, not error. `.none()` always wrong unless input guaranteed integers only.

## Cache Warning (Deploy-Critical)

`products.ContractViewSet` caches 1 hour (`contract_list_v1_{md5(params)}`). After deploy, clear cache:
```python
cache.delete_pattern("contract_list_v1_*")  # or cache.clear()
```

**Mandatory on every deploy that changes the filter shape** — stale cache will serve old text-fallback-broken responses for up to 1 hour. Add to CI deploy script or runbook. See [[contract-fk-icontains-or-fallback]] for the M2M+FK variant of the same pattern.

## SmartEnPlus Instance

`smartenplus-backend/products/views.py:446-453` — location filter on `ContractViewSet`. Fixed in `260601-fix/activities-browse-audit`. Note: `status=active` param from frontend silently ignored — viewset hardcodes `is_actived=True`. Harmless but misleading.

## Related

- [[activities-location-search-bug-2026-06-01]] — RC-1 root cause chain
- [[backend-architecture]] — `products` app = public API; differs from `operators` viewset