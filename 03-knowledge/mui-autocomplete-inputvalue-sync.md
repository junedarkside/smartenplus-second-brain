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

See [[activities-location-search-bug-2026-06-01]] F-1.

## Related
- [[activities-location-search-bug-2026-06-01]]
- React: prop updates must trigger effect, not be ignored