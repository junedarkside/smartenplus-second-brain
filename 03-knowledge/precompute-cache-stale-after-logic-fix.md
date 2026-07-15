# Precompute Cache Serves Stale Data After Logic Fix

## Summary

Fixing query logic that feeds a precomputed cache does NOT propagate the fix while a skip-if-fresh guard holds — deploy must flush the affected key pattern or stale data persists up to full TTL.

## Context

Precompute Celery tasks often guard against redundant regeneration: skip a cache key if its remaining TTL is above a refresh threshold. That guard is correct for data-freshness but wrong for CODE-freshness — it cannot know the generating query changed.

## Problem

Case: rec-price fix (BE `06423c5`) added `is_active=True` to 8 `Min(selling_rate)` annotations in `products/services.py`. Rec cache: 24h TTL, hourly precompute with skip-if-fresh guard at `products/tasks.py:66-75` (`refresh_threshold = ttl - 2h` → skip when remaining TTL > 22h). Keys written pre-deploy keep serving wrong prices; hourly task refuses to overwrite them because they look "fresh". Worst case: 24h of stale prices post-deploy.

## Details

Deploy step (one-off, after any change to cache-feeding query logic):

```bash
redis-cli --scan --pattern "recommendations:*" | xargs redis-cli del
```

Next request/precompute regenerates with fixed code immediately. Self-heals via TTL if forgotten — but that's the full TTL window of wrong data.

Detection checklist when shipping a fix to any function called inside a `cache.set` path:
1. Find the cache key pattern (`grep cache.set` around the changed function's callers)
2. Check for skip-if-fresh / TTL guards in the precompute task
3. If guard exists → add pattern flush to the deploy runbook for that change

## Consequences

- "No migration, no FE change" is NOT the same as "no deploy steps" — cache layers are deploy surface too.
- Applies to any precompute+guard combo, not just recommendations (same class as ISR-cache-persists gotcha: correct code, stale artifact).

## Related

[[rec-engine-report-audit]] · [[precompute-popular-contracts-fix-plan]] · [[recommendation-system]] · [[docker-standalone-isr-revalidate-gap]]
