# Django Soft-Delete Preserves S3 File (Cross-Model Reference Invariant)

## Summary
Soft-delete a file-bearing model row keeps the S3 file alive because other models may hold FK references to the same path. Hard-delete fires `post_delete` → S3 cleanup → broken references downstream.

## Why It Matters
Any model with an `ImageField` / `FileField` referenced by other rows must soft-delete, not hard-delete. The `destroy` docstring at `operators/views.py:1860-1868` is the canonical example. Reusable for any file-bearing model with cross-model FK references.

## Detail
- `is_deleted=True` + `deleted_at` + `deleted_by` — row marked dead, file kept
- `get_queryset` filters `is_deleted=False` — gallery/picker hides it
- `post_delete` signal (`operators/signals.py:85-132`) only fires on hard-delete — file removed only then
- Hard-delete is reserved for: admin Django UI, or after `validate-deletion` confirms no live cross-model refs

## Constraints / Gotchas
- Hard-delete breaks `Operator.image`, `Operate.image_url`, `ImageGallery.image`, and any other FK to the S3 path
- Cross-model dedup must key on URL string (not ID) because soft-delete and live references are two different rows sharing the same path
- `validate-deletion` returns `safe_to_delete` based on active bookings/carts/contracts. Use it before any hard-delete.
- `Asset.usage_count` is decremented on soft-delete but the file stays alive. Anyone treating `usage_count == 0` as "safe to garbage-collect" must also check `ImageGallery.objects.filter(image=storage_path).exists()`.

## Related
- [[admin-dashboard-image-pipeline]] — two-model image identity, dedup helpers
- [[operator-image-soft-delete-cascade-gap]] — operator vs contract gallery audit (intentional independence)
- [[operators]] — model summary
- [[django-serializer-shadowing-pattern]] — local class redefinition gotcha (related serializer risk)
- [[django-nested-delete-sweep-pattern]] — exclude-based delete sweep safety
