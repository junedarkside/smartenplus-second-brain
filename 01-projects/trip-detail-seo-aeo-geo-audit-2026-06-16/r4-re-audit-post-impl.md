# r4 — Re-Audit Post-Implementation (Trip Detail SEO/AEO/GEO)

> Verification of the 7 HIGH fixes from [[r2-leader-synthesis]], implemented on `feat/trip-detail-seo-aeo-geo-fix`.
> Source-derived (WebFetch blocked on localhost). All file:line citations verified by 3 specialists.

## Overall verdict: 7/7 HIGH fixed. 1 PARTIAL (code smell, not a broken output).

---

## SEO (3 findings)

### PASS — Canonical via getSiteUrl()
`generateTripSEOConfig` (`tripDetailSEOUtils.js:7,28`) imports and uses `getSiteUrl()` not raw env.
`const canonical = \`${getSiteUrl()}/trips/detail/${slug}\``
Known dev-localhost caveat is pre-existing (inherent to `NEXT_PUBLIC_*`, not introduced by this fix). Prod env correct.

### PASS — BreadcrumbList JSON-LD
`TripDetailSEO.js:1,29` imports and renders `<BreadcrumbJsonLd itemListElements={breadcrumbItems} />`.
`generateTripBreadcrumbItems` (`tripDetailSEOUtils.js:95-102`) returns 3-item array with `position`/`name`/`item`, all absolute URLs via `getSiteUrl()`. Flows `getStaticProps:463` → `seoProps` → component. Correct.

### PASS — TripDetailSEO.js docstring now accurate
Old docstring claimed LocalBusiness/TouristTrip/FAQ/Breadcrumb/Organization — none rendered.
New docstring (`TripDetailSEO.js:7-24`) lists exactly: NextSeo, ProductJsonLd, BreadcrumbJsonLd, FAQPageJsonLd, CustomJsonLd. Matches actual render (`:25-33`). Truthful.

**Minor note (code smell, not defect):** `CustomJsonLd` (`helpers/JsonLd.js:7-9`) injects `@context`/`@type` then spreads productProps; `generateTripJsonLd` also includes `@context`/`@type` in its return — duplicate keys. `JSON.stringify` takes last value (both `'TouristTrip'`), so output is correct. Should be fixed for contract clarity but not a SEO defect.

### PASS — UI regressions: none
`lowestRate` (`[...slug].js:126`), `coverImage` (`:176-179`), h1 route name — all still present. `useTripSEO.js` deleted, no remaining imports anywhere in app code.

---

## AEO (3 findings)

### PASS — FAQPage schema
`generateTripFAQItems` (`tripDetailSEOUtils.js:104-126`) returns 4 `{ question, answer }` pairs built from live `productData` fields (stations, operator, rate, times). No hardcoded placeholders. `faqItems` in `seoProps` (`[...slug].js:464`). `TripDetailSEO.js:30` renders `<FAQPageJsonLd mainEntity={faqItems} />` conditionally. Schema in SSR HTML — AEO root cause fixed.

### PARTIAL — TouristTrip schema (correct output, messy contract)
Schema renders correctly: `@type: 'TouristTrip'`, `departureLocation`/`arrivalLocation` as `Place`, `provider` as `TravelAgency`, conditional `departureTime`/`arrivalTime`. All required fields present (`tripDetailSEOUtils.js:72-93`). Output validates.
**Issue:** `generateTripJsonLd` returns full JSON-LD object including `@context`/`@type`; `CustomJsonLd` also injects them. Duplicate keys — last-value-wins via JSON.stringify, both happen to be `'TouristTrip'`. Output correct, contract muddled. MED cleanup item for follow-up.

### PASS — Route facts prose
`TripDetailContent.js:139-162`: `<h2>` now populated (`data?.route?.route_name || data?.trip_route || ''`). `<p>` summary sentence sits above `route_info` HTML, built from route/station/time/operator fields, filtered for missing data, renders only when route_name or departure_station exists. No hardcoded content. Crawler-extractable.

---

## GEO (2 findings)

### PASS — og:locale:alternate key spelling
`tripDetailSEOUtils.js:34`: `localeAlternate: ['en_US','en_GB','de_DE','fr_FR','en_SG']` — correct next-seo v6 spelling (no trailing 's'). 5 market alternates. Agent C fixed the wrong-key bug from Agent A.

### PASS — hreflang alternates
`tripDetailSEOUtils.js:42-46`: 6 entries — `th`, `en`, `de`, `fr`, `en-SG`, `x-default`. All `href` = canonical (absolute via `getSiteUrl()`). `x-default` last (correct per Google guidance). Extends reference pattern from `FrontPage/Seo.js:26-41` (was 2 entries: th + x-default only) to full international set. Propagates clean: `getStaticProps:460` → `seoProps.seoConfig` → `TripDetailSEO.js:27` → `<NextSeo {...seoConfig} />` no filtering.

---

## Outstanding (not in this pass — MED/LOW deferred)

- `generateTripJsonLd` / `CustomJsonLd` contract: remove `@context`/`@type` from the return value, let CustomJsonLd inject them. MED cleanup.
- `formattedRateData.js:25` empty `{}` offer keys — still in file but unreachable from trip-detail flow (productProperties.js no longer called here). MED.
- Title/desc formatting, robots/viewport dedup, server-sitemap enumeration, SSR reviews, LocalBusiness, GTM currency — all deferred LOW/MED.

## Related
[[r2-leader-synthesis]] · [[r3-implementation-plan]] · [[r1-seo]] · [[r1-aeo]] · [[r1-geo]]
