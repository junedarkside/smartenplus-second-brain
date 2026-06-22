---
name: filter-text-stringify-bug
description: BUG-003 in filter functionality — object passed to text filter, causing `[object Object]` string comparison. Breaks text search filters.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: filter-functionality-audit
---

# Filter Text Stringify Bug — Object to String

## Summary
BUG-003: Object passed to text filter, causing `[object Object]` string comparison. Breaks text search filters.

## Why It Matters
Text filters never match. User searches "Bangkok" → filter compares `[object Object].includes("Bangkok")` → always false.

## Detail
**Location:** Text filter input handler.

**Bug pattern:**
```js
const matchesText = (item) => {
  return textQuery && item.name.toLowerCase().includes(textQuery); // WRONG if item is object
};
```

If `item` is `{ name: "Bangkok" }` and code accidentally passes entire `item` instead of `item.name`, `[object Object].toLowerCase()` = `"[object Object]"`.

**Fix:** Ensure text filter extracts string field:
```js
const matchesText = (item) => {
  const textField = item.name || item.title || item.description; // extract string
  return textQuery && textField.toLowerCase().includes(textQuery);
};
```

## Constraints / Gotchas
Happens when filter data structure changes (enum → object) but filter logic not updated.

## Related
- [[filter-status-checkbox-onclick-inversion]] · [[filter-array-includes-reference-bug]] — filter bug companions
- [[filter-functionality-audit]] — parent audit
