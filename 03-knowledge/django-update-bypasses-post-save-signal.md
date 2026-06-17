# Django QuerySet.update() Bypasses post_save (No Signal)

## Summary

`Model.objects.filter(...).update(...)` does a direct SQL UPDATE — it does **NOT** call `Model.save()` and does **NOT** fire `post_save`/`pre_save` signals. Use this deliberately to write a field without triggering signal side-effects.

## Why this matters here (ISR no-storm proof)

`ProductDetailViewSet.retrieve` bumps a view counter on every page load. Original code:
```python
contract.daily_counter += 1
contract.save()   # fires post_save → cache-bust signals → would fire ISR revalidate on EVERY view
```
Changed to:
```python
Contract.objects.filter(pk=contract.pk).update(daily_counter=F('daily_counter') + 1)
```
`.update()` fires **no** `post_save` → the `_trigger_revalidate` hooked into `invalidate_contract_caches_on_save` (`operators/signals.py:46`) never runs on a view. This is the load-bearing reason the on-demand ISR revalidation does NOT storm: counter writes (per-view AND the nightly `Contract.objects.all().update(...)` reset) bypass the signal entirely. Only a real `instance.save()` (admin edit, `operators/views.py:946`) fires revalidate.

## Rule

- Want a signal to fire (cache-bust, revalidate, audit) → use `instance.save()`.
- Want to write a field WITHOUT side-effects (counters, denormalized rollups, bulk ops) → use `.update()` / `.bulk_update()`.
- Trade-off: `.update()` does not refresh the in-memory object, doesn't run `save()` overrides, skips `auto_now`. Confirm nothing downstream reads the stale in-memory value (for daily_counter: not in serializer output, not read after the bump → safe).

## Related
- [[docker-standalone-isr-revalidate-gap]]
- [[isr-revalidate-csr-vs-isr-field-matrix]]
- [[celery-task-over-bare-thread-django-signals]]
