# List Filter + Sort — `useXFiltering` Memoised Hook

## Summary
Pure filter+sort logic lifted from page component into a `useMemo`-backed hook. Keeps page JSX small, makes logic testable in isolation.

## Context
`pages/locations/index.js` had inline `filteredLocations = allLocations.filter(...).sort(...)` running every render. With search input changing per keystroke + URL param sync, the chain re-ran even when `searchTerm` hadn't moved. #252 split it into `useLocationsFiltering(allLocations, searchTerm, sortOption)`.

## Decision

```js
export const useLocationsFiltering = (allLocations, searchTerm, sortOption) => {
  return useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    const filtered = q
      ? allLocations.filter(loc => loc.location_name?.toLowerCase().includes(q))
      : allLocations;

    const sorted = [...filtered].sort((a, b) => {
      switch (sortOption) {
        case SORT_OPTIONS.ALPHABETICAL_ASC:
          return (a.location_name || '').localeCompare(b.location_name || '');
        case SORT_OPTIONS.ROUTE_COUNT_DESC:
          return (b.route_count || 0) - (a.route_count || 0);
        default:
          return 0;
      }
    });
    return sorted;
  }, [allLocations, searchTerm, sortOption]);
};
```

## Rules

1. **Always spread before sort** — `[...filtered].sort(...)`. In-place sort mutates the source array; if `filtered` is a reference shared via props, this corrupts parent state.
2. **Stable dep array** — `[allLocations, searchTerm, sortOption]` is the minimal complete set. Adding `domain` or other render-time values = false cache misses.
3. **Hook name mirrors noun** — `useLocationsFiltering`, `useActivitiesFiltering`. Not `useFilter` (too generic — clashes with any input filter).
4. **Pure inside `useMemo`** — no `Date.now()`, no `window`, no `console` (useEffect that), no fetch.

## When NOT to extract
- One-line filter (`.filter(x => x.active)`). Inline is fine.
- Filter depends on a ref or external store (Redux, Context value that changes every render). Memo deps wrong → bug. Keep inline or use a selector.

## Tradeoffs
- **Pro:** page component reads top-down (`useLocationsFiltering(list, q, sort)` → render). Logic testable by mocking inputs.
- **Pro:** `useMemo` skips re-sort when `searchTerm` debounce holds steady.
- **Con:** one extra hook per list page (~30 LOC). Worth it once the page grows past ~150 LOC.

## Related
- `hooks/useLocationsFiltering.js` — #252
- `hooks/useLocationFiltering.js` — singular form (single-location page, different concern; do not merge)
- [[react-usememo-rules]] (TBD) — broader memo discipline
