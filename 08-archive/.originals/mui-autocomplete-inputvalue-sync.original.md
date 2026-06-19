# MUI Autocomplete — inputValue Not Syncing with value Prop

**Bug:** `useState(value || '')` initializes once. Prop changes after mount (URL hydration) are invisible.

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

Now URL-restored location visible in input field.

**Rule:** Never initialize state from prop unless prop is static. Use `useEffect` for prop→state sync.

See [[activities-location-search-bug]] F-1.

## Related
- [[activities-location-search-bug]]
- React: prop updates must trigger effect, not be ignored
