# Activities Location Search — Backend Text Fallback

**Bug:** Location filter expect integer IDs. Text input like "Phuket" → `_parse_int_list()` returns `[]` → backend branches to `.none()` → zero results.

**File:** `products/views.py:446-453` `_parse_int_list()`

**Fix:** Add text-search fallback after integer parse fails:
```python
ids = _parse_int_list(location_param)
if ids:
    queryset = queryset.filter(service_areas__id__in=ids)
else:
    # Fallback to text search on location name
    queryset = queryset.filter(service_areas__name__icontains=location_param)
```

**Impact:** Users type city names (e.g., "Phuket") not just integer IDs. See [[activities-location-search-bug-2026-06-01]] B-1.

## Related
- [[activities-location-search-bug-2026-06-01]] — full audit
- [[django-parse-int-list-text-fallback]] — general pattern