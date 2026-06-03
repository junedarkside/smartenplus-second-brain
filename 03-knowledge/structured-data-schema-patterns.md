# Structured Data Schema Patterns

## Summary
Homepage uses 7 schema types. Critical gaps: fake TravelAgency phone/address, missing WebSite+SearchAction, server-sitemap.xml 404. Live data should replace hardcoded literals.

## Context
`homepage-seo-performance-deep-review-2026-05-21.md`. 3-specialist audit (Structured Data + Technical SEO + Performance). 11 SD findings.

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

**Proper fix:** Create `pages/server-sitemap.xml.js` using `getServerSideSitemap` fetching live trip routes. Pattern in `[[blog-seo-performance-2026-05-20]]`.

## Details

### TravelAgency full fix list
1. Import `COMPANY_PHONE_NUMBER`, `FACEBOOK_URL`, `INSTAGRAM_URL`, `X_URL`
2. Replace telephone literal
3. Add `COMPANY_ADDRESS` constant + replace streetAddress/postalCode
4. Wire `aggregateRating` to `lastTopReviewData` (live data)
5. Add `sameAs: [FACEBOOK_URL, INSTAGRAM_URL, X_URL]`
6. Add `logo` ImageObject
7. Add `contactPoint` with `COMPANY_PHONE_NUMBER`, `contactType: "customer support"`, `availableLanguage: ["Thai", "English"]`
8. Replace hardcoded `lastReviewed` with `new Date().toISOString()`

### Other critical OG fixes
- `og:site_name` missing from `Seo.js` — add `siteName: siteName` from constants
- `og:locale` missing — add `locale: 'th_TH'`
- `twitter:site` missing — add `site: '@smartenplus'`

## Tradeoffs
- `server-sitemap.xml.js` proper fix needs backend API enumerating live trip routes — sprint task, not hotfix
- `COMPANY_ADDRESS` needs backend team alignment on legal entity address

## Consequences
- TravelAgency schema accuracy affects Google Business Profile integration
- server-sitemap.xml 404 = Google can't discover dynamic trip routes, suppresses crawl budget
- AggregateRating wired to live data refreshes with ISR (60s)

## Related
- [[blog-seo-performance-2026-05-20]] — server-sitemap.xml pattern
- [[homepage-ux-review-2026-05-21]] — review section render order
- [[nextjs-patterns]] — ISR patterns