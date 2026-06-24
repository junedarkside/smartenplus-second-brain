# precompute-popular-contracts — Fix Plan (3-Agent Debate)

> **Status:** PRODUCTION EMERGENCY — deploy immediately  
> **Severity:** CONFIRMED ACTIVE INCIDENT on smallest burstable EC2 (1 vCPU, CPU-credit limited, celery concurrency=1, external RDS).
>
> **CORRECTED ROOT CAUSE (single-vCPU):** Not parallel DB burst — at concurrency=1 child tasks drain *serially*. Damage is *total sequential work* pinning the one core: hourly popular = 100×12 = 1,200 computations; **nightly 2 AM all-contracts = 1000+ ×12 = 12,000+ computations = the bigger CPU-credit drain.** Cache-key bug made every computation a cache miss → recompute every hour + every night → credit drain → CloudWatch spike (19.9% CPU, 18MB net).
>
> **Fixes (branch `fix/precompute-popular-contracts`):** (1) cache-key `:none` align + cache list-not-dict — `7b6a9f8`; (2) skip-if-fresh `cache.ttl()` guard — `a59b9b8`; (3) revert stagger (counterproductive at conc=1), hourly→every-6h, drop nightly all-contracts from beat — `2c2c799`.  
> **Source:** [[precompute-popular-contracts-audit]] + 3-agent debate (Backend Engineer / Senior Reviewer / SRE)

---

## Root Cause Summary

Two bugs cause the entire recommendation pre-computation system to produce zero cache hits in production. They must be fixed together.

| Bug | Location | Severity | Status |
|-----|----------|----------|--------|
| BUG 1 — `list.count()` TypeError | `products/tasks.py:111` | CRITICAL | Active every hour |
| BUG 3 — Cache key mismatch (`:none` missing) | `products/tasks.py:67` | CRITICAL | Active since launch |
| BUG 4 — No `order_by` on `[:100]` slice | `products/tasks.py:108` | LOW | Active, not crashing |
| BUG 2 — `reset_daily_counter` not scheduled | `Smartenplus/celery.py` | MEDIUM | Active, slow burn |

---

## BUG 1 — `list.count()` TypeError

Django queryset with `[:100]` slice becomes a Python list. `list.count()` with no args = `TypeError`. Outer `except Exception` at line 128 catches it silently — task returns `{"status": "error"}`, for loop never runs, zero contracts queued. **Cache never warms. Every recommendation call hits DB.**

**Fix — `products/tasks.py` lines 104–111:**
```python
# BEFORE (broken)
popular_contracts = Contract.objects.filter(
    is_actived=True
).filter(
    Q(booked_count__gte=50) | Q(daily_counter__gte=10)
)[:100]
count = popular_contracts.count()  # TypeError!

# AFTER (correct — one query, no race)
popular_contracts = list(
    Contract.objects.filter(
        is_actived=True
    ).filter(
        Q(booked_count__gte=50) | Q(daily_counter__gte=10)
    ).order_by('-booked_count', '-daily_counter')[:100]  # also fixes BUG 4
)
count = len(popular_contracts)
```

Debate note: `list()` + `len()` preferred over `qs.count()` + `qs[:100]` (two queries with phantom-read race where count and slice could diverge).

---

## BUG 3 — Cache Key Mismatch

`precompute_contract_recommendations` writes keys WITHOUT `rate_date` component:
```
recommendations:{contract_id}:{rec_type}:{limit}
```

`get_recommendations` in `products/services.py:795` reads keys WITH `rate_date` component:
```
recommendations:{contract_id}:{rec_type}:{limit}:{rate_date or 'none'}
```

For requests with no date (the common case), this appends `:none`. Pre-computed keys never match. **Zero cache hits system-wide, even if BUG 1 is fixed.**

**Fix — 4 places in `products/tasks.py`:**

Line 67 (`precompute_contract_recommendations`):
```python
# BEFORE
cache_key = f"recommendations:{contract_id}:{rec_type}:{limit}"
# AFTER
cache_key = f"recommendations:{contract_id}:{rec_type}:{limit}:none"
```

Lines 230–233 (`precompute_contract_on_create`):
```python
# BEFORE
cache_keys = [
    f"recommendations:{contract_id}:hybrid:8",
    f"recommendations:{contract_id}:hybrid:12",
    f"recommendations:{contract_id}:similar:8",
]
# AFTER
cache_keys = [
    f"recommendations:{contract_id}:hybrid:8:none",
    f"recommendations:{contract_id}:hybrid:12:none",
    f"recommendations:{contract_id}:similar:8:none",
]
```

