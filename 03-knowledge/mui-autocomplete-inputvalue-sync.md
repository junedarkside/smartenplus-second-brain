# MUI Autocomplete — inputValue Doesn't Sync With value Prop

## Summary

MUI Autocomplete with local `inputValue` state initialized via `useState(value || '')` does NOT update when the controlled `value` prop changes after mount. The visible text field goes stale. Caused the location search invisible-on-URL-restore bug.

## Problem

```js
// WRONG — inputValue is only set once at mount
const [inputValue, setInputValue] = useState(value || '');

// When parent changes value prop (e.g. URL hydration sets location="Phuket"):
// → value prop = "Phuket"
// → inputValue still = ""
// → MUI renders blank text field
// → user sees no location despite filter being active
```

## Fix

Add a `useEffect` to sync `inputValue` whenever `value` prop changes:

```js
const [inputValue, setInputValue] = useState(value || '');

React.useEffect(() => {
  setInputValue(value || '');
}, [value]);
```

This covers:
- URL-restored filter state (router hydration post-mount)
- Parent programmatically resetting the field
- External navigation with pre-selected location

## When This Occurs

Any MUI Autocomplete component where:
1. `inputValue` is managed locally with `useState`
2. The `value` prop is controlled externally (Redux, URL params, parent state)
3. Value can change after initial mount (URL hydration, navigation)

## SmartEnPlus Instance

`components/activities/shared/DayTripLocationSearch.js:20` — location search field shows blank when URL has `?location=Phuket`. Fix applied in branch `260601-fix/activities-browse-audit`.

## Related

- [[activities-location-search-bug-2026-06-01]] — RC-2 root cause
- MUI Autocomplete docs: `inputValue` (uncontrolled display) vs `value` (controlled selection) are separate concerns
