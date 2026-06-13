# useDayTripFilters — Hydration + Spurious Push Bug

**Problem:** `useState` reads `router.query` during mount, before hydration. `router.query === {}` pre-hydration → all filters init to defaults (DAY_TOUR, null). Then `useEffect` fires `router.push` with defaults → overwrites actual URL params on every page load.

**Example:** URL has `?category=SPA_WELLNESS` → page loads → init to DAY_TOUR → push → URL becomes `?category=DAY_TOUR`.

**File:** `hooks/useDayTripFilters.js:16–43`

**Fix:** Gate state + push on `router.isReady`:
```js
const [filters, setFilters] = useState(DEFAULT_FILTERS);

useEffect(() => {
  if (!router.isReady) return;
  setFilters(fromQuery(router.query));
}, [router.isReady]);
```

Prevent spurious push — check URL params changed before calling `router.push`.

**Severity:** P1. Interacts with UX-5 ("All" chip state loss).

Part of [[activities-day-tour-page-review-2026-06-01]] findings. See [[nextjs-hydration-rules]] for hydration patterns.

## FQ-2 Severity

Confirmed in [[activities-day-tour-page-review-2026-06-01]] — interacts with [[mui-autocomplete-handlInputchange-parent-emit]] to amplify URL-overwrite bug. Specified fix: `useState(DEFAULT_FILTERS) + useEffect(() => { if (!router.isReady) return; setFilters(fromQuery(router.query)); }, [router.isReady])`.

## Related
- [[activities-day-tour-page-review-2026-06-01]] FQ-2
- [[activities-location-search-bug-2026-06-01]]
- [[nextjs-hydration-rules]]
- [[mui-autocomplete-handlInputchange-parent-emit]]
- CLAUDE.md: "useEffect chains forbidden"
