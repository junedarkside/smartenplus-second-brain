# Trip Detail SEO/AEO/GEO — Implementation Plan (7 HIGH)

> Fixes the 7 HIGH findings from [[r2-leader-synthesis]]. Decisions locked via grill (synthesis §"Implementation decisions"). Scope: HIGH only; MED/LOW deferred.

## Context
The transport trip-detail page (`pages/trips/detail/[...slug].js`) generates all SEO **client-side** in `useTripSEO` hook on already-hydrated data, and renders only `<NextSeo>` + `<ProductJsonLd>` (`components/trips/detail/TripDetailSEO.js:59-63`) — despite a docstring claiming Breadcrumb/LocalBusiness/FAQ/TouristTrip schema. Result: missing schema + key signals absent from the SSR HTML crawlers and answer engines read.

**Strategy:** mirror the proven day-trip server-side pattern. The day-trip page generates SEO in `getStaticProps` via `helpers/seo/dayTripSEOUtils.js` and renders it through `components/activities/detail/DayTripDetailSEO.js`. We replicate that for trip-detail. `getStaticProps` already fetches the full `productData` (`[...slug].js:478`) — no new fetch.

## Reused helpers (verified present)
- `findLowestSellingRate` — `helpers/tripSorting.js:74`
- `getSiteUrl` — `utils/blog/seoHelper.js:3`
- `CustomJsonLd` — `helpers/JsonLd.js:1`
- `FAQPageJsonLd`, `BreadcrumbJsonLd`, `ProductJsonLd`, `NextSeo` — `next-seo@6.1.0`
- Pattern references (copy structure, don't import): `helpers/seo/dayTripSEOUtils.js`, `components/activities/detail/DayTripDetailSEO.js`

## Files

### NEW: `helpers/seo/tripDetailSEOUtils.js`
Modeled on `dayTripSEOUtils.js`. Pure functions, server-callable, all input = the `productData` object + `domainURL`. No React, no hooks.

- `generateTripSEOConfig({ productData, slug, domainURL })` → NextSeo config: title, description, canonical (`getSiteUrl()` + `/trips/detail/${slug}`), openGraph (incl. `locale: 'th_TH'` + `localeAlternate: ['en_US','en_GB','de_DE','fr_FR','en_SG']`), twitter, `additionalLinkTags` for hreflang (one `rel:'alternate'` per locale → same URL + `x-default`). **[fixes: canonical, og:locale:alternate, hreflang]**
- `generateProductJsonLd({ productData, domainURL })` → Product schema. Offer price via `findLowestSellingRate(productData)` from ISR ratecard. Drop the empty-`{}` keys. Pass the real `description` (not title). **[fixes: offer price source server-side]**
- `generateTripJsonLd({ productData, domainURL })` → **`TouristTrip`** (or `Trip`) schema: `departureLocation`/`arrivalLocation` as `Place`, `departureTime`/`arrivalTime`, `provider` as `TravelAgency` (operator), `offers` reuse. **[fixes: generic Product → TouristTrip]**
- `generateBreadcrumbItems({ productData, slug, domainURL })` → array for `BreadcrumbJsonLd`: Home → Trips → route_name, absolute URLs via `getSiteUrl()`. **[fixes: no BreadcrumbList]**
- `generateTripFAQSchema({ productData })` → FAQ Q&A array from `route_name`, stations, `duration`, `trip_departure_time`/`trip_arrival_time`, operator, ISR `lowestRate`. Questions: "How much is {from} to {to}?", "How long does {from} to {to} take?", "Who operates {route}?", "What time does it depart?". **[fixes: no FAQPage; route-facts-as-prose — answer strings are the extractable prose]**

### MODIFY: `pages/trips/detail/[...slug].js`
- In `getStaticProps` (`:499-502`): build the 5 SEO objects from `productData` and pass under a single `seo` prop alongside `productData`. Keep `revalidate:300`.
- Replace the `<TripDetailSEO .../>` call (`:330-344`) — pass the server-computed `seo` prop instead of the current per-field props. Remove now-dead client-side title/description/domainURL derivation that only fed SEO (keep any still used by visible UI, e.g. `title` for `<h1>`-adjacent display, `lowestRate` for price badge).
- **Route-facts prose (HIGH):** fill the empty `<h2>` at `components/itinerary/TripDetailContent.js:139-140` with the route name, and add one factual summary sentence above the `route_info` block, composed from `productData` fields. (Small edit in that component, not the page.)

### MODIFY: `components/trips/detail/TripDetailSEO.js`
Rewrite to the `DayTripDetailSEO` shape — accept server-built objects, render:
```jsx
<NextSeo {...seo.config} />
<ProductJsonLd {...seo.productJsonLd} />
<TouristTrip ... />            // via CustomJsonLd type="TouristTrip" or next-seo if available
<BreadcrumbJsonLd itemListElements={seo.breadcrumbItems} />
<FAQPageJsonLd mainEntity={seo.faq} />
{seo.providerJsonLd && <CustomJsonLd type="Organization" {...seo.providerJsonLd} />}
```
Fix the false docstring (`:11-15`) to match what is actually rendered.

### DELETE / SHRINK: `hooks/useTripSEO.js`
Once `getStaticProps` owns SEO, this hook is dead (or shrinks to nothing). Grep callers before deleting: `grep -rn "useTripSEO" --include=*.js` — should be only `TripDetailSEO.js`. Remove if sole caller.

## Build order
1. `tripDetailSEOUtils.js` (new, isolated — no risk).
2. Wire `getStaticProps` + rewrite `TripDetailSEO.js` together (they share the prop contract).
3. `TripDetailContent.js` h2 + summary sentence.
4. Delete `useTripSEO.js` if grep confirms sole caller.

## Out of scope (deferred to MED/LOW follow-up)
title/desc formatting, robots/viewport dedup, server-sitemap enumeration verify, SSR-reviews for aggregateRating, LocalBusiness Place wiring (needs station coords not in API), currency multi-signal, GTM currency, dead keywords, alt fallbacks, bestRating rounding.

## Caveats
- **Canonical:** `getSiteUrl()` returns `localhost` in dev (`NEXT_PUBLIC_DOMAIN`) and does not force HTTPS/www — prod env is already correct (`.env.production.sample`). Routing through it removes raw-env duplication + gives a safe missing-env default; it does not by itself rewrite a bad env. Acceptable for this fix; do not claim it "guarantees" canonical.
- **Schema price ≤5min stale** vs CSR-merged visible price — accepted (decision §4). Negligible mismatch risk.
- **TouristTrip type:** if `next-seo` has no first-class component, emit via `CustomJsonLd type="TouristTrip"` (helpers/JsonLd.js) — same mechanism day-trip uses for provider.

## Verification (end-to-end)
1. `npm run build` exit 0; build-log shows trip-detail static gen, no SEO util errors.
2. Run dev / preview, `view-source` a trip-detail page → confirm in **initial HTML** (not post-hydration): `<link rel="canonical">`, hreflang `alternate` tags + `x-default`, `og:locale:alternate`, and 4 JSON-LD blocks (Product, TouristTrip, BreadcrumbList, FAQPage).
3. Paste rendered URL into Google Rich Results Test → Product + Breadcrumb + FAQ + Trip parse, zero offer warnings (empty `{}` keys gone).
4. Crawl with JS disabled (curl the page) → FAQ answers + route facts present in HTML.
5. Regression greps: `grep -rn "useTripSEO"` returns nothing if deleted; `grep -n "shippingDetails: {}"` gone from offer path.
6. Visual smoke: price badge + `<h1>` still render (didn't break the UI removing dead SEO derivation).

## Related
[[r2-leader-synthesis]] · [[r1-seo]] · [[r1-aeo]] · [[r1-geo]]
