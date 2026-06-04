# Django Nested Delete Sweep Pattern

## Summary
Exclude-based delete sweep for nested resources is safe only if the `existing_ids` set is guaranteed non-empty. A `continue` or exception in the processing loop leaves the set incomplete — the sweep then deletes all rows not in the partial set.

## Problem
```python
existing_ids = set()
for item in items:
    try:
        instance = Model.objects.get(id=item['id'])
        # ... update ...
        existing_ids.add(instance.id)
    except Model.DoesNotExist:
        if not some_condition:
            continue  # ← silently skips — id never added to set
        instance = Model.objects.create(...)
        existing_ids.add(instance.id)

Model.objects.filter(parent=parent).exclude(id__in=existing_ids).delete()
# If existing_ids is empty → deletes ALL rows for this parent
```

## Decision
Two required guards:

**1. Never `continue` in the create branch** — if an item can't be created, raise an error or skip and handle explicitly. A silent skip means the item is excluded from `existing_ids` and treated as "deleted."

**2. Guard the delete sweep:**
```python
if existing_ids:
    Model.objects.filter(parent=parent).exclude(id__in=existing_ids).delete()
```

## Details

**When this pattern appears:** any endpoint that accepts a full replacement list of nested resources (timeline stops, order items, image gallery). Pattern: loop → upsert → delete-non-present.

**Why `continue` is the silent killer:** it exits the loop iteration before `existing_ids.add()`. The item is still in the DB but not in the exclude set → gets deleted on next save.

**Null id sentinel:** new items from the frontend should use `id: null` (not a fake timestamp). `Model.objects.get(id=None)` raises `DoesNotExist`, cleanly routing to create branch. Timestamp PKs risk collision with PostgreSQL sequences.

**`id=` in create:** never pass `id=item['id']` when creating — let DB assign PK. Forced PK on create with a client-generated value (e.g., `Date.now()`) can collide if sequence lags.

## Consequences
- Stops one of the most common "all rows deleted on save" bugs in Django REST APIs
- Applies to any nested writable resource: `TimeLinePlace`, `OrderItem`, `ImageGallery`, etc.

## Related
- [[django-nullable-fk-migration-pattern]]
- [[react-client-key-null-id-pattern]]
