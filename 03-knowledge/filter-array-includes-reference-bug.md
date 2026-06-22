---
name: filter-array-includes-reference-bug
description: BUG-002 in filter functionality — `Array.includes()` uses reference equality instead of value comparison. Filter always returns false for object/array items.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: filter-functionality-audit
---

# Filter Array.includes Reference Equality Bug

## Summary
BUG-002: `Array.includes()` uses reference equality instead of value comparison. Filter always returns false for object/array items.

## Why It Matters
Broken filter logic. Users select filter → nothing matches because object reference !== array value.

## Detail
**Location:** Filter component checking if selected item exists in filter array.

**Bug pattern:**
```js
const isSelected = filterArray.includes(item); // WRONG for objects/arrays
```

`includes()` uses `===` (reference equality). `item` is new object reference each render → always false.

**Fix (for objects):**
```js
const isSelected = filterArray.some(f => f.id === item.id);
```

**Fix (for primitives):** `includes()` is fine for strings/numbers/booleans.

## Constraints / Gotchas
Only affects object/array filters. Primitive filters (category names, booleans) work correctly with `includes()`.

## Related
- [[filter-status-checkbox-onclick-inversion]] — BUG-001 companion
- [[filter-functionality-audit]] — parent audit
