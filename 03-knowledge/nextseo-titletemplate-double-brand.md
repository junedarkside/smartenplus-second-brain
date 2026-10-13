# NextSeo titleTemplate double brand

## Summary
`_app.js` sets `titleTemplate="%s | SmartEnPlus"`. Any page title that already ends in `| SmartEnPlus` renders the brand twice.

## Context
Thai no-price route title in `components/SEO/seoConfig.js` `formatTitle` ended `| SmartEnPlus` -> `... | SmartEnPlus | SmartEnPlus`. English titles never had the suffix. Same trap recorded for `/activities` (comment in `pages/activities/index.js`).

## Rule
Page titles must NOT include the brand. `openGraph.title` is not templated, so it shows no brand; accepted (English already behaves this way). The og:image `alt` text may keep the brand, it is not a `<title>`.

## Detect
`grep -rn "| SmartEnPlus" components pages hooks` outside `_app.js`, then curl a `/th/` page and count `SmartEnPlus` in `<title>`.

## Related
[[noindex-flag-decoupled-from-title-flag]] · [[seo-aeo-geo-live-audit-2026-06-22/r8-live-prod-2026-06-26]]
