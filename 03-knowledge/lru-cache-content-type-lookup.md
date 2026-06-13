# LRU Cache ContentType Lookup

## Summary
`ContentType.objects.get(app_label='operators', model='contract')` is a per-request DB hit (12 cards × 1 /check/ = 12 hits/page load). Module-level `@lru_cache(maxsize=2)` wrapper eliminates the per-request cost.

## Context
GenericForeignKey fields (used heavily for `favoritable`, `bookable`, `reviewable` polymorphism) require a `ContentType` lookup. The naive pattern — `ContentType.objects.get_for_model(Contract)` or `.objects.get(app_label=..., model=...)` — issues a SQL query every time. On the 2026-06-08 favorite-heart analysis, the `/api/favorites/check/` endpoint fired once per card on a listing page (12 cards = 12 CT lookups in a single request), and CTs never change at runtime. The DB hit is pure waste.

## Problem
1. **Per-request DB hit for static data** — CT rows are seeded at deploy time and effectively immutable.
2. **Hidden N+1** — the same lookup appears in serializers, views, and signals, multiplying the cost.
3. **Migration fragility** — a rename of `app_label` or `model` silently breaks the cache key; need a guard.

## Details
The wrapper:

```python
# helpers/content_types.py
from functools import lru_cache
from django.contrib.contenttypes.models import ContentType

@lru_cache(maxsize=64)
def get_contract_ct() -> ContentType:
    return ContentType.objects.get(app_label='operators', model='contract')

@lru_cache(maxsize=64)
def get_hotel_ct() -> ContentType:
    return ContentType.objects.get(app_label='operators', model='hotel')
```

`maxsize=2` is the proposal baseline; `64` is safer as new model types get added. The cache lives for the worker process lifetime — on most deployments that's hours to days, so the CT is fetched once per process per model.

Wiring:

```python
# views.py
from helpers.content_types import get_contract_ct

def check_favorite(request, contract_id):
    ct = get_contract_ct()
    exists = Favorite.objects.filter(
        user=request.user,
        content_type=ct,
        object_id=contract_id,
    ).exists()
    return Response({'favorited': exists})
```

Edge cases:
- **Tests:** `@lru_cache` persists across tests, masking state changes. Add `get_contract_ct.cache_clear()` to test setUp, or wrap the helper so tests can opt out.
- **Migrations:** if `app_label` or `model` is renamed, the cache key changes silently and old cached entries become dead. The cache is bounded (`maxsize=64`) so it self-cleans; explicit `cache_clear()` in a data migration is the rigorous approach.

## Decision
All `ContentType` lookups in hot paths (views, serializers, signals fired per-row) MUST go through an `@lru_cache`d helper. Direct `.objects.get` is banned in code review for performance-critical paths.

## Tradeoffs
- Process-local cache means multi-process deploys each fetch once — that's fine.
- `lru_cache` makes testing trickier; the test suite pays the cost.
- Alternative: `django.contrib.contenttypes.models.ContentType.objects.get_for_model(Contract)` is itself cache-backed (per-request via `GenericForeignKey` machinery) but the `get()` form is not — the explicit form is faster but per-DB-hit.

## Consequences
Reusable for any CT-heavy view: activity browse, hotel list, polymorphic reviews. The 12× → 1× reduction in CT lookups per page load is a 92% query reduction on the affected endpoints. Audit pattern: `grep -rn "ContentType.objects.get" --include="*.py" | grep -v "get_for_model"` should return only `helpers/content_types.py`.

## Related
- [[django-serializer-shadowing-pattern]] — same family of "hide the ORM detail behind a helper" patterns.
