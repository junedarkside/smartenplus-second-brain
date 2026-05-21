# Next.js Patterns

## Summary
Patterns learned from SmartEnPlus Next.js 14 app. Pages Router, Redux Toolkit, RTK Query, ISR, dynamic imports.

## ISR Cache
Trip detail pages use `revalidate: 300` (5 min). Cache cleared on deploy via Docker volume cleanup (`smartenplus_next_cache`). Without volume cleanup, ISR persists stale content across deploys.

## Dynamic SSR Disable
`dynamic(() => Promise.resolve(Index), { ssr: false })` for pages that depend on client-side state (cart, auth). Never add `getServerSideProps` to these pages.

## RTK Query
- `refetchOnMountOrArgChange: false` — prevents 429 on frequently-visited pages
- `skip` for conditional queries — don't fetch until params ready
- Transform data in RTK endpoint, not in components
- `next/image` always, never raw `<img>`

## DatePicker Handling
Store Date objects in Formik. Format to string ONLY at API boundary. Storing strings in Formik causes comparison bugs and timezone issues.

## State Management Rule
- `useState` — UI-only state (modals, tabs, form inputs)
- Redux — cross-component state (cart, auth, checkout)
- `useMemo` — derived values inline
- Max 3 prop levels before moving to Redux

## Component Patterns
- Named exports only
- Fetch in parent, pass as props
- Hook when logic >20 lines or reused across components
- `next/dynamic` + `ssr: false` for heavy components
- No inline objects/arrays in render (causes re-renders)

## Error Handling
Helpers return `null` + `console.warn`. Never throw from utilities. Guard clauses at function tops.

## Redux Fallback Props Pattern

Components that read Redux state can show stale/empty data on fresh page load (cold Redux). Pattern: accept URL-derived values as props, use `reduxValue || propValue`. Implemented in `StickySearchBar` (reads `state.location.from_location/to_location`; fallback to `fromSearch`/`toSearch` props from `FilterTripsPage`). `SearchCover` uses same pattern (`fromLocationRedux || initialFromLocation`). Rule: Redux wins when populated; URL/prop is fallback. Never dispatch to Redux just to fix display — pass as prop instead.

## Hydration Error Prevention

Hydration mismatch in a module imported by `_app.js` causes Next.js HMR to reload ALL pages, not just the affected page. Appears as "infinite page refresh across whole project."

**Rule 1 — No dynamic values in render:**
`Date.now()`, `new Date()`, `Math.random()` during render = server value ≠ client value = mismatch.
Fix: move to module-level constant (computed once at module load — same value server + client).
```js
// BAD — inside component or inline in JSX
"priceValidUntil": new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
// GOOD — module level
const PRICE_VALID_UNTIL = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
```

**Rule 2 — No dual JSX trees via isClient:**
`isClient ? <TreeA> : <TreeB>` = two different DOM structures = hydration mismatch on every page.
Fix: use `PersistGate loading={null}` directly — it renders `null` during SSR, then children after rehydration. No mismatch.
```js
// BAD
const [isClient, setIsClient] = useState(false);
useEffect(() => setIsClient(true), []);
return isClient ? <PersistGate>...</PersistGate> : <...without PersistGate...>
// GOOD
return <PersistGate persistor={persistor} loading={null}>...</PersistGate>
```

**Rule 3 — Memoize context value objects:**
`const value = { a, b, c }` inside provider = new object ref every render = all consumers re-render.
Fix: `useMemo(() => ({ a, b, c }), [a, b, c])`.

**Rule 4 — Memoize render-prop functions:**
Passing inline function as `renderItem` prop = new ref every render = `memo()` on child is bypassed.
Fix: wrap in `useCallback` with correct deps.

**Rule 5 — useRouter() IS stable:**
`router` from `useRouter()` returns a stable ref — NOT a new object each render. Safe in useCallback deps. (Common agent hallucination — verify against Next.js docs before removing.)

**Rule 6 — RTK Query refetchOnMountOrArgChange unit:**
`refetchOnMountOrArgChange: 300` = 300 **seconds** (5 min), NOT milliseconds. Not a re-render loop trigger.

See [[hydration-infinite-refresh-fix-2026-05-20]] for full investigation report.

## Related
- [[architecture]]
- [[payment-integration]]
- [[hydration-infinite-refresh-fix-2026-05-20]]
