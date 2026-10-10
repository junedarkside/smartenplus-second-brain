# ISR Cold-Route Latency and the WP Fetcher Retry Footgun

## Summary
On `/trips/[from]/[to]` the first visitor to a route not in `getStaticPaths` waits for the whole `getStaticProps` (`fallback: 'blocking'`). Measured on prod 2026-10-10: `x-nextjs-cache: MISS` 1.2-4.4 s vs `HIT` 0.26-0.8 s. Same route is fast afterwards (revalidate 300 s).

## Context
Search click does `router.push`; Next fetches `/_next/data/<buildId>/<locale>/trips/<from>/<to>.json`. While that is pending the user stays on the homepage. Deploy clears `smartenplus_next_cache` (see CLAUDE.md gotcha), so every route is cold after each deploy. Related: [[destination-trips-slow-root-cause]], [[fetcher-graphql-envelope-footgun]].

## Rules learned
- Start independent upstream calls together (front-page, location labels, route API); await in the end. A promise that never rejects (own try/catch) is safe to await again in the `catch` block.
- `helpers/fetcher.js` defaults to `timeout 30000`, `retries 2`, delays 2 s/4 s: up to ~96 s per WP call inside a blocking render. In `getStaticProps` pass a short `timeout` and `retries: 0`, fail soft, and shorten `revalidate` (30 s) on ANY failed WP call (blog or FAQ), or missing content is cached 5 min.
- `router.push` returns a promise that settles when navigation completes or fails. Returning it from the search handler lets the button keep its spinner exactly as long as needed; a fixed 3 s reset made 4 s waits look frozen. Reset with `.then(done, done)` (no unhandled rejection).
- `router.prefetch` 100 ms before `push` gains nothing (push requests the same data); it does nothing in `next dev`.
- Local `next dev` hides the problem: local upstreams answer in 0.1-0.7 s. Measure on prod with 2 GETs per route (MISS then HIT), do not loop-curl.

## Open
Popular routes expected prebuilt still showed MISS on prod (cause unknown). Post-deploy warm-up script and prefetch-on-selection are not built.
