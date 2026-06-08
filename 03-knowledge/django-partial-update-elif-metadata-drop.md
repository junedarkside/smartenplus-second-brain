---
name: django-partial-update-elif-metadata-drop
description: Backend partial_update `elif` that handles only ONE field silently drops all other payload fields on existing rows. Fix: unconditional sync of all payload fields.
metadata:
  type: knowledge
---

# Django partial_update elif metadata drop

## Summary

`partial_update` in DRF that branches on `elif field_changed` only writes THAT field, dropping every other payload field on existing row. Symptom: "first save works, every subsequent edit of dropped fields does nothing."

## Context

Two branches in `partial_update`: CREATE for new rows, UPDATE for existing. UPDATE written to handle reorder (`elif instance.order != new_order`) — body only saves `order`. CREATE persists all metadata (`alt_text`, `description`, `caption`).

## Problem

User adds image (CREATE → metadata saved). User edits metadata only, no reorder, saves contract. UPDATE runs, `elif order != new_order` FALSE, body skipped. Metadata never reaches DB. **First save after add works; every subsequent metadata edit vanishes.**

## Details

`elif` body:

```python
elif image_gallery_instance.order != order:
    image_gallery_instance.order = order
    image_gallery_instance.save()
```

Fix: drop `elif` condition, unconditionally write all payload fields like CREATE does:

```python
else:  # existing row, order unchanged or changed
    instance.alt_text = payload.get('alt_text') or (source.alt_text or '' if source else '')
    instance.description = payload.get('description') or (source.description or '' if source else '')
    instance.caption = payload.get('caption') or (source.caption or '' if source else '')
    instance.order = order
    instance.save()
```

## Decision

**Sync ALL payload fields in UPDATE, not just the one the branch condition was designed for.** Branch is a short-circuit optimization that costs user edits. Order easy to detect; metadata is what users edit repeatedly.

## Tradeoffs

- Unconditional save writes ALL fields every update. Cost: 1 extra UPDATE query. Worth it: never lose user data.
- Fallback chain (`payload.get('x') or source.x`) prevents blanks in payload from overwriting existing data with empty string.

## Consequences

- Re-test "edit metadata only, no reorder" path after writing any `partial_update` with branched logic. First-save-success not enough.
- Two write paths (CREATE + UPDATE) must write IDENTICAL fields. Drift = lost data.
- For view-level `partial_update` with many payload fields, prefer `serializer.partial_update(instance, validated_data)` so DRF iterates fields uniformly.

## Related

- [[operator-image-alt-caption-fields]] — same bug class, different field set
- [[django-soft-delete-s3-file-preserve]] — file-bearing model invariants
- Source: `operators/views.py:711-733` (the fix)
