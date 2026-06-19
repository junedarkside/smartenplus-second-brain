# MUI Autocomplete — inputValue Not Syncing with value Prop

**Bug:** `useState(value || '')` initializes once. Prop changes after mount (URL hydration) invisible.

**Example:**
```js
const [inputValue, setInputValue] = useState(value || '');  // ❌ One-time init
```

URL restores `value="Phuket"` → component mounts → `inputValue` stays empty. User sees blank field.

**Fix:**
```js
useEffect(() => {
  setInputValue(value || '');
}, [value]);  // Re-sync on value change
```

URL-restored location now visible in input.

**Rule:** Never init state from prop unless prop static. Use `useEffect` for prop→state sync.

See [[activities-location-search-bug]] F-1.

## Companion Pattern

Pairs with [[mui-autocomplete-handlInputchange-parent-emit]] — together form the "URL-hydrated search bar" recipe. FQ-2 (activities-day-tour-page-review) confirms both must be present; missing either yields blank field or unfiltered API calls.

## Related
- [[activities-location-search-bug]]
- [[activities-day-tour-page-review]] FQ-2
- [[mui-autocomplete-handlInputchange-parent-emit]]
- React: prop updates must trigger effect, not be ignored