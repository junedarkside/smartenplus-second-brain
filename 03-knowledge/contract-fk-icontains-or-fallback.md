# Contract FK IContains OR Fallback for Location Search

## Summary
When filtering a model by an FK name field (e.g., `Location.location_name`), use `Q(fk__location_name__icontains=text) | Q(fk2__location_name__icontains=text).distinct()` for both the M2M (`service_areas`) and the FK (`primary_location`). M2M filter requires `.distinct()`. The 1-hour `cache.set` TTL means a backend deploy requires `cache.clear()`.

## Context
Backend search views (activities, day-tour page) accept a text search param and need to match it against the contract's related location(s). A contract can have one `primary_location` (FK) and many `service_areas` (M2M to `Location`). The API receives a name string (not an ID), so the filter has to be on `location_name__icontains`.

## Problem
Naive filter: `Contract.objects.filter(service_areas__location_name__icontains=text)` — misses contracts where the searched name matches `primary_location` but not any `service_areas`. Conversely, `primary_location__location_name__icontains=text` alone misses M2M matches. And `service_areas` is M2M, so `filter` on it produces duplicates when a contract has multiple matching service areas.

Cache: search results are `cache.set` with a 1-hour TTL. If the location data is updated (e.g., a location gets renamed), the cache is stale for up to an hour. A `cache.clear()` is needed on deploy to force fresh results.

## Details
The correct pattern:

```python
from django.db.models import Q
from .models import Contract, Location

def search_contracts_by_location(text):
    return Contract.objects.filter(
        Q(primary_location__location_name__icontains=text) |
        Q(service_areas__location_name__icontains=text)
    ).distinct()  # ← required for M2M
```

`Q(...) | Q(...)` covers both FK and M2M in a single query (Django generates one SQL JOIN with OR). `.distinct()` deduplicates the M2M duplicates.

For the cache:

```python
from django.core.cache import cache

def get_search_results(text):
    cache_key = f'search:{text}'
    results = cache.get(cache_key)
    if results is None:
        results = search_contracts_by_location(text)
        cache.set(cache_key, results, 60 * 60)  # 1 hour
    return results
```

The 1-hour TTL means a deploy that changes `Location.location_name` data won't reflect in search results for up to an hour. The deploy script should include `python manage.py shell -c "from django.core.cache import cache; cache.clear()"` to invalidate.

## Decision
- Use `Q(fk__field__icontains) | Q(m2m__field__icontains).distinct()` for any "filter by related name" pattern
- Cache search results with 1-hour TTL, but require `cache.clear()` on deploy
- For name-icontains search, do NOT use `__iexact` — substring matches are expected for search UX

## Tradeoffs
- Pro: One query, covers both FK and M2M
- Pro: `.distinct()` is the canonical fix for M2M duplicate rows
- Pro: Cache reduces DB load for repeated searches
- Con: 1-hour cache window means stale data after location renames — requires deploy coordination
- Con: `icontains` is non-sargable (no index uses it). For large datasets, search performance degrades. Mitigated by the cache.
- Con: `text` should be sanitized for ILIKE wildcards (`%`, `_`) — user typing `_` should not match all rows

## Consequences
Any new search view that filters by related-model name fields should use this exact `Q | Q.distinct()` pattern. The 1-hour cache + `cache.clear()` on deploy is the contract with the deploy script. A broken cache invalidation silently shows wrong search results for up to an hour — debugging requires knowing the cache is in play.

## Related
- [[django-parse-int-list-text-fallback]] — sibling pattern for parsing list-shaped text params
