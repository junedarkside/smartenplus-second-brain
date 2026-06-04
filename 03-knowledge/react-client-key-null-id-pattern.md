# React Client-Key Null-ID Pattern

## Summary
For optimistic-add UIs where new records have no server ID yet, use `id: null` as the "unsaved" sentinel and a separate `_clientKey` (e.g., `Date.now()`) for stable React `key` props. Never use a fake ID as the DB identifier.

## Problem
```js
// Anti-pattern: Date.now() as fake DB id
const newItem = { id: Date.now(), ... }

// Two problems:
// 1. Backend receives id=1748900000000 → tries GET or forced INSERT with that PK
//    → PostgreSQL sequence collision if sequence < 1748900000000
// 2. Multiple new items added same ms → duplicate keys → React render bugs
```

## Decision

```js
const newItem = {
  id: null,          // sentinel: "not yet saved" — backend routes to create branch
  _clientKey: Date.now(),  // local-only stable key for React rendering
  order: newOrder,
  title: `Stop ${newOrder}`,
  // ...
};
```

React `key`:
```jsx
<div key={item.id ?? item._clientKey}>
```

**Why `id: null` works on the backend:**
- `Model.objects.get(id=None)` raises `DoesNotExist` → create branch runs
- Create branch does NOT pass `id=` to `Model.objects.create()` → DB assigns real PK
- Response returns the real PK → `enableReinitialize={true}` on Formik picks it up

**Why `_clientKey` over `index`:**
- `index` as key breaks drag-and-drop reorder (React reconciles by position, not identity)
- `_clientKey` is stable across re-renders until the item is replaced by server response

## Consequences
- `_clientKey` must never be sent to the backend — it's a frontend-only field. Backend ignores unknown keys, but add a comment to make intent clear.
- After save, server response replaces `id: null` with real PK. `_clientKey` becomes irrelevant (existing items have real `id`).
- Any component reading `item.id` for non-key purposes (e.g., delete by id) must handle `null` — use `_clientKey` as fallback or disable delete on unsaved items.

## Related
- [[django-nested-delete-sweep-pattern]]
