# Next.js shallow router.push — scroll:false for URL sync

## Summary
`router.push({...}, undefined, { shallow: true })` for URL sync on filter change ALSO scrolls to top by default. Add `scroll: false` to prevent jarring scroll jumps while user reads/scans content.

## Context
Next.js 14 Pages Router. Shallow routing updates URL bar without re-running `getStaticProps`/`getServerSideProps`. Default `scroll: true` mimics real navigation behavior. Filter hooks sync state→URL on every state change — multiple per second during debounce + scroll.

## Problem
`hooks/useDayTripFilters.js` URL sync effect fires on every filter state change. Without `scroll: false`, each push scrolls viewport to top:
- Type in search → debounced effect → URL push → page jumps to top
- Click pagination chip → URL push → page jumps to top
- Select sort option → URL push → page jumps to top

All wrong. Loses user's viewport on every interaction.

## Decision
```js
router.push({ pathname: router.pathname, query }, undefined, { shallow: true, scroll: false });
```
`scroll: false` is the right default for any URL sync that does not represent a real navigation (filter change, form edit, hash anchor). Pair with `shallow: true` so the route does not refetch data.

## Tradeoffs
- Pro: no scroll jumps, preserves user's viewport position
- Pro: small one-word change, low risk
- Con: may need explicit `window.scrollTo(0, 0)` in actual navigation handlers (separate from URL sync). Filter search and form edit are not "navigation" — they are state sync.

## Related
- [[react-state-no-op-guard-side-effect-prevention]] — sibling fix in same hook
- [[nextjs-hydration-rules]] — broader Next.js patterns