Line 292 (`get_cache_statistics`):
```python
# BEFORE
cache_key = f"recommendations:{contract.id}:hybrid:8"
# AFTER
cache_key = f"recommendations:{contract.id}:hybrid:8:none"
```

Debate note: `rate_date`-specific requests (e.g. `get_recommendations(id, 'hybrid', 8, '2026-06-20')`) still miss cache — precompute never writes date-keyed entries. Acceptable for now: date-specific requests are an edge case; the common path (`rate_date=None`) is fixed.

---

## BUG 2 — `reset_daily_counter` Not Scheduled (Phase 2)

`operators/tasks.py:8` defines `reset_daily_counter()` — rolls `daily_counter` into `booked_count` and resets to 0 — but it's absent from `Smartenplus/celery.py` beat_schedule. `daily_counter` has been accumulating since launch, never reset. `booked_count` never gets the daily rollup.

**Do NOT ship with Phase 1.** Requires data audit first.

**Pre-deploy audit:**
```python
from operators.models import Contract
import statistics
vals = list(Contract.objects.values_list('daily_counter', flat=True))
print(f"Max: {max(vals)}, Median: {statistics.median(vals)}")
# If max > 1000: cap before enabling
Contract.objects.filter(daily_counter__gt=1000).update(daily_counter=1000)
```

**Fix — `Smartenplus/celery.py`, add to `beat_schedule`:**
```python
'reset-daily-counter': {
    'task': 'operators.tasks.reset_daily_counter',
    'schedule': crontab(hour=0, minute=30),  # 00:30 Bangkok — avoids 00:00 precompute
},
```

Restart **Beat** (not just workers) — `DatabaseScheduler` syncs new entries on Beat startup.

Debate note: `booked_count = F('booked_count') + F('daily_counter')` grows monotonically. Contracts with 50+ cumulative bookings never fall off the popularity filter. Acceptable if `booked_count` is a pure signal (not used in pricing). Audit before shipping.

---

## Deploy Sequence

### Phase 1 — Emergency (today)

1. `git pull` on EC2
2. `sudo supervisorctl restart celery-worker`
3. Beat does NOT need restart
4. Verify: `celery -A Smartenplus call products.tasks.precompute_popular_contracts`

### Phase 2 — Scheduled fix (next business day)

1. Run data audit in Django shell
2. Cap `daily_counter` if needed
3. Take `booked_count` snapshot to `/tmp/contract_counts_backup.json`
4. `git pull` on EC2
5. `sudo supervisorctl restart celery-beat` (Beat restart required)

---

## Verification

```bash
# Confirm cache keys now written with :none suffix
redis-cli -n 0 --scan --pattern "recommendations:*:hybrid:8:none" | wc -l
# Expected: > 0 within 1 min of manual trigger

# Confirm cache hit on a popular contract
python manage.py shell -c "
from django.core.cache import cache
from operators.models import Contract
c = Contract.objects.filter(is_actived=True, booked_count__gte=50).first()
if c:
    key = f'recommendations:{c.id}:hybrid:8:none'
    print('Cache hit:', cache.get(key) is not None)
"

# Confirm no more silent errors
grep 'Error in precompute_popular_contracts' /var/log/celery/worker.log
# Should be empty after fix

# Watch Redis keyspace hit rate improve
redis-cli -n 0 INFO stats | grep -E "keyspace_hits|keyspace_misses"
```

---

## Rollback

```bash
# Code rollback
git revert HEAD --no-edit
sudo supervisorctl restart celery-worker

# Cache rollback (safe — do NOT flushdb, only recommendation keys)
redis-cli -n 0 --scan --pattern "recommendations:*" | xargs redis-cli -n 0 DEL
# Worst case: DB fallback for 1 hour until next precompute fires
```

---

## Related

- [[precompute-popular-contracts-audit]] — original audit with all bug details
- [[celery-tasks]] — general Celery patterns
- [[recommendation-engine-completion-roadmap]] — broader roadmap

## Atomized Notes (Extracted 2026-06-24)

- [[django-queryset-slice-becomes-list-count-typeerror]] — BUG 1: `qs[:100]` is a list; `.count()` → TypeError. Use `list(qs)` + `len()`.
- [[celery-task-defined-but-not-in-beat-schedule]] — BUG 2: task in `tasks.py` but absent from `celery.py` beat_schedule silently never runs.
- [[cache-precompute-key-must-match-reader-suffix]] — BUG 3: writer omits `:none` suffix reader appends → zero cache hits. Centralize key construction.
