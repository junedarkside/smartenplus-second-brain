---
name: activities-location-search-inputvalue-divergence
description: `inputValue` state never emits to parent component. User selects location → state updates locally → parent never receives selection → search never executes. Component encapsulation bug.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: activities-location-search-bug
---

# Activities Location Search — inputValue Divergence

## Summary
`inputValue` state never emits to parent. User selects location → local state updates → parent never receives selection → search never executes. Component encapsulation bug.

## Why It Matters
Location search doesn't work. User picks "Chiang Mai" → nothing happens. Frontend-backend communication broken.

## Detail
**Bug pattern:**
```jsx
// DayTripLocationSearch.js:26
const [inputValue, setInputValue] = useState('');

const handleSelect = (location) => {
  setInputValue(location.name);  // Local only
  // MISSING: onLocationSelect(location) callback
};

return (
  <Autocomplete
    value={inputValue}
    onChange={(e, val) => setInputValue(val.name)}  // Local only
    // MISSING: onChange prop to parent
  />
);
```

**Fix:**
```jsx
const DayTripLocationSearch = ({ onLocationSelect }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSelect = (location) => {
    setInputValue(location.name);
    onLocationSelect(location);  // Emit to parent
  };

  return (
    <Autocomplete
      value={inputValue}
      onChange={(e, val) => {
        setInputValue(val?.name || '');
        if (val) onLocationSelect(val);  // Emit to parent
      }}
    />
  );
};
```

## Constraints / Gotchas
Parent must pass `onLocationSelect` callback. Component is controlled — value comes from prop OR local state.

## Related
- [[activities-location-search-backend-text-id-type-mismatch]] — companion bug
- [[activities-location-search-bug]] — parent audit
