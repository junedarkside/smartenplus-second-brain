# Trip Detail — SEO / AEO / GEO Audit (Synthesis)

## Summary
3-specialist audit of the transport trip-detail page (`/trips/detail/[...slug]`). **25 raw findings → 18 unique** after dedup. The page has solid Product JSON-LD + OpenGraph foundations but: (1) canonical can ship wrong in non-prod, (2) most claimed schema is never rendered, (3) it is hardcoded Thailand-only against Europe/USA/Asia targets, (4) route facts are trapped in UI widgets answer engines can't read.

Raw notes: [[r1-seo]] · [[r1-aeo]] · [[r1-geo]].

> **Scrutiny pass (2026-06-16):** leader hand-traced the 6 load-bearing findings against source post-audit. 5 confirmed; **1 corrected** — malformed-offers downgraded **HIGH→MED** (the empty-`{}` offer is the *base* offer always set, overridden on the happy path; the `lowestRate===null` case early-returns a noindex page that renders no SEO at all, so the bad offer only escapes on the narrow `0`/`NaN`/`undefined` edge). **HIGH count 8 → 7.** All other file:line cites verified real: docstring lie, no BreadcrumbList, canonical no-guard, no hreflang (`seo.js:66` favicon-only), description=title, aggregateRating gate.

## Context
Trip detail is a booking/conversion money page. Search + answer-engine + international visibility directly drive traffic and revenue. No prior SEO/AEO/GEO audit existed for this route. Audit was read-only (code + intended live URL); **WebFetch could not reach `localhost`**, so all findings are derived from the deterministic SEO emitter chain (`[...slug].js` → `TripDetailSEO.js` → `useTripSEO.js` → `productProperties.js`/`seo.js`) with file:line verification. A live rich-results test on the production URL is still recommended to confirm rendered output.

## Cross-cutting root cause (flagged by ALL 3 specialists)
**`components/trips/detail/TripDetailSEO.js:11-15` docstring claims it emits Breadcrumb, Organization, LocalBusiness, FAQ, and TouristTrip schema — it renders only `<NextSeo>` + `<ProductJsonLd>` (`:59-64`).** Every "missing schema" finding below traces to this gap between documented intent and actual render. The components to fulfill the promise already exist (`JsonLd.js`, `LocalBusinessSchema.js`, `generateFAQSchema`, `generateProviderSchema`) — this is wiring, not new authorship. Fix the docstring too; it is actively misleading.

## Findings by severity

### HIGH
- **[SEO] Canonical can render `http://localhost:3000` / non-www** — no runtime guard on `NEXT_PUBLIC_DOMAIN`. `[...slug].js:123,127` → `seo.js:53`. Fix: `getSiteUrl()`.
- **[SEO] No BreadcrumbList JSON-LD** — visual breadcrumb only. Fix: reuse `components/SEO/JsonLd.js` + `customBreadcrumbPath` (`[...slug].js:116-119`).
- **[AEO] No FAQPage schema** — `generateFAQSchema` (`dayTripSEOUtils.js:320-359`) + `RouteFAQ.js` already prove the pattern on other surfaces. Fix: detail-scoped FAQ builder via `productData`, emit `FAQPageJsonLd`.
- **[AEO] Generic Product, no TouristTrip/Trip** — engines can't read trip semantics. Fix: add Trip block, reuse `generateProviderSchema` for provider node.
- **[AEO] Route facts trapped in tooltips/tables/badges** — no extractable prose; empty `<h2>` at `TripDetailContent.js:139`. Fix: FAQ answers + fill h2 + one factual summary sentence.
- **[GEO] og:locale hardcoded `th_TH`** — suppresses non-Thai surfaces. Fix: derive + `og:locale:alternate`.
- **[GEO] No hreflang alternates** — `FrontPage/Seo.js:26-41` has the pattern. Fix: replicate `additionalLinkTags` per target locale.

### MED
- **[SEO] Malformed `offers` (empty `{}` keys)** — *downgraded from HIGH post-scrutiny.* Base offer always = `formattedRateData` (`productProperties.js:88,107` + `formattedRateData.js:25-26`); only escapes to a crawlable page on the `lowestRate` `0`/`NaN`/`undefined` edge (the `null` case noindex-early-returns, `[...slug].js:309-327`). Fix: delete the two empty keys.
- **[SEO] Product `description` = title** — real description discarded (`productProperties.js:96`).
- **[SEO] Title no cap/brand; meta desc cut mid-word** (`[...slug].js:133-151`).
- **[SEO] Duplicate robots + viewport meta** (`useTripSEO.js:144-147,178-182` + `seo.js:56-59`).
- **[SEO] Long-tail detail pages depend wholly on `server-sitemap.xml`** — verify it enumerates transport slugs.
- **[SEO] CWV: ISR shell + 2 CSR refetches on mount** (`[...slug].js:74-80,93-97`).
- **[AEO] aggregateRating CSR-only** — may be absent from crawled HTML; ensure SSR carries `productData.reviews`.
- **[GEO] Currency THB-only** — keep THB primary; add FX hint only with a real conversion source.
- **[GEO] LocalBusiness/Place schema unused** — wire `LocalBusinessSchema.js` in; note data-shape mismatch (`location_name`+coords vs flat station strings, no coords).
- **[GEO] geo.placename `'Thailand'` fallback** dilutes place anchor.

### LOW
Hero LCP `fill` empty-alt risk · aggregateRating missing `bestRating`/unrounded · dead `keywords` + OG-alt boilerplate · operator/stations not typed (auto-fixed by Trip schema) · "Language Support" lone i18n signal · GTM `view_item` currency hardcoded THB.

**Keep as-is (verified correct, do not "fix"):** `geo.region: TH` (legit physical-location signal), aggregateRating gated behind reviews>0 (avoids fake-rating penalty), THB as settlement currency, `noindex` when `lowestRate===null`.

## Prioritized action list (impact × effort)

| # | Action | Impact | Effort | Reuse |
|---|--------|--------|--------|-------|
| 1 | Force canonical through `getSiteUrl()` + hard HTTPS/www default | High | XS | `utils/blog/seoHelper.js` |
| 2 | Fix `TripDetailSEO.js` docstring to match reality | High (prevents false confidence) | XS | — |
| 3 | Add BreadcrumbList JSON-LD | High | S | `components/SEO/JsonLd.js` |
| 4 | Add FAQPage (detail-scoped) | High | S | `generateFAQSchema`, `RouteFAQ.js` |
| 5 | Add hreflang alternates + og:locale:alternate | High | S | `FrontPage/Seo.js:26-41` |
| 6 | Delete empty offer `{}` keys (edge-case, was HIGH → MED) | Low-Med | XS | `formattedRateData.js` |
| 7 | Fill empty `<h2>` + factual summary sentence | Med | S | `productData` fields |
| 8 | Add TouristTrip/Trip schema (provider+Place) | High | M | `generateProviderSchema`, `LocalBusinessSchema.js` |
| 9 | Pass real `description` to Product; title brand+cap; word-boundary desc | Med | S | — |
| 10 | De-dup robots/viewport; ensure SSR reviews | Med | S | NextSeo `robotsProps` |
| 11 | LOW cleanup batch | Low | S | — |

Sequence: 1-5 first (each ≤S effort, high impact, all reuse existing helpers), then 6-10, batch LOW last.

## Verification (when fixes land — separate task)
- Production URL through Google Rich Results Test + Schema.org validator → confirm Product, BreadcrumbList, FAQPage, Trip all parse, zero offer warnings.
- `view-source` the prod page → canonical is absolute `https://www.smartenplus.co.th/...`; hreflang tags present; `og:locale:alternate` present.
- Crawl prod page with JS disabled → aggregateRating + route facts present in SSR HTML (not CSR-only).
- Confirm `server-sitemap.xml` lists transport `/trips/detail/<slug>` URLs.
- Re-run this audit's file:line cites post-fix to confirm no regression in the emitter chain.

## Related
[[r1-seo]] · [[r1-aeo]] · [[r1-geo]] · [[index]]
