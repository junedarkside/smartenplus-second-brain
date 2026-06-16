# Contract Soft-Delete: is_actived Invariant

## Summary
Soft-deleting a Contract MUST also set `is_actived=False`. The rule `is_deleted=True ⇒ is_actived=False` is load-bearing, not redundancy.

## Why
~14 public/booking querysets filter `is_actived=True` and do NOT check `is_deleted`. Most critically the booking guard `carts/utils.py:62` (`if not cartitem.contract.is_actived:`) checks only `is_actived`. A contract sitting in someone's cart, then soft-deleted, stays bookable unless `is_actived` flips. So flipping `is_actived` on delete is what actually hides a deleted contract across every path — not the `is_deleted` filter (which is only applied explicitly on 2 of the ~14 paths).

## Details
- Invariant lives in ONE place: `Contract.soft_delete(user)` in `operators/models.py` (sets `is_deleted=True, deleted_at, deleted_by, is_actived=False`, single `.save()` so `post_save` cache signal fires).
- `Contract.restore()` clears the delete flags but deliberately leaves `is_actived=False` — admin re-activates explicitly after review (no silent republish of a possibly-stale contract).
- `update_activation` admin action guards `is_deleted=False` so a deleted contract can't be re-activated onto the public site via bulk-activate.
- The 2 explicit `is_deleted=False` filters (`products/views.py:431` list, `:845` detail) are defense-in-depth; the other ~12 paths rely on the invariant.

## Consequences
- Never bulk `.update(is_deleted=True)` without also setting `is_actived=False` — bypass the model method and you re-open every leak.
- Auditing a new public Contract query path: filter `is_deleted=False` OR confirm it already filters `is_actived=True` (which the invariant covers).

## Related
- [[adr-contract-soft-delete-2026-06-16]]
- [[stations-arrival-viewset-public-leak]]
- [[activities-browse-filter-inactive-contracts]]
- [[django-soft-delete-s3-file-preserve]]
