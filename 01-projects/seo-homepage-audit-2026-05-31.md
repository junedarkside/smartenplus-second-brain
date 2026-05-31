# Homepage SEO Audit 2026-05-31

## Summary
3-specialist sequential audit of localhost:3000 homepage. 17 findings. 2 P0, 4 P1, 1 P2, 3 P3. Server-sitemap.xml handler missing (active 404). og:locale should be th_TH not en_US.

## Context
User invoked SEO team audit on homepage. Full 3-role specialist team: Structured Data → Technical SEO → Page Performance. Live page inspection via Playwright.

## Findings

### P0 — Correctness (breaks rich results or active 404)

**P0-1: server-sitemap.xml handler — REFUTED**
next-sitemap.config.js line 10 is `additionalSitemaps: []` (empty array). No reference to server-sitemap.xml exists. `pages/server-sitemap.xml.js` does not exist but no sitemap config points to it — no active 404. Claim of "explicitly-configured sitemap returning 404" was incorrect. **Downgrade to informational gap, not P0.**

**P0-2 (former P1-1): og:locale en_US → th_TH — CONFIRMED**

### P1 — Major gaps

**P1-1: og:locale en_US → th_TH**
Both `pages/_app.js:39` and `components/FrontPage/Seo.js:46` set `locale: 'en_US'`. Thailand-focused site should primary locale th_TH with en hreflang.

**P1-2: TravelAgency schema missing postalAddress**
`pages/homepagev2.js:238-264` — TravelAgency JSON-LD has `geo` with lat/lng (13.7563, 100.5018) but no `address` field. Schema.org TravelAgency requires address or geo or both. Add PostalAddress.

**P1-3: Security headers missing HSTS, CSP, Permissions-Policy**
`next.config.js` has only X-Frame-Options, X-Content-Type-Options, Referrer-Policy. Missing industry-standard 2026 headers.

**P1-4: FAQPage schema not wired**
`subcategoriesData` exists in `homepagev2.js:105` getStaticProps and `FAQPageJsonLd` component exists in `components/SEO/SEOSection.js` but homepagev2.js does not render SEOSection with `isFAQ` prop. FAQPage schema exists as reusable component but not wired to homepage.

**P1-5: FAQPage component doesn't exist yet**
`lib/homepage/components/FAQStructuredData.js` — referenced as create target in Fix Queue but component does not yet exist. subcategoriesData shape TBD — needs audit of data structure before component can be built.

### P2 — Performance

**P2-1: hero image sizes="100vw" at all breakpoints**
`helpers/imageOptimization.js:25` — mobile downloads desktop-resolution image. Change to `'(max-width: 768px) 100vw, (max-width: 1200px) 100vw, 1920px'`.

### P3 — Completeness

**P3-1: Missing contactPoint on TravelAgency**
**P3-2: PopularRoutesStructuredData BusTrip missing departureTime/arrivalTime**
**P3-3: ReviewsStructuredData uses LocalBusiness instead of TravelAgency**
**P3-4: LocationsStructuredData missing GeoCoordinates**

### Positive findings (no fix needed)

- TravelAgency aggregateRating correctly wired to `lastTopReviewData`
- TravelAgency telephone uses COMPANY_PHONE_NUMBER constant
- TravelAgency sameAs complete with all 3 social URLs
- WebSite SearchAction present targeting correct endpoint
- WebPageJsonLd lastReviewed dynamic (not hardcoded)
- robots.txt Allow/Disallow order correct
- sitemap.xml correctly formatted as sitemapindex
- preconnect for GTM + dns-prefetch for S3 origins present
- ColorThief uses requestIdleCallback (non-blocking)
- next.config.js compress:true and standalone present
- minimumCacheTTL for images 24h
- Next.js 14.2.5 auto-adds fetchpriority when priority=true

## Scrutiny Corrections

| Finding | Original | Corrected | Reason |
|---------|----------|----------|--------|
| P0-1 server-sitemap.xml | P0 — active 404 | informational gap | next-sitemap.config.js line 10 is `additionalSitemaps: []` — no reference to server-sitemap.xml. Handler missing but no active 404 from config. |
| P1-4 FAQPage | "not implemented" | "not wired" | FAQPageJsonLd component exists in components/SEO/SEOSection.js. Not rendered because homepagev2.js doesn't pass isFAQ prop. |

## Fix Queue

| Priority | Action | Files | Status |
|----------|--------|-------|--------|
| P0-1 | Informational — no active 404 from config. Consider creating server-sitemap.xml anyway for future dynamic routes | `pages/server-sitemap.xml.js` | Optional |
| P1-1 | Change locale to `th_TH` + en hreflang | `components/FrontPage/Seo.js:46`, `pages/_app.js:39` | Confirmed |
| P1-2 | Add postalAddress to TravelAgency JSON-LD | `pages/homepagev2.js:238-264` | Confirmed |
| P1-3 | Add HSTS, CSP, Permissions-Policy headers | `next.config.js` | Confirmed |
| P1-4 | Wire FAQPageJsonLd into homepagev2 via SEOSection with isFAQ prop | `pages/homepagev2.js` + `components/SEO/SEOSection.js` | DONE — resolved via direct FAQPageJsonLd render (not SEOSection), extended WP query with faqsPosts |
| P1-5 | Audit subcategoriesData shape before building FAQStructuredData | `pages/homepagev2.js:105` | DONE — WP query extended to fetch FAQ post title+content, transformed to question/answer |
| P2-1 | Cap hero image sizes | `helpers/imageOptimization.js:25` | Confirmed |
| P3-1 | Add contactPoint to TravelAgency | `pages/homepagev2.js` | Confirmed |
| P3-2 | Add departureTime/arrivalTime to BusTrip | `lib/homepage/components/PopularRoutesStructuredData.js` | Confirmed |
| P3-3 | Change ReviewsStructuredData to TravelAgency | `lib/homepage/components/ReviewsStructuredData.js:63` | Confirmed |
| P3-4 | Add geo coordinates to LocationsStructuredData | `lib/homepage/components/LocationsStructuredData.js` | Confirmed |

## Cross-Specialist Debates Resolved

| Debate | Verdict |
|--------|---------|
| server-sitemap.xml 404 priority | P0 — explicitly-configured sitemap returning 404, live production correctness issue |
| og:locale th_TH vs en_US | P1 — indirect ranking impact via user signals, not direct crawl issue |
| CLS from ssr:false form | Not a finding — homepagev2 DiscoverySection has no min-height constraint (homepagev1 had it) |

## Key Files

- `pages/server-sitemap.xml.js` (create)
- `components/FrontPage/Seo.js`
- `pages/_app.js`
- `pages/homepagev2.js`
- `next.config.js`
- `helpers/imageOptimization.js`
- `lib/homepage/components/FAQStructuredData.js` (create)
- `lib/homepage/components/LocationsStructuredData.js`
- `lib/homepage/components/PopularRoutesStructuredData.js`
- `lib/homepage/components/ReviewsStructuredData.js`

## Related

- [[seo-homepage-specialist-team]]
- [[homepage-seo-performance-deep-review-2026-05-21]]
- [[structured-data-schema-patterns]]
- [[homepage-ux-review-2026-05-21]]
- [[blog-seo-performance-2026-05-20]]
- [[og-image-inferred-audit-2026-05-23]]
- [[og-image-ssr-fix-2026-05-23]]

## Audit Metadata

- Date: 2026-05-31
- Scope: http://localhost:3000/ homepage
- Specialists: Structured Data, Technical SEO, Page Performance
- Method: 3-agent sequential review + Playwright live page inspection
- Agent: seo-homepage-auditor