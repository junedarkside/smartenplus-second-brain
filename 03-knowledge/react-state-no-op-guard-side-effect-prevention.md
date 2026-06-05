# React State No-Op Guard for Side-Effect Prevention

## Summary
When a state write couples a primary value with a side effect (e.g. "set X, reset page"), guard the write inside the `setState` callback: if the new value equals the old, return `prev` to short-circuit React. Side effects never fire on no-op writes.

## Context
React 18 functional setState `setState((prev) => next)`. Side effects coupled to state change include URL push, page reset, scroll, fetch trigger, refetch. All should be guarded by the setState callback, not by callers.

## Problem
`hooks/useDayTripFilters.js` original:
```js
const updateFilter = useCallback((key, value) => {
  setFilters((prev) => ({
    ...prev,
    [key]: value,
    page: key === 'page' ? value : 1,  // ← side effect: reset page
  }));
}, []);
```
Any caller doing `updateFilter('search', '')` when `filters.search === ''` already resets page to 1. Bug fires under StrictMode replay of `<ActivitySearch>` mount (see [[react-strictmode-useref-persistence]]).

## Decision
```js
const updateFilter = useCallback((key, value) => {
  setFilters((prev) => {
    if (prev[key] === value) return prev;  // ← no-op short-circuit
    return { ...prev, [key]: value, page: key === 'page' ? value : 1 };
  });
}, []);
```
React bails out of re-render when `prev === next` (same reference). No state change, no URL sync effect, no page reset.

## Tradeoffs
- Pro: defense in depth — protects all current + future callers
- Pro: works regardless of StrictMode state
- Pro: smaller, more local change than guarding every caller
- Con: ref equality on arrays/objects needs same-reference. Current `features` filter callers always build new arrays, so behavior unchanged. If a caller ever does `updateFilter('features', prev.features)` that would silently no-op — feature test catches it.

## Related
- [[react-strictmode-useref-persistence]] — bug origin
- [[react-dual-hook-url-race]] — broader URL sync + filter hook patterns
- [[nextjs-shallow-router-push-scroll-false]] — sibling fix in same hook
