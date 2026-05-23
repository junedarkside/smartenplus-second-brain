# Next.js Patterns

## Summary
SmartEnPlus Next.js 14 patterns. Pages Router, Redux Toolkit, RTK Query, ISR, dynamic imports.

## ISR Cache
Trip detail: `revalidate: 300` (5 min). Deploy clears `smartenplus_next_cache` Docker volume. Without volume cleanup, ISR persists stale across deploys.

**`revalidate` is ignored in `next dev`:** `getStaticProps` runs on every request in dev mode regardless of `revalidate` value. ISR only activates in production (`next build` + `next start`). Changing `revalidate` to fix local dev 429s is ineffective. Fix 429s in dev at the backend layer (response cache, throttle rate). See [[isr-429-cold-start-fix-2026-05-23]].

**`getStaticPaths` is build-time only:** Never runs during ISR revalidation at runtime. Only `getStaticProps` runs on ISR revalidation. A dynamic route's `getStaticPaths` hitting an API endpoint is a build concern, not a runtime 429 concern.

## Dynamic SSR Disable
`dynamic(() => Promise.resolve(Index), { ssr: false })` for pages depending on client state (cart, auth). Never add `getServerSideProps` to these.

## RTK Query
- `refetchOnMountOrArgChange: false` — prevents 429 on frequent pages
- `skip` for conditional queries — don't fetch until params ready
- Transform data in RTK endpoint, not components
- `next/image` always, never raw `<img>`

## DatePicker
Store Date objects in Formik. Format to string ONLY at API boundary. Strings in Formik → comparison bugs + timezone issues.

## State Management
- `useState` — UI-only (modals, tabs, inputs)
- Redux — cross-component (cart, auth, checkout)
- `useMemo` — derived values inline
- Max 3 prop levels → move to Redux

## Component Patterns
- Named exports only
- Fetch in parent, pass as props
- Hook when logic >20 lines or reused
- `next/dynamic` + `ssr: false` for heavy components
- No inline objects/arrays in render

## Error Handling
Helpers return `null` + `console.warn`. Never throw from utilities. Guard clauses at function tops.

## Redux Fallback Props
Fresh page load = cold Redux = stale/empty data. Pattern: accept URL-derived props, use `reduxValue || propValue`. `StickySearchBar`: `fromLocationRedux || fromSearch`. `SearchCover`: `fromLocationRedux || initialFromLocation`. Redux wins when populated; URL/prop is fallback.

## Hydration Error Prevention

Hydration mismatch in `_app.js` module → Next.js HMR reloads ALL pages ("infinite refresh").

**Rule 1 — No dynamic values in render:**
`Date.now()`, `new Date()`, `Math.random()` during render = server ≠ client = mismatch. Fix: module-level constant.
```js
// BAD — inside component
"priceValidUntil": new Date(Date.now() + 365*24*60*60*1000).toISOString().split('T')[0]
// GOOD — module level
const PRICE_VALID_UNTIL = new Date(Date.now() + 365*24*60*60*1000).toISOString().split('T')[0];
```

**Rule 2 — No dual JSX trees via isClient:**
`isClient ? <TreeA> : <TreeB>` = mismatch. Fix: `<PersistGate persistor={persistor} loading={null}>` directly.

**Rule 3 — Memoize context value objects:**
`{ a, b, c }` inside provider = new ref every render. Fix: `useMemo(() => ({ a, b, c }), [a, b, c])`.

**Rule 4 — Memoize render-prop functions:**
Inline `renderItem` prop = new ref = bypasses `memo()`. Fix: `useCallback` with correct deps.

**Rule 5 — useRouter() IS stable:**
Stable ref, NOT new object each render. Safe in useCallback deps.

**Rule 6 — refetchOnMountOrArgChange semantics:**
`300` (number) = "refetch if cached data older than 300 seconds" — triggers immediately on cold mount with no cache. Use `true` to mean "refetch when args change". Use `false` to prevent refetch entirely. Never pass a number unless you explicitly want time-based stale cache refetch behavior.

See [[hydration-infinite-refresh-fix-2026-05-20]].

## Related
- [[architecture]]
- [[payment-integration]]
- [[hydration-infinite-refresh-fix-2026-05-20]]
- [[isr-429-cold-start-fix-2026-05-23]]
