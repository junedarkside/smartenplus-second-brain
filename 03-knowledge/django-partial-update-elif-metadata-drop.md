---
name: django-partial-update-elif-metadata-drop
description: Backend partial_update `elif` that only handles ONE field (e.g. order) silently drops all other payload fields on existing rows. Fix: unconditional sync of all payload fields.
metadata:
  type: knowledge
---

# Django partial_update elif metadata drop

## Summary

`partial_update` in DRF that branches on `elif field_changed` only writes THAT field, dropping every other payload field on the existing row. Symptom: "first save works, every subsequent edit of the dropped fields does nothing."

## Context

Two model branches in a `partial_update`: a CREATE branch for new rows, and an UPDATE branch for existing rows. The UPDATE branch was written to handle reorder (`elif instance.order != new_order`) — the body only saves `order`. The CREATE branch correctly persists all metadata fields (`alt_text`, `description`, `caption`).

## Problem

User adds image (CREATE branch → metadata saved correctly). User edits metadata only, doesn't reorder, saves contract. UPDATE branch runs, `elif order != new_order` is FALSE, body skipped. Metadata never reaches the DB. **Only the first save after add works; all subsequent metadata edits vanish.**

## Details

The `elif` body looks like:

```python
elif image_gallery_instance.order != order:
    image_gallery_instance.order = order
    image_gallery_instance.save()
```

The fix is to drop the `elif` condition and unconditionally write all payload fields, like the CREATE branch does:

```python
else:  # existing row, order unchanged or changed
    instance.alt_text = payload.get('alt_text') or (source_instance.alt_text or '' if source_instance else '')
    instance.description = payload.get('description') or (source_instance.description or '' if source_instance else '')
    instance.caption = payload.get('caption') or (source_instance.caption or '' if source_instance else '')
    instance.order = order
    instance.save()
```

## Decision

**Always sync ALL payload fields in UPDATE, not just the one the branch condition was designed for.** The branch is a short-circuit optimization that costs you the user's edits. Order is the easy field to detect; metadata is what users actually edit repeatedly.

## Tradeoffs

- Unconditional save writes ALL fields every update, even unchanged ones. Cost: 1 extra UPDATE query per save. Worth it: never lose user data.
- The fallback chain (`payload.get('x') or source_instance.x`) ensures blanks in payload don't overwrite existing data with empty string.

## Consequences

- Always re-test the "edit metadata only, no reorder" path after writing any `partial_update` with branched logic. First-save-success is not enough.
- When two write paths exist (CREATE + UPDATE), make them write IDENTICAL fields. Drift = lost data.
- For view-level `partial_update` with many payload fields, prefer `serializer.partial_update(instance, validated_data)` so DRF handles field iteration uniformly.

## Related

- [[operator-image-alt-caption-fields]] — same bug class, different field set
- [[django-soft-delete-s3-file-preserve]] — file-bearing model invariants
- Source: `operators/views.py:711-733` (the fix)
