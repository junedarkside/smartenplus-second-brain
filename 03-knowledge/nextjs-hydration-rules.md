# Next.js Hydration Rules

## Summary
6 rules preventing hydration mismatches in Next.js 14 + PersistGate SSR blocker pattern. Mismatch in `_app.js` triggers HMR infinite refresh across all pages.

## Context
Extracted from [[nextjs-patterns]]. Discovered during [[hydration-infinite-refresh-fix]] + [[og-image-ssr-fix-2026-05-23]].

## Details

### Rule 1 — No dynamic values in render
`Date.now()`, `new Date()`, `Math.random()` in render = server ≠ client = mismatch. Fix: module-level constant.
```js
// BAD — inside component
"priceValidUntil": new Date(Date.now() + 365*24*60*60*1000).toISOString().split('T')[0]
// GOOD — module level
const PRICE_VALID_UNTIL = new Date(Date.now() + 365*24*60*60*1000).toISOString().split('T')[0];
```

### Rule 2 — No dual JSX trees via isClient
`isClient ? <TreeA> : <TreeB>` = mismatch. Fix: `<PersistGate persistor={persistor} loading={null}>` directly.

### Rule 3 — Memoize context value objects
`{ a, b, c }` in provider = new ref each render. Fix: `useMemo(() => ({ a, b, c }), [a, b, c])`.

### Rule 4 — Memoize render-prop functions
Inline `renderItem` = new ref = bypasses `memo()`. Fix: `useCallback` with correct deps.

### Rule 5 — useRouter() IS stable
Stable ref, not new object each render. Safe in useCallback deps.

### Rule 6 — refetchOnMountOrArgChange semantics
`300` (number) = "refetch if cached data older than 300 seconds" — fires immediately on cold mount, no cache. Use `true` = refetch on arg change. Use `false` = no refetch. Never pass number unless explicitly want time-based stale cache refetch.

### PersistGate SSR Blocker

`PersistGate loading={null}` renders **null on server**. Any component inside — `DefaultSeo`, `Head`, `<Component>` — suppressed during SSR. Result: `next-head-count="2"`, empty `<title>`, no OG tags in view-source.

**Symptom:** opengraph.dev / view-source shows empty meta tags on ALL pages.

**Diagnosis:** `curl http://localhost:3000/ | grep 'next-head-count'` → `content="2"` = SSR blocked.

**Fix:** hoist `DefaultSeo`, `Head`, `Layout`, `<Component>` above `PersistGate`. Wrap only client-only utilities (RefreshTokenHandler, DevToolsProvider) inside PersistGate.

```jsx
// BAD — everything suppressed SSR
<PersistGate persistor={persistor} loading={null}>
  <DefaultSeo ... />
  <Layout><Component {...pageProps} /></Layout>
</PersistGate>

// GOOD — meta + page render SSR; persist wraps only client utilities
<DefaultSeo ... />
<Layout>
  <PersistGate persistor={persistor} loading={null}>
    <RefreshTokenHandler ... />
    <DevToolsProvider />
  </PersistGate>
  <Component {...pageProps} />
</Layout>
```

Fixed in `_app.js` commit `ac6f8aa` — verified `next-head-count="14"` after fix.

## Related
- [[nextjs-patterns]] — parent note
- [[hydration-infinite-refresh-fix]]
- [[og-image-ssr-fix-2026-05-23]]
- [[persistgate-ssr-suppresses-head-component]]