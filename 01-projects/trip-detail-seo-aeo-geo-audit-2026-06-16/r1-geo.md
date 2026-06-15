# r1 — GEO (Geo-Targeting + Generative Locale) Findings (Trip Detail)

> Raw specialist output. Platform targets Europe/USA/Asia; page hardcoded Thailand. Synthesis → [[r2-leader-synthesis]].
> Caveat: source-derived (no live localhost DOM); file:line verified.

**8 findings — 3 HIGH, 3 MED, 2 LOW.**

## HIGH

### og:locale hardcoded `th_TH` for Europe/USA/Asia targets
Every page declares Thai as sole locale → engines/social read Thai as canonical audience, suppress in non-Thai surfaces, show Thai previews to foreign users.
- Evidence: `hooks/useTripSEO.js:88` (literal); no `og:locale:alternate` anywhere.
- Fix: derive locale + add `og:locale:alternate` (`en_US,en_GB,de_DE,fr_FR,en_SG`) via NextSeo `openGraph.localeAlternate`.

### No hreflang alternates (pattern exists, not replicated)
Zero `rel="alternate" hrefLang` tags → no signal locale variants exist; engines can't serve right URL per market. Homepage already solves this.
- Evidence: `TripDetailSEO.js:59-64` (no link tags); `useTripSEO.js:115-183` `additionalMetaTags` only, no `additionalLinkTags`; contrast `components/FrontPage/Seo.js:26-41` (th + x-default).
- Fix: replicate `additionalLinkTags` from `FrontPage/Seo.js:26-41` into `useTripSEO.js`, extend per target locale, href from `domainURL`.

### geo.region hardcoded `TH` — reinforces Thailand-only framing
Fixed `geo.region: TH` + `th_TH` doubles down on Thailand scope vs multi-market goal. NOTE: value is legitimate (trip physically in Thailand) — harm is absence of audience signals, not this tag.
- Evidence: `useTripSEO.js:118-121`.
- Fix: KEEP `geo.region: TH` (accurate physical-location signal); carry audience targeting via hreflang + og:locale:alternate above. Do NOT remove.

## MED

### Currency THB-only — no multi-currency signal for foreign markets
All price signals THB, no locale-aware hint → friction + weak commerce-snippet relevance for USD/EUR/GBP/SGD.
- Evidence: `useTripSEO.js:128-134,94-96`.
- Fix: THB is correct settlement currency, keep primary. Add secondary currency hint ONLY if a real FX helper exists — never fabricate conversions.

### Station Place/LocalBusiness schema exists but never wired in
`LocalBusinessSchema.js` (Place + PostalAddress + GeoCoordinates) fully built, imported nowhere → no machine-readable station entity.
- Evidence: grep finds only vault docs, zero .js imports; `TripDetailSEO.js:59-64` no Place; false docstring `:12-15`.
- Fix: import into `TripDetailSEO.js`. BUT data-shape mismatch — component expects `location_name`+`latitude`/`longitude` (`LocalBusinessSchema.js:16,33`), API gives flat strings `route.departure_station`/`arrival_station` (`[...slug].js:147-148`) no coords. Map fields or accept schema sans `geo`.

### geo.placename fallback dilutes to country
Correctly uses departure station (verified right anchor). Fallback to literal `'Thailand'` when absent adds nothing.
- Evidence: `useTripSEO.js:123-124`.
- Fix: low priority — fallback to route name/arrival station, keep primary as-is.

## LOW

### "Language Support: Thai, English" only i18n signal
No `inLanguage`/audience signal matching target locales.
- Evidence: `useTripSEO.js:226-228`.
- Fix: acceptable if accurate; pair with hreflang fix. No machine-translated claims.

### GTM view_item currency hardcoded THB — breaks market segmentation
Analytics misattributes all foreign-market views to THB; blocks Phase-4 regional revenue KPI.
- Evidence: `pages/trips/detail/[...slug].js:230`.
- Fix: source currency from same market resolver as og:locale.
