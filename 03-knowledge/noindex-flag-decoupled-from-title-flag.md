# Decouple the robots flag from the title flag

## Summary
One boolean (`dataValid` = overview rows exist) drove both `noindex` and the price title. Widening it to fix indexing would print "from THB null". Keep the flags separate.

## Context
`/trips/koh-phi-phi/ao-nang` served `noindex,follow` while listed in the sitemap. API `routes[]` = `RouteByLocationInfo` (editorial overview/FAQ), `contracts[]` = sellable trips. 227 of 354 sitemap pairs had routes=0 but contracts>0. `createSeo(..., dataValid)` uses the same value for `formatTitle` ("from THB ${minRate}"); contracts-only pages have `minRate: null`.

## Decision
Leave `createSeo` signature and `dataValid` alone; override only the robots field in `hooks/useRouteSeo.js`:
`noindex: !(data?.length || contracts?.length)`. Product call (user): pages without editorial info but with real inventory should be indexed. Pages with routes=0 AND contracts=0 already `notFound`.

## Tradeoffs
- Contracts-only pages get the generic title/description (no price) and thin editorial content; backfill `RouteByLocationInfo` for high-traffic pairs later.
- Sitemap filter (BE `has_route_info`) became unnecessary: sitemap and robots now agree.

## Verify
Test all three states (routes only, contracts only, neither) and assert no "null" in the title. Probe real API with a dev server (env override of `NEXT_PUBLIC_API_URL`, read-only GETs). ISR means prod lags up to 1 h (3600 s on contracts-only pages).

## Related
[[soft-404-api-returns-200-empty-payload]] · [[tiered-empty-page-noindex-strategy]] · [[next-seo-v6-robots-prop-broken]]
