# React State No-Op Guard for Side-Effect Prevention

## Summary
Wrap setState in `prev === next ? return prev : set` guard when the next value is a derived object/array or has coupled side effects. Prevents unnecessary re-renders + side-effect cascades (URL push, page reset, refetch, scroll).

## Context
React functional `setState((prev) => next)`. When the new value is the same reference as the old, React bails out of the re-render. But if the next value is a *new object* (even with identical contents), React proceeds — re-render fires, `useEffect` deps change, and any coupled side effects (URL sync, page reset, scroll, fetch) trigger.

## Problem
Any `useState` that holds an object/array AND couples a side effect to its update is at risk. Example: filter hook that resets `page: 1` whenever any filter changes. If a caller passes the same value (e.g. user toggles a filter off then on without changing), the page reset still fires — wrong.

This is a general React perf pattern. Recurs wherever object references change on every render (MUI Autocomplete inputValue, Redux selectors, derived state from props).

## Details
The guard:

```js
setState((prev) => {
  if (Object.is(prev[key], value)) return prev;  // ← no-op short-circuit
  return { ...prev, [key]: value, page: key === 'page' ? value : 1 };
});
```

`Object.is` is the canonical React comparison (handles `NaN === NaN` correctly). For arrays, check `prev.length === next.length && prev.every((v, i) => Object.is(v, next[i]))`. For deep equality, use a small `shallowEqual` helper or library.

The pattern applies to:
- `useState` holding derived state from props
- `useState` holding MUI Autocomplete `inputValue` (inputValue can drift from `value` on every keystroke)
- `useState` holding URL-derived filters

## Decision
Use the no-op guard pattern whenever:
1. The new value is an object/array reference that may be `===` to the old
2. The state write has a coupled side effect (URL, page, refetch)

For primitive values (`useState<string>`), no guard needed — React's default `Object.is` bailout works.

## Tradeoffs
- Pro: defense in depth — protects all current and future callers
- Pro: React-idiomatic, no extra library
- Pro: Smaller change than guarding every caller site
- Con: Ref equality on arrays/objects needs same-reference. If a caller does `updateFilter('features', [...prev.features])` that creates a new array — guard would not no-op, would proceed (correct behavior).
- Con: For derived state, the guard is "is the result === the input" which can mask upstream bugs (parent re-renders with new array reference but same contents)

## Consequences
Apply this pattern by default to any new `useState` holding object/array state. The codebase's existing `useDayTripFilters` hook already has a specific instance of this fix (see existing note). The general rule: when in doubt, guard.

This also reduces `useEffect` dep churn. A guarded setState that returns the same reference doesn't update deps, doesn't fire downstream effects, doesn't cause the ripple of re-renders that perf-sensitive surfaces (checkout, payment) cannot afford.

## Related
- [[useeffect-cancellation-guard-pattern]] — sibling pattern for async effects
- [[mui-autocomplete-inputvalue-sync]] — concrete instance of the inputValue drift problem
