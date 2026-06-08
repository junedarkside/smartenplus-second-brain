# Operator Image Soft-Delete — Intentional Independence from Contract Galleries

## Summary

Soft-deleting an `OperatorImageGallery` row (admin "delete image" in operator gallery) **intentionally does NOT cascade** to `ImageGallery` rows attached to contracts. The two models share only the `image` URL string — there is no FK. An operator can soft-delete a master gallery image and a contract that already adopted that image will keep rendering it on the consumer frontend. This is correct, intentional design — not a gap. Existing contracts are self-managed content and must be edited through the contract management workflow.

## Context

Image selection flow (see [[admin-dashboard-image-pipeline]]):

```
OperatorImageGallery (operator master)  -- copy `image` path -->  ImageGallery (contract row)
                ↓                                                            ↓
   admin gallery page (soft-delete)                          consumer frontend (DayTripCard, DayTripDetailPage)
```

When the admin picks an operator gallery image into a contract, the backend creates a new `ImageGallery` row whose `image` field is the *same S3 path string* as the source. After that point, there is no relational link between the two records — only an incidental string match.

## Why They Are Independent

Soft-delete preserves the S3 file to avoid breaking cross-model references — see [[django-soft-delete-s3-file-preserve]] for the generic invariant. The `destroy` docstring (`operators/views.py:1860-1868`) states this explicitly.

But the soft-delete itself only flips `is_deleted=True` on the `OperatorImageGallery` row. It does:

1. **Not touch** `ImageGallery` rows that copied the same `image` path.
2. **Not surface** deletion state to the consumer frontend (`ContractSerializer.image` ships `[id, image, order]` only — no `is_deleted`).
3. **Not block** on the `validate-deletion` action's `safe_to_delete=false` signal; the action is a separate `GET` preflight that the admin UI calls voluntarily.

Result: the operator-side gallery hides the image; the contract-side keeps it. A guest browsing `/activities/detail/{slug}` still sees the soft-deleted image because `contract.image` (an array of `ImageGallery` records) is the only thing the frontend consumes.

## Details

### Models

`smartenplus-backend/operators/models.py`:

- **`ImageGallery`** (L514-526) — contract image record. `contract = FK(Contract, CASCADE)`, `image = ImageField(upload_to='contract/vehicle/')`, `order = IntegerField`. **No FK to `OperatorImageGallery`. No `is_deleted` flag.**
- **`OperatorImageGallery`** (L556-599) — operator master image. `operator = FK(Operator, SET_NULL)`, `image = ImageField(upload_to='contract/vehicle/')`, plus soft-delete fields `is_deleted` / `deleted_at` / `deleted_by` (L578-587) and Asset Registry link `asset = FK(Asset, SET_NULL)` (L562-569).

Both models write to the same S3 prefix `contract/vehicle/`. Same path string ends up on both rows.

### Soft-delete endpoint

`smartenplus-backend/operators/views.py:1858-1882` — `destroy` action on `OperatorImageGalleryViewSet`:

```python
instance.is_deleted = True
instance.deleted_at = datetime.now(pytz.utc)
instance.deleted_by = request.user
instance.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])
# decrement Asset.usage_count
return Response(status=204)
```

No query against `ImageGallery`. No post-save side effect on contract rows.

### Preflight that *detects* the issue

`validate-deletion` action at `operators/views.py:1910-1996` does compute the cross-model overlap:

```python
image_path = image.image.name
contracts_using_image = ImageGallery.objects.filter(image=image_path)...
active_contracts_count = Contract.objects.filter(id__in=..., is_actived=True).count()
# ...
safe_to_delete = not (active_bookings or active_carts)
```

But `safe_to_delete` is gated on **bookings/carts only**, not on `active_contracts_count`. Contracts merely appear in the `warnings[]` list as `"{n} active contracts reference this image"`. The admin UI uses `safe_to_delete` as the hard gate.

### Admin preflight (admin-dashboard)

`admin-dashboard/pages/routemanagement/operators/images/index.js`:

- L104 — `validateDeletion(item.id, true)` on dialog open
- L116-122 — re-validates on confirm; blocks only when `!validation.safe_to_delete`. Contracts-warning is informational

So even when the warning shows "N active contracts reference this image", the delete button proceeds.

### Serializer exposure

`smartenplus-backend/operators/serializers.py`:

