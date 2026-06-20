# precompute-popular-contracts — Task Audit

## Summary

`precompute_popular_contracts` is hourly Celery Beat task that warms Redis recommendation cache for high-traffic contracts. Fan-out pattern: parent task selects up to 100 contracts → queues one child task per contract → child pre-computes 12 cache keys per contract (4 types × 3 limits).

**File:** `products/tasks.py:88-130`  
**Schedule:** every hour at `:00` (`crontab(minute=0)`)  
**Celery config:** `Smartenplus/celery.py` key `precompute-popular-contracts`

---

## What It Does

1. Queries `Contract` where `is_actived=True` AND (`booked_count >= 50` OR `daily_counter >= 10`)
2. Slices to top 100 (`[:100]`)
3. Calls `.count()` on already-sliced queryset (see bug below)
4. Queues `precompute_contract_recommendations.delay(contract.id)` for each
5. Returns `{"processed": count, "status": "queued"}`

**Child task** (`precompute_contract_recommendations`, `tasks.py:42-84`):
- 4 rec types: `similar`, `alternatives`, `packages`, `hybrid`
- 3 limits: `8`, `12`, `20`
- = 12 cache keys per contract
- Cache TTL: 24 hours
- Retry: max 3, exponential backoff `60 * 2^n` seconds
- Error per key: logs warning, continues (doesn't abort contract)

---

## Bugs & Issues

### BUG 1 — Sliced queryset `.count()` is wrong (line 111)

```python
popular_contracts = Contract.objects.filter(...).filter(...)[:100]  # sliced — evaluates to list
count = popular_contracts.count()  # ERROR: calling .count() on a list raises AttributeError
```

Slicing a Django queryset returns a list. `list.count()` exists but counts **occurrences of an argument**, not length — calling it with no args raises `TypeError`. In practice this either crashes silently (exception caught at line 128) or returns wrong value.

**Fix:** call `.count()` before slicing, or use `len()` after slicing.

```python
qs = Contract.objects.filter(is_actived=True).filter(
    Q(booked_count__gte=50) | Q(daily_counter__gte=10)
)
count = min(qs.count(), 100)
popular_contracts = qs[:100]
```

### BUG 2 — No `@bind=True` / no retry on parent task

Parent task swallows all exceptions (line 128-130, returns dict with status `error`). Celery won't retry. If DB is momentarily unavailable, task silently fails and cache goes cold for 1 hour.

**Fix:** either accept the behavior (acceptable for hourly warm-up) or add retry with `bind=True`.

### BUG 3 — No ordering on `[:100]` slice

`Contract.objects.filter(...)[:100]` without `order_by` = non-deterministic which 100 contracts are selected. Database may return different contracts each run.

**Fix:** order by priority signal before slicing.

```python
.order_by('-booked_count', '-daily_counter')[:100]
```

### ISSUE — `daily_counter` field semantics unclear

Threshold `daily_counter >= 10` suggests daily reset. No reset logic visible in this file. If `daily_counter` is never reset, all contracts eventually qualify and the `booked_count >= 50` filter does the real work. Check if a daily reset task exists.

### ISSUE — `precompute_contract_recommendations` not `bind=True` retry pattern

Uses `self.retry()` which requires `bind=True` — confirmed present at line 42 (`@shared_task(bind=True, max_retries=3)`). Retry countdown: `60 * 2^retries` = 60s, 120s, 240s. Correct. **No issue here.**

---

## Cache Key Pattern

```
recommendations:{contract_id}:{rec_type}:{limit}
```

Examples for contract 42:
- `recommendations:42:similar:8`
- `recommendations:42:hybrid:20`
- (12 keys total per contract)

---

## Task Ecosystem

| Task | Schedule | Purpose |
|------|----------|---------|
| `precompute_popular_contracts` | Hourly `:00` | Warm top-100 popular contracts |
| `precompute_all_active_contracts` | 2:00 AM daily | Full cache warm for all active |
| `cleanup_expired_recommendation_cache` | 3:00 AM daily | Placeholder — Redis TTL handles expiry automatically |
| `get_cache_statistics` | Every 30 min | Monitor cache hit rate (samples 100 contracts, checks `hybrid:8` key) |
| `precompute_contract_on_create` | Signal-triggered | Warm 3 keys (hybrid:8, hybrid:12, similar:8) at 15-min TTL on new contract |

---

## Observations

- `cleanup_expired_recommendation_cache` is a no-op placeholder. Redis TTL on 24-hour keys makes it redundant unless manual invalidation is added.
- `get_cache_statistics` only checks `hybrid:8` key as proxy for "is contract cached" — understates coverage since 11 other keys also exist.
- `precompute_contract_on_create` uses 15-min TTL vs 24-hour for hourly task. New contracts get short-lived cache until nightly batch upgrades them. Acceptable.
- No deduplication guard: if contract qualifies for both hourly popular AND nightly full batch, it gets pre-computed twice. Redis overwrite is idempotent so no correctness issue, just wasted work.

---

## Related

- [[celery-tasks]] — general Celery patterns in SmartEnPlus
- [[celery-beat-payment-scheduling]] — other Beat tasks
- [[recommendation-engine-completion-roadmap]] — roadmap for recommendation system
- [[contract-model-ambiguity-audit]] — Contract model field audit
