# Structured Data Schema Patterns

## Summary
Homepage uses 7 schema types. Critical gaps: fake TravelAgency phone/address, missing WebSite+SearchAction, server-sitemap.xml 404. Live data should replace hardcoded literals.

## Context
`homepage-seo-performance-deep-review.md`. 3-specialist audit (Structured Data + Technical SEO + Performance). 11 SD findings.

## Problem

### SD1 — TravelAgency telephone is fake
`pages/homepagev2.js:295` hardcodes `"+66-2-123-4567"`. Real constant: `COMPANY_PHONE_NUMBER = '+66-61-465-5695'` in `helpers/constants.js:63`. Google rejects mismatched contact details.

### SD2 — TravelAgency streetAddress is placeholder
`"streetAddress": "123 Sukhumvit Road"` — no `COMPANY_ADDRESS` constant exists. False address risks manual action.

### SD7 — WebSite + SearchAction missing
No `WebSite` schema. Required for Sitelinks Search Box. Trip search URL maps to `SearchAction`.

### TS6 — server-sitemap.xml 404
`next-sitemap.config.js:12` + `public/robots.txt:17` reference `server-sitemap.xml` — file missing. 404 suppresses dynamic trip route indexing.

## Decision

### Fix TravelAgency schema
```jsx
// BEFORE (homepagev2.js:295)
"telephone": "+66-2-123-4567"

// AFTER
import { COMPANY_PHONE_NUMBER } from 'helpers/constants';
"telephone": COMPANY_PHONE_NUMBER
```

### Add COMPANY_ADDRESS constant
```js
// helpers/constants.js
export const COMPANY_ADDRESS = {
  streetAddress: '...',
  postalCode: '...',
  addressLocality: '...',
  addressCountry: 'TH'
};
```

### WebSite + SearchAction schema
```jsx
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "SmartEnPlus",
  "url": "https://www.smartenplus.co.th",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://www.smartenplus.co.th/trips/{from}/{to}?date={date}",
    "query-input": "required name=from"
  }
}
```

### server-sitemap.xml hotfix + proper fix
**Hotfix (5 min):** Remove from `next-sitemap.config.js` + `robots.txt`.

**Proper fix:** Create `pages/server-sitemap.xml.js` using `getServerSideSitemap` fetching live trip routes. Pattern in `[[blog-seo-performance]]`.

## Details

### TravelAgency full fix list
1. Import `COMPANY_PHONE_NUMBER`, `FACEBOOK_URL`, `INSTAGRAM_URL`, `X_URL`
2. Replace telephone literal
3. Add `COMPANY_ADDRESS` constant + replace streetAddress/postalCode
4. Wire `aggregateRating` to `lastTopReviewData` (live data)
5. Add `sameAs: [FACEBOOK_URL, INSTAGRAM_URL, X_URL]`
6. Add `logo` ImageObject
7. Add `contactPoint` with `COMPANY_PHONE_NUMBER`, `contactType: "customer support"`, `availableLanguage: ["English"]` (en-only policy — site serves no Thai; was `["Thai","English"]` which contradicted the en-only decision, corrected 2026-06-25 alongside `homepagev2.js:244` fix)
8. Replace hardcoded `lastReviewed` with `new Date().toISOString()`

### Other critical OG fixes
- `og:site_name` missing from `Seo.js` — add `siteName: siteName` from constants
- `og:locale` missing — add `locale: 'en_US'` (en-only policy; was `th_TH`, corrected 2026-06-26)
- `twitter:site` missing — add `site: '@smartenplus'`

## Tradeoffs
- `server-sitemap.xml.js` proper fix needs backend API enumerating live trip routes — sprint task, not hotfix
- `COMPANY_ADDRESS` needs backend team alignment on legal entity address

## Consequences
- TravelAgency schema accuracy affects Google Business Profile integration
- server-sitemap.xml 404 = Google can't discover dynamic trip routes, suppresses crawl budget
- AggregateRating wired to live data refreshes with ISR (60s)

## RULE — `aggregateRating` placement (Google self-serving policy)
**Never attach `aggregateRating` to a `TravelAgency`/`Organization`/`LocalBusiness` node representing your own (or a partner operator's) business.** Google prohibits self-serving review markup on the org entity — it's ineligible at best, manual-action risk at worst. Attach `aggregateRating` ONLY to the **bookable item** (`Product`/`TouristTrip`/`Offer`), where it's eligible. (Established via operator-detail SEO/AEO/GEO audit 2026-06-16; the trip-detail page does this correctly — rating on the `Product`/`TouristTrip`, not the operator `TravelAgency`.)

**⚠ Contradiction flag:** this note's older "Details → TravelAgency full fix list" item 4 ("Wire `aggregateRating` to `lastTopReviewData`" on the homepage TravelAgency node) is the exact anti-pattern above. Re-evaluate before implementing item 4 — either drop the org-level aggregateRating, or move it to a Product/Offer node. First-party-vs-self-reported provenance doesn't rescue org-node placement; the *node type* is the problem.

On `/operators/[slug]` (shipped #124) the rating is deliberately rendered in **FAQ prose only**, with the operator emitted as a bare `TravelAgency` (name/url/logo, no rating). Reusable utils: `helpers/seo/operatorDetailSEOUtils.js`, renderer `components/operators/OperatorDetailSEO.js`.

## Related
- [[blog-seo-performance]] — server-sitemap.xml pattern
- [[homepage-ux-review]] — review section render order
- [[nextjs-patterns]] — ISR patterns
- [[operator-detail-seo-aeo-geo-audit]] — source of the aggregateRating-placement rule + operator schema pattern