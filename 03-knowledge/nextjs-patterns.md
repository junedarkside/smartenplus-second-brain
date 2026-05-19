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

## Related
- [[architecture]]
- [[payment-integration]]