- L22-56 — `OperatorImageGallerySerializer` exposes `is_deleted`, `deleted_at`, `deleted_by`, `deleted_by_name`. Read-only.
- L148 — `_ImageGallerySerializer` (used by `ContractSerializer.image` at L168 via `source='imagegallery_set'`) only exposes `['id', 'image', 'order']`. **No deletion state. No back-reference to the operator image.**
- L300-303 — public `ImageGallerySerializer`, same shape.

So the consumer-side payload literally cannot tell a deleted image apart.

### S3 cleanup signal

`smartenplus-backend/operators/signals.py:85-132` — `post_delete` handler for `OperatorImageGallery` deletes the S3 file and zeroes the Asset's `storage_path`. **Only fires on hard-delete.** Soft-delete preserves the S3 file (intentional — see docstring), which is why soft-deleted images keep loading on the contract pages.

The parallel handler at L134-156 for `ImageGallery` only fires when a contract image is hard-deleted (e.g. contract removes that image from `imageSelection` on save).

### Frontend consumer

`smartenplus-frontend/components/activities/browse/DayTripCard.js:43-44` and `components/activities/detail/DayTripDetailPage.js:118` both read `contract.image` and render whatever URL is there. No deletion check possible (no field to check).

## Decision

**No behavior change. The current design is correct.** Soft-delete on `OperatorImageGallery` is intentionally independent from `ImageGallery` rows. Hard-delete would break live contracts/bookings/carts that point at the same S3 path. Soft-delete preserves the path, which is the *correct* invariant for the consumer side.

The earlier audit **incorrectly framed** this as a "gap" and recommended cascade A+. That recommendation was retracted after the user clarified the design intent: contracts are self-managed content edited through the contract management workflow. No cascade is intended.

The fix surface (admin UX clarity only, no behavior change):

1. **Add explicit copy to admin delete dialog** — when `active_contracts > 0`, show an informational block: "This removes the image from the operator's master gallery. It will not affect contracts that already use this image — those are managed via the contract edit screen."
2. **Optional — extend `safe_to_delete` semantics** — split into `safe_for_operator_gallery` vs `safe_for_consumer` so the admin can see which is true. Today they are conflated.
3. **Optional — add `is_deleted` to `_ImageGallerySerializer`** so admin tooling can flag stale contract images. Would NOT change consumer behavior because the consumer payload doesn't ship the flag.

None of the above change the cascade semantics. The image keeps rendering, which is the intended invariant.

## Tradeoffs

| Approach | Pros | Cons |
|----------|------|------|
| Status quo (soft-delete only) | No broken images on consumer pages. No FK migration. | Stale images keep showing forever from a contract that "shouldn't" have them. Admin has no clean way to find/replace. |
| Cascade soft-delete to ImageGallery rows | Contract pages stop showing the image immediately. | **Rejected — not a candidate.** Would break live contracts. User has confirmed contracts are self-managed content. |
| Add FK `ImageGallery.source_operator_image` | True cascade possible. Allows "find usages" queries. | Backfill migration required (string match → FK). Changes contract save logic. Higher blast radius. **Also rejected — cascades are not desired.** |
| Explicit admin dialog copy (recommended) | Zero data model change. Closes the UX gap. Preserves intentional independence. | Doesn't fix images already soft-deleted before the dialog ships. Doesn't help if the operator forgets to edit the contract afterward. |

## Consequences

- **For audit/inventory:** any "operator gallery is X images" count and any "this image is used in Y contracts" count must `filter(is_deleted=False)` on the operator side but NOT on the contract side. The two counts can legitimately diverge.
- **For Asset Registry:** `usage_count` is decremented on soft-delete (`views.py:1877-1880`). But the actual S3 file stays alive because contract `ImageGallery` rows still reference the same path. `usage_count` is therefore a measure of *active gallery references*, not *live S3 referrers*. Anyone using `usage_count == 0` as "safe to garbage-collect" must also check `ImageGallery.objects.filter(image=storage_path).exists()`.
- **For hard-delete tooling (admin only):** the `post_delete` S3 cleanup signal will yank the file even when contracts still reference it. Must always run `validate-deletion` first AND check `active_contracts_count == 0` (not just `safe_to_delete`).

## Related

- [[admin-dashboard-image-pipeline]] — two-model identity, dedup helpers, frontend flow
- [[operators]] — model summary mentioning soft-delete
- [[admin-dashboard]] — project overview
- [[celery-tasks]] — `soft_delete_expired_ratecards` (different soft-delete pattern, same intent)
- [[django-nullable-fk-migration-pattern]] — useful if "Add FK" tradeoff is ever taken
