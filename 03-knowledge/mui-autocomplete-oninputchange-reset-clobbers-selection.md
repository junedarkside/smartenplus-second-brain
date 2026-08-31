# MUI Autocomplete: onInputChange fires on selection too, not just typing

## Summary
Using `onInputChange` to drive a server-side search query, without checking the `reason` argument, causes a freshly-selected option to disappear from the very next fetch — the Autocomplete's controlled `value` then falls back to `null`, looking like "selection doesn't work."

## Context
MUI's `Autocomplete` fires `onInputChange(event, newInputValue, reason)` in three cases: `reason === 'input'` (user actually typing), `reason === 'reset'` (MUI programmatically writes `getOptionLabel(selectedOption)` into the input box right after a selection, or on external `value` change), and `reason === 'clear'` (the clear button). A naive handler that does `setSearchState(newInputValue)` on every call treats the post-selection label-write as a new search term.

## Problem
Found in `admin-dashboard/components/routeFaq/routeFaqEdit.js` and `pages/routemanagement/route-faqs/index.js` (session #370): picking a `RouteByLocationInfo` option set the input text to its composite label (`"Hatyai → Penang"`), which fired `onInputChange` with `reason: 'reset'`, which the handler treated as a new search — refetching the picker list with `?search=Hatyai → Penang`. The backend's `icontains` filter matched neither `departure_location_name` nor `arrival_location_name` against that full compound string, so the refetched option list no longer contained the just-picked route. `options.find(o => o.id === selectedId)` then returned `undefined`, and the controlled `value` fell back to `null` — the selection visibly cleared itself immediately after being made.

The identical unguarded pattern exists in `components/route/routeEdit.js`'s departure/arrival Station Autocompletes (`onInputChange` at lines ~275, ~321) but has never visibly broken there — because a Station's `getOptionLabel` is just `station_name`, a single field that is *also* the search target, so the post-selection refetch coincidentally still includes it. The bug is dormant, not absent, in any Autocomplete whose `getOptionLabel` returns a composite/derived string rather than a single searchable field.

## Decision
Gate the search-state update on `reason`:
```js
onInputChange={(event, newInputValue, reason) => {
  if (reason === 'input' || reason === 'clear') {
    setSearchState(newInputValue);
  }
}}
```
`'clear'` is included so the search term resets to empty (showing the full list again) when the field is cleared; `'reset'` is excluded since that's the programmatic post-selection write, never a real query.

## Consequences
- `components/route/routeEdit.js`'s station pickers carry the same latent pattern, unfixed as of #370 — not reported broken, out of scope for that session's bug report, but will surface the same way if a Station's display label ever becomes a composite string.
- General rule for this codebase: any new Autocomplete wired to a server-side search must use this `reason` guard from the start, not just the ones with composite labels — composite-vs-single-field label is what determines whether the bug is *visible*, not whether it's *present*.

## Related
- `components/routeFaq/routeFaqEdit.js`, `pages/routemanagement/route-faqs/index.js`
- [[tailwind-important-next-vs-mui-dialog-portal]]
