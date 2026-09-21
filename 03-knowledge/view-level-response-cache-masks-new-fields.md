---
name: view-level-response-cache-masks-new-fields
description: Two Django view-level response caches (product-detail 30min, trip-search 15min) will silently serve responses missing a newly-added serializer field for up to their full TTL after deploy — distinct from the precompute-cache staleness pattern, needs its own manual cache.clear() step.
metadata:
  type: reference
---

# View-Level Response Cache Masks New Serializer Fields

## Summary

Adding a new field to `ContractSerializer`/`ProductDetailSerializer` does not appear in responses immediately after deploy if a request for that exact cache key was already served — the cached dict was built and stored before the field existed, and neither cache has any field-set/version fingerprint in its key.

## Where

Two separate, unrelated response caches, both keyed too coarsely to notice a serializer shape change:

- `ProductDetailViewSet.retrieve()` (`products/views.py:1075-1086`) — full response cached **30 minutes** under `product_detail_v1_{slug}_{lang_hash}`.
- `FindTripViewSet.list()` (`products/views.py:356-369`) — trips-by-route lookup cached **15 minutes** under `trips:{from}:{to}` (not even date-scoped).

## How this was hit (2026-09-21, seat-check-indicator feature)

Added `has_live_seat_check` to both serializers, verified via `manage.py shell` (worked immediately — no cache involved there), then hit the real HTTP endpoint and got `has_live_seat_check: FIELD MISSING` on a contract already known to qualify. Spent real debugging time suspecting a serializer bug before tracing it to a pre-existing cached response from before the code change. `cache.clear()` (Django's generic cache API, not Redis-CLI pattern-delete) fixed it instantly.

## Distinction from precompute-cache staleness

[[precompute-cache-stale-after-logic-fix]] covers a *different* mechanism — a Celery precompute task with a skip-if-fresh TTL guard that refuses to regenerate a key it thinks is still valid. This note covers plain Django view-level response caching (`cache.get`/`cache.set` directly in a viewset method) with no precompute/guard logic at all — the cache is just stale because nothing ever told it the underlying serializer shape changed. Same *symptom* (new field/logic invisible after deploy), different code path, different fix mechanics (`cache.clear()` vs `redis-cli --scan --pattern ... | xargs del`).

## Fix / deploy step

Any change to `ContractSerializer` or `ProductDetailSerializer` — new field, changed computation, anything affecting response shape — needs a cache clear at deploy time:

```python
from django.core.cache import cache
cache.clear()
```

or, if the cache backend supports pattern deletes and a full clear is too broad for a busy prod cache, target the two key prefixes specifically (`product_detail_v1_*`, `trips:*`) — confirm the actual cache backend (Redis vs local-memory) before assuming pattern-delete is available.

**Do not treat "field not showing up" as a code bug without checking this first** — it wastes debugging time chasing a serializer issue that doesn't exist.

## Related

[[precompute-cache-stale-after-logic-fix]] · [[cache-precompute-key-must-match-reader-suffix]] · [[seat-availability-fe-integration-decision]]
