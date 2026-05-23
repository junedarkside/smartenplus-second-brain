# SEO Wave 2 Audit — 2026-05-23

## Summary

Post-PersistGate-fix audit by 3-agent team. Found second wave of OG image relative URL bugs, hydration risks, stale NEXT_PUBLIC_SITE_URL references. All 11 bugs verified + fixed + merged to main (`ceb0eac`).

## Status

DONE — `260523-fix/seo-wave2-og-and-hydration` merged to develop → main → production.

## Key Findings

### Root Cause Clusters

1. **Webpack image `.src` used directly in OG meta** → needs `NEXT_PUBLIC_DOMAIN` prefix
2. **`NEXT_PUBLIC_SITE_URL` still referenced** after removal in commit `4644fac`
3. **Auth pages (bookings/checkout) missing noindex** → crawl budget leak

### M5/M6 — ALREADY FIXED

`forum/index.js` :93 and `locations/[slug].js` :165 — `secureUrl: ogImagePath` already present. No change needed.

### P2 → P1 Promotions

| Item | File | Issue |
|------|------|-------|
| P2-1 | `privacy/index.js` | description says "Terms and Conditions" + manual title bypass |
| P2-5 | `bookings/index.js` | auth page: zero SEO meta, no noindex |
| P2-6 | `checkout/index.js` | same — auth page, no public SEO value |

## Fixes Applied (11 bugs, 9 files)

| ID | File | Fix |
|----|------|-----|
| C1 | `airport-transfer/index.js` | siteUrl template for ogImagePath |
| C2 | `blog/categories/index.js` | getSiteUrl() import + replacement |
| C3 | `blog/categories/[slug].js` | getSiteUrl() + siteUrl template at :32, :50, :150 |
| M1 | `blog/search/[...slug].js` | getSiteUrl() + siteUrl template at :129, :164 |
| M2 | `_app.js` | Added `url` + `images[]` array to DefaultSeo openGraph |
| M3 | `privacy/index.js` | correct privacy description |
| M4 | `forum/createtopic.js` | Added `secureUrl: ogImagePath` |
| M7 | `help/index.js` | Inline siteUrl template for selectedGroupImage |
| P2-1 | `privacy/index.js` | Head → NextSeo with correct privacy description |
| P2-5 | `bookings/index.js` | NextSeo noindex |
| P2-6 | `checkout/index.js` | NextSeo noindex |

## Auth Pages Noindex — BLOCKED

`ProtectedComponent` returns `null` on SSR for unauthenticated users → NextSeo never renders → noindex not taking effect. Fix deferred: `_app.js` DefaultSeo conditional per route, or middleware `X-Robots-Tag` header.

## Related

See atomic notes:
- [[persistgate-ssr-suppresses-head-component]]
- [[webpack-image-src-og-absolute-url-rule]]