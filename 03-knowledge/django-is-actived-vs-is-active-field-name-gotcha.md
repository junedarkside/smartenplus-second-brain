---
name: django-is-actived-vs-is-active-field-name-gotcha
description: Django field name typo gotcha: `is_actived` (with 'd') vs `is_active` (no 'd') across models. Django silently skips wrong filter name → query returns zero, no error. Silent filter failure.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: transportation-category-audit
---

# Django is_actived vs is_active — Field Name Gotcha

## Summary
Django field name typo: `is_actived` (with 'd') vs `is_active` (no 'd'). Django silently skips wrong filter → zero results, no error. Silent failure.

## Why It Matters
Filter `Contract.objects.filter(is_actived=True)` returns nothing because field is `is_active`. No error → silent data loss. Hard to debug.

## Detail
**Bug pattern:**
```python
# Model definition
class Contract(models.Model):
    is_active = models.BooleanField(default=True)  # CORRECT

# Query with typo
Contract.objects.filter(is_actived=True)  # WRONG — silent miss
# Returns: [] (empty queryset, no error)
```

**Why typo happens:** Copy-paste from legacy code OR autocorrect slip. Django doesn't validate field names at query time.

**Fix:** Grep for `is_actived` across codebase:
```bash
grep -r "is_actived" .
```

Replace all instances with `is_active`.

**Prevention:** Use model linting:
```python
# In tests
def test_contract_filter_field_exists():
    assert hasattr(Contract, 'is_active')
```

## Constraints / Gotchas
Also check `is_actived` in filters, serializers, admin list_display, search fields. Any ORM lookup with typo = silent miss.

## Related
- [[transportation-category-audit]] — parent audit (classification tables, filters)
