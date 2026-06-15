# r1 — Technical SEO Findings (Trip Detail)

> Raw specialist output. Page: `/trips/detail/[...slug]` (transport). Synthesis → [[r2-leader-synthesis]].
> Caveat: WebFetch can't reach localhost; findings source-derived from the deterministic SEO emitter chain, file:line verified.

**11 findings — 3 HIGH, 5 MED, 3 LOW.**

## HIGH

### Canonical can render `http://localhost:3000`, never forced to www-HTTPS
Canonical built from raw `NEXT_PUBLIC_DOMAIN`, no runtime guard. Dev emits `http://localhost:3000/...`; any misconfigured-env deploy silently ships wrong-protocol/non-www canonical, violating `docs/operations/SEO.md`.
- Evidence: `pages/trips/detail/[...slug].js:123,127` → `hooks/useTripSEO.js:75` → `components/review/seo.js:53`. Env: `.env.local:6`.
- Fix: route canonical through `getSiteUrl()` (`utils/blog/seoHelper.js`), hard-default `https://www.smartenplus.co.th`.

### No BreadcrumbList JSON-LD (breadcrumbs visual-only)
Visible breadcrumb renders but emits no structured data → loses breadcrumb rich result. `NextBreadcrumbs.js` is MUI-only. `TripDetailSEO.js` docstring falsely claims breadcrumb schema.
- Evidence: `components/UI/NextBreadcrumbs.js` (no script tag); `components/trips/detail/TripDetailSEO.js:59-64` renders only NextSeo+ProductJsonLd; false docstring `:11-15`.
- Fix: reuse `components/SEO/JsonLd.js`, build BreadcrumbList from `customBreadcrumbPath` (`[...slug].js:116-119`), absolute URLs via `getSiteUrl()`.

### Product `offers` malformed in fallback path (empty `shippingDetails`/`hasMerchantReturnPolicy`)
Fallback offer shape emits empty `{}` objects → Google "invalid object" warnings. (Mitigated: page `noindex` when `lowestRate===null`, so fallback is non-indexable — dead but risky shape.) The `lowestRate` single-Offer override is valid.
- Evidence: `components/review/formattedRateData.js:25-26`; override `useTripSEO.js:197-209`; noindex guard `[...slug].js:312-314`.
- Fix: drop the two empty keys in `formattedRateData.js`.

## MED

### Product `description` = title (real description discarded)
`productProperties.js:96` sets Product `description` to title, duplicating product name; the genuine `route_info`-derived description is computed but ignored.
- Evidence: `components/review/productProperties.js:94,96`; real desc `[...slug].js:139-151`.
- Fix: pass the `description` param (already received `:64`) into the description property.

### Title leads with price, no length cap, no brand; meta desc cut mid-word
Title `${routeName} | THB ${rate}` — no cap, no site-name. Long Thai names overflow SERP. Meta desc raw `.substring(0,155)+'...'` cuts mid-word.
- Evidence: `[...slug].js:133-137` (title), `:139-151` (desc).
- Fix: append brand via `appSiteName`, truncate desc on word boundary.

### Duplicate/conflicting `robots` + `viewport` meta
Hand-rolled `robots` competes with NextSeo's own; `viewport` injected twice (hook + seo.js).
- Evidence: robots `useTripSEO.js:144-147`; viewport `useTripSEO.js:178-182` AND `seo.js:56-59`.
- Fix: drop manual robots (use NextSeo `robotsProps`), single viewport source.

### Catch-all detail pages depend entirely on server-sitemap.xml
`/trips/detail` index excluded (correct). But `fallback:'blocking'` pre-renders only 20; long-tail discoverability hinges on `server-sitemap.xml`. If it omits transport products → orphaned indexable pages.
- Evidence: `next-sitemap.config.js:25` (index-only exclude, no `/trips/detail/*` glob); server sitemap `:10-11`, `robots.txt:17`; paths `[...slug].js:425-457`.
- Fix: confirm `server-sitemap.xml` enumerates transport slugs (out of file scope; verify dynamic route).

### CWV: ISR shell + immediate CSR refetch on mount
Two hydration round-trips: full `/product-detail/` refetch for reviews only + RTK `refetchOnMountOrArgChange:true` for fares → CLS/INP risk.
- Evidence: `[...slug].js:74-80` (full payload for reviews), `:93-97`.
- Fix: scope reviews refetch to reviews-only endpoint or drop if ISR carries them; keep min-height loaders (`:29`) on review/related sections.

## LOW

### Hero LCP image `fill`, no intrinsic dims; alt can be empty
`<Image fill priority>` — CLS prevented only by parent `min-h`. `alt={productData?.trip_route}` can be undefined on shell.
- Evidence: `components/UI/FeaturedImageHeader.js:18-21,114`; alt `TripDetailHero.js:51`.
- Fix: deterministic alt fallback.

### aggregateRating omits bestRating, unrounded ratingValue
Correctly gated behind reviews>0 (good), but no `bestRating` and raw avg (`4.3333`); per-review schema already has bestRating.
- Evidence: `productProperties.js:100-106`; `reviews.js:22-24`.
- Fix: round to 1 decimal, add `bestRating:'5'`.

### Dead `keywords` meta + dead OG alt boilerplate
`keywords` emitted twice (ignored by Google); base OG alt sentence overridden by hook.
- Evidence: `useTripSEO.js:136-139` + `seo.js:61-64`; OG alt `seo.js:80` overridden `useTripSEO.js:78-86`.
- Fix: optional cleanup, no indexing risk.
