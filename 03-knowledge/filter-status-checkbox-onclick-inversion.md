---
name: filter-status-checkbox-onclick-inversion
description: BUG-001 in filter functionality — onClick handler used instead of onChange for status checkbox, causing state inversion. Checkbox toggles on every render, not user change.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: filter-functionality-audit
---

# Filter Status Checkbox — onClick/onChange Inversion Bug

## Summary
BUG-001: Filter status checkbox uses `onClick` instead of `onChange`, causing inversion. Checkbox toggles on every render, not user change.

## Why It Matters
Checkbox state unreliable. Users deselect → re-renders → re-selects silently. Breaks filters completely.

## Detail
**Location:** `components/activities/FiltersSidebar.js` (or equivalent filter component).

**Bug pattern:**
```jsx
<Checkbox onClick={handleStatusToggle} checked={selected} />
```

Every component re-render calls `onClick` → toggles `selected`. State inverts on render, not user intent.

**Fix:**
```jsx
<Checkbox onChange={handleStatusToggle} checked={selected} />
```

`onChange` fires on user change only. `onClick` fires on every render (button press default).

## Constraints / Gotchas
Apply to ALL filter checkboxes, not just status. Any filter using onClick for state toggle is wrong.

## Related
- [[filter-functionality-audit]] — parent audit (3 bugs, ranked summary, fix procedures)
