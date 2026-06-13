# MUI Autocomplete — handleInputChange Must Emit to Parent

**Bug:** `handleInputChange` updates local state but never calls `onChange(newValue)`. Parent never sees typed text.

**Wrong:**
```js
const handleInputChange = (event, newInputValue) => {
  setInputValue(newInputValue);  // Local update only
  // onChange(newInputValue) NEVER called
};
```

User types "Phuket" → `inputValue` local state updates → parent `filters.location` stays `null` → API fires unfiltered.

**Right:**
```js
const handleInputChange = (event, newInputValue) => {
  setInputValue(newInputValue);
  onChange(newInputValue);  // Tell parent about typed text
};
```

Freetext search works without blur or dropdown selection.

**File:** `components/activities/shared/DayTripLocationSearch.js:26-28` (RC-3).

See [[activities-location-search-bug-2026-06-01]] F-2.

## Severity Escalation

P1 per FQ-2 in [[activities-day-tour-page-review-2026-06-01]] — escalated from P2 due to interaction with `useDayTripFilters` hydration pattern. RTK Query dedup makes excess calls cheap, so always emit on every keystroke. Companion to [[mui-autocomplete-inputvalue-sync]].

## Related
- [[activities-location-search-bug-2026-06-01]]
- [[activities-day-tour-page-review-2026-06-01]] FQ-2
- [[mui-autocomplete-inputvalue-sync]]