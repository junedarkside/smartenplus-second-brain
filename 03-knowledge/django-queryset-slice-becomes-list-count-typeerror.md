# django-queryset-slice-becomes-list-count-typeerror

## Summary
Slicing a Django QuerySet (`qs[:100]`) returns a Python list, not a QuerySet. Calling `.count()` on it raises `TypeError` (list.count needs an arg). Silent `except Exception` swallows it → task returns error, loop never runs.

## Why It Matters
A swallowed TypeError here meant the entire recommendation pre-compute produced zero cache hits from launch. The bug was invisible — task "succeeded" with `{"status": "error"}`. Any `qs[:N].count()` pattern is a latent crash.

## Detail
```python
# BROKEN — qs[:100] is a list; .count() → TypeError
popular = Contract.objects.filter(...)[:100]
n = popular.count()  # TypeError!

# CORRECT — materialize once, count with len()
popular = list(Contract.objects.filter(...).order_by('-booked_count')[:100])
n = len(popular)
```

Prefer `list(qs)` + `len()` over `qs.count()` + `qs[:N]` (two queries with phantom-read race where count and slice diverge).

## Constraints / Gotchas
- `order_by()` must come BEFORE the slice — can't order a list. Combining fixes both the TypeError and nondeterministic ordering.
- Never wrap precompute/celery bodies in bare `except Exception` — it hides TypeErrors as silent "error" status.

## Related
- [[precompute-popular-contracts-fix-plan]] — BUG 1 source
- [[precompute-popular-contracts-audit]] — original audit
