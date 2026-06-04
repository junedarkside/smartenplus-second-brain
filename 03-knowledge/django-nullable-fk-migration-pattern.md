# Django Nullable FK Migration Pattern

## Summary
Changing a ForeignKey from required (`NOT NULL`) to optional (`null=True`) requires both a model change and a migration. The view layer allowing `None` without the migration causes `IntegrityError` at the DB level.

## Problem
View code sets `place_obj = None` and passes it to `Model.objects.create(place=None)`. If the DB column is still `NOT NULL`, PostgreSQL raises:
```
IntegrityError: null value in column "place_id" violates not-null constraint
```
This happens even if Django's model field is updated — the migration must be applied for the DB schema to change.

## Decision

**Model change:**
```python
# Before
place = models.ForeignKey(Place, on_delete=models.CASCADE)

# After
place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True)
```

**`on_delete` change:** `CASCADE` → `SET_NULL` — when the referenced Place is deleted, the stop is preserved with `place=None` rather than cascade-deleted.

**Migration:**
```bash
venv/bin/python manage.py makemigrations <app> --name="<model>_<field>_nullable"
venv/bin/python manage.py migrate
```

**Order of operations matters:** apply migration before deploying view code that sets the field to `None`. If deployed in wrong order: `IntegrityError` in production.

## Tradeoffs
- `null=True` adds nullable column — queries that filter `place__isnull=False` now have meaning
- `SET_NULL` preserves parent row (stop) when child (Place) is deleted — usually correct for junction tables
- Alternative: `on_delete=PROTECT` — prevents Place deletion if any stop references it. Use when orphaned stops are unacceptable.

## Consequences
- Frontend display code must guard `place` being `None` — `item?.place?.name`, `item?.place?.image_gallery?.length`
- Serializers returning nested `place` must handle `None` — `PlaceSerializer(allow_null=True)` or `SerializerMethodField`

## Related
- [[django-nested-delete-sweep-pattern]]
