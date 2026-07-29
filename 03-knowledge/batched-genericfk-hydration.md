# Batched GenericForeignKey Hydration (avoid N+1 on a list)

## Summary
When a DRF `list()` must return rows that point at heterogeneous targets via `GenericForeignKey`, do NOT touch `content_object` per row (that's an N+1). Partition rows by content_type, bulk-fetch each type once, map back. Bounded query count regardless of row count.

## Problem
`Bookmark` (generic FK: content_type + object_id) holds blog / contract / product rows. Naive `list()` serializing `content_object` per row = one extra query per row. 50 bookmarks = 50+ queries.

## Pattern
Override `list()` in the ViewSet:
```python
def list(self, request, *args, **kwargs):
    rows = list(self.get_queryset().select_related('content_type').order_by('-created_at'))
    product_ct_id = _get_product_ct().id   # lru_cached — 0 queries after warmup
    contract_ct_id = _get_contract_ct().id

    product_ids  = [r.object_id for r in rows if r.content_type_id == product_ct_id]
    contract_ids = [r.object_id for r in rows if r.content_type_id == contract_ct_id]

    products  = {p.id: p for p in Product.objects.filter(pk__in=product_ids)} if product_ids else {}
    contracts = {c.id: c for c in Contract.objects.filter(pk__in=contract_ids).select_related('operator','trip__route__departure_station','trip__route__arrival_station')} if contract_ids else {}

    data = [self._row(r, products, contracts) for r in rows]
    return Response(data)
```
Result: **rows query + one bulk query per present type** (measured 2 total for a product-only list). CT lookups are `@lru_cache`d → 0 queries.

## Guards
- **Orphan safety**: `products.get(r.object_id)` → `None` when the target was hard-deleted (FK is on ContentType, not the target, so the Bookmark row survives). Summary returns `null`, never a 500.
- **Sentinel CT**: blog rows use the Bookmark model's own CT as a sentinel → don't try to resolve them as a real model; return the raw id (`{wordpress_post_id}`) for the FE to hydrate.
- Return **plain dicts** from the view — a dedicated `ListSerializer` class is YAGNI here.

## Tradeoffs
- `select_related` on the FK chain (operator, trip→route→stations) keeps the per-type fetch to one query even with nested reads.
- Adding a new content type = add its ct-id partition + bulk map. Linear, no N+1 regression.

## Related
- [[adr-saved-page-product-favorites]] — BookmarkViewSet.list() shipped this
- [[sentinel-content-type-bookmark-blog]] — the blog sentinel CT gotcha
