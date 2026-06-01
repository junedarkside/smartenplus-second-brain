# React Dual-Hook URL Race

## Summary
Two React hook instances both managing the same URL parameter race each other — the secondary instance overwrites URL state set by the primary, causing divergent UI.

## Problem

When a component calls a hook that owns URL state (e.g. `useDayTripFilters` → `router.push(shallow)`), and that component is rendered inside another component that also calls the same hook, you get two independent state machines both pushing to the same URL.

**Concrete case (ACT-12, 2026-06-01):**
- `FilterDayTripsPage` calls `useDayTripFilters()` — primary instance, owns URL
- `ActivitySearch` (compact, injected into header) also calls `useDayTripFilters()` internally
- Compact mounts → ownHook hydrates from URL → URL-sync effect fires → pushes its own version
- Page-level hook re-hydrates from pushed URL → state diverges → header shows "bangkok", page shows "phuket"

## Fix Patterns

### 1. `{ enabled }` param — gate URL-sync on secondary instances

```js
export function useDayTripFilters({ enabled = true } = {}) {
  useEffect(() => {
    if (!hydrated || !enabled) return;
    router.push(...);         // only primary instance pushes
  }, [filters]);
}
```

Secondary caller passes `{ enabled: false }` → hook hydrates (reads URL) but never pushes. Read-only passenger.

### 2. `isControlled` detection in component

```js
const isControlled = filtersProp !== undefined;
const ownHook = useDayTripFilters({ enabled: !isControlled });
const filters = filtersProp ?? ownHook.filters;
const updateFilter = updateFilterProp ?? ownHook.updateFilter;
```

When props provided: use props, silence own hook. When standalone: use own hook fully.

Hook must still be called unconditionally (React hook rules). The `enabled` flag silences the side effect without conditional hook call.

### 3. `didMountRef` — skip effect on initial render

Debounce or derived-value effects fire on mount with initial state (often empty string). Use `didMountRef` to skip:

```js
const didMountRef = useRef(false);

useEffect(() => {
  if (!didMountRef.current) { didMountRef.current = true; return; }
  updateFilter('search', debouncedSearch);
}, [debouncedSearch]);
```

Prevents clearing URL search param when a controlled component first renders with `pendingSearch = ''`.

### 4. MUI Autocomplete freeSolo — handle string branch in `onChange`

`freeSolo + Enter` fires `onChange(event, "typed-text")` where value is a plain string. Missing string branch → typed text silently discarded, input blanked.

```js
const handleChange = (event, newValue) => {
  if (!newValue) { /* clear */ return; }
  if (typeof newValue === 'object') { /* option selected */ return; }
  // string: user pressed Enter on typed text — commit immediately
  updateFilter('search', newValue);
};
```

Never use early-return or top-level `setPendingSearch('')` before the string branch — it would clear the pending value before committing.

## When This Pattern Applies

- Any hook that both reads AND writes shared external state (URL, Redux, localStorage)
- Any component rendered in multiple contexts: standalone page vs injected into a header/modal
- Any `Autocomplete freeSolo` that supports both typed text and option selection

## Related

[[activities-browse-architecture]] | [[nextjs-hydration-rules]]
