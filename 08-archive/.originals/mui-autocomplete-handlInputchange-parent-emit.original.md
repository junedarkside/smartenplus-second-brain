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

Now freetext search works without requiring blur or dropdown selection.

**File:** `components/activities/shared/DayTripLocationSearch.js:26-28` (RC-3).

See [[activities-location-search-bug]] F-2.

## Related
- [[activities-location-search-bug]]
