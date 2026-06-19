# Homepage SEO Audit 2026-05-31

## Summary
3-specialist sequential audit of localhost:3000 homepage. 17 findings. Scrutinize found P0-1 REFUTED, P1-4 clarified. All fixes re-applied one-by-one on `260528-feat/header-redesign-2026` (commit `a2a4ff9`). CSP header skipped — causes runtime break on this project.

## Context
User invoked SEO team audit on homepage. Full 3-role specialist team: Structured Data → Technical SEO → Page Performance.

## Findings

### P0 — Correctness

**P0-1: server-sitemap.xml handler — REFUTED**
next-sitemap.config.js line 10 is `additionalSitemaps: []` (empty). No reference to server-sitemap.xml. No active 404. Downgraded to informational gap.

### P1 — Major gaps

**P1-1: og:locale en_US → th_TH — DONE**
Both `pages/_app.js` and `components/FrontPage/Seo.js` changed to `locale: 'th_TH'`. hrefLang alternate tags added.

**P1-2: TravelAgency schema missing postalAddress — DONE**
`pages/homepagev2.js` — postalAddress field added to TravelAgency JSON-LD.

**P1-3: Security headers missing HSTS, CSP, Permissions-Policy — PARTIAL**
`next.config.js` — HSTS + Permissions-Policy added. CSP skipped — causes runtime break (CSP blocks inline scripts needed by Next.js/GTM).

**P1-4: FAQPage schema not wired — DONE**
FAQPageJsonLd component exists in components/SEO/SEOSection.js but not rendered. Resolved via direct FAQPageJsonLd render in homepagev2.js. WP query extended with faqsPosts (categoryName: "FAQs", first: 5, title + content fields). Transform: post.title → question, post.content → answer.

### P2 — Performance

**P2-1: hero image sizes="100vw" — DONE**
`helpers/imageOptimization.js` — changed to `'(max-width: 768px) 100vw, (max-width: 1200px) 100vw, 1920px'`.

### P3 — Completeness

**P3-1: Missing contactPoint on TravelAgency — OPEN**
Not implemented in `a2a4ff9`.

**P3-2: PopularRoutesStructuredData BusTrip missing departureTime/arrivalTime — OPEN**
Not implemented in `a2a4ff9`.

**P3-3: ReviewsStructuredData uses LocalBusiness — DONE**
`lib/homepage/components/ReviewsStructuredData.js` — type changed to TravelAgency.

**P3-4: LocationsStructuredData missing GeoCoordinates — DONE**
`lib/homepage/components/LocationsStructuredData.js` — geo coordinates fallback added (location.latitude/longitude conditional).

## Fix Queue — Final Status

| Priority | Action | Files | Status |
|----------|--------|-------|--------|
| P0-1 | server-sitemap.xml | informational gap | Optional — no active 404 |
| P1-1 | og:locale th_TH + hrefLang | `_app.js`, `Seo.js` | DONE `a2a4ff9` |
| P1-2 | postalAddress TravelAgency | `homepagev2.js` | DONE `a2a4ff9` |
| P1-3 | Security headers | `next.config.js` | PARTIAL — HSTS + Permissions-Policy only. CSP skipped (breaks runtime) |
| P1-4 | FAQPageJsonLd wired | `api.js`, `homepagev2.js` | DONE `a2a4ff9` |
| P2-1 | hero image sizes | `imageOptimization.js` | DONE `a2a4ff9` |
| P3-1 | contactPoint TravelAgency | `homepagev2.js` | OPEN |
| P3-2 | departureTime/arrivalTime BusTrip | `PopularRoutesStructuredData.js` | OPEN |
| P3-3 | ReviewsStructuredData → TravelAgency | `ReviewsStructuredData.js` | DONE `a2a4ff9` |
| P3-4 | LocationsStructuredData geo | `LocationsStructuredData.js` | DONE `a2a4ff9` |

## Isolation Testing Log

All fixes applied ONE AT A TIME on `ade94ee` clean state:

| Order | Fix | Result |
|-------|-----|--------|
| 1 | ReviewsSection float formatting | OK |
| 2 | HSTS + Permissions-Policy (no CSP) | OK |
| 3 | og:locale th_TH + hrefLang | OK |
| 4 | TravelAgency postalAddress | OK |
| 5 | hero image sizes | OK |
| 6 | ReviewsStructuredData + LocationsStructuredData | OK |
| 7 | FAQPageJsonLd | OK (was the risky one — passed) |

**CSP was the breaker.** Full CSP (HSTS + CSP + Permissions-Policy) broke the project when first tried. CSP blocks inline scripts needed by this Next.js app.

## Key Files Modified (`a2a4ff9`)

- `components/FrontPage/Seo.js` — locale th_TH + hrefLang
- `pages/_app.js` — locale th_TH + hrefLang
- `next.config.js` — HSTS + Permissions-Policy (CSP excluded)
- `pages/homepagev2.js` — postalAddress, FAQPageJsonLd wired, faqsData transform
- `helpers/wordpress/api.js` — faqsPosts query added
- `helpers/imageOptimization.js` — hero sizes breakpoint-aware
- `lib/homepage/components/ReviewsStructuredData.js` — LocalBusiness → TravelAgency
- `lib/homepage/components/LocationsStructuredData.js` — geo coordinates fallback
- `lib/homepage/components/ReviewsSection.js` — displayRating.toFixed(1)

## Related

- [[seo-homepage-specialist-team]]
- [[structured-data-schema-patterns]]
- [[homepage-ux-review]]
- [[blog-seo-performance]]

## Audit Metadata

- Date: 2026-05-31
- Scope: http://localhost:3000/ homepage
- Commit: `a2a4ff9` on `260528-feat/header-redesign-2026` (pushed)
- Scrutinize: 2-agent trace, P0-1 refuted, P1-4 clarified
- Isolation test: 7 fixes tested one-by-one, CSP identified as breaker