---
name: hreflang-th-tag-self-referencing-bug
description: Homepage declared hreflang="th" pointing at its own English-only URL — a live, self-contradicting language signal to Google, unrelated to any Thai-market migration timing. Fixed 2026-09-23.
type: knowledge-atom
date: 2026-09-23
parent: multi-market-i18n-analytics-migration
---

# Homepage hreflang="th" Self-Referencing Bug

## Summary
`components/FrontPage/Seo.js` declared a `hrefLang="th"` alternate link pointing at the homepage's own English-only URL, while the same file sets `openGraph.locale: 'en_US'` and an English title. Found during the multi-market migration audit (`[[multi-market-i18n-analytics-migration]]`) — live today, independent of whether/when a real Thai page ever ships.

## Problem
`components/FrontPage/Seo.js:32-41` (before fix):
```js
additionalLinkTags: [
  { rel: 'icon', href: '/favicon.ico' },
  { rel: 'alternate', hrefLang: 'th', href: domainURL },        // wrong
  { rel: 'alternate', hrefLang: 'x-default', href: domainURL },
],
```
`domainURL` is the page's own canonical English URL (`homeTitle = 'Book Bus, Ferry & Train Tickets in Thailand'`, `openGraph.locale: 'en_US'` at `:59`). Declaring `hrefLang="th"` here tells Google this URL is the Thai-language version of itself — a self-contradicting signal on the site's highest-authority page. Not a stub or placeholder; it was actively serving this incorrect tag in production.

This is **not** the same category as `helpers/seo/operatorDetailSEOUtils.js:51-53`, which has a deliberate code comment explaining why hreflang is intentionally omitted there (single-locale site, no equivalent page to point at) — that file is correct as-is. The homepage's bug was an incorrect *value*, not an intentional omission.

## Decision
Fixed 2026-09-23, branch `fix/seo-hreflang-th-alternate`, commit `b27b20a0`. Changed `hrefLang: 'th'` → `hrefLang: 'en'` — a self-referencing `en` alternate, matching the pattern already used correctly in three other places in this codebase:
- `hooks/useLocationDetailStructuredData.js:45-46`
- `hooks/useTripsStructuredData.js:29-30`
- `helpers/seo/tripDetailSEOUtils.js:43-44`

Did not delete the alternate-links block or the `x-default` entry — REUSE FIRST: matching an existing correct pattern beats inventing a new one or removing hreflang from the page entirely.

## Consequences
Zero-dependency fix (verified: no test coverage on `Seo.js`, two callers `pages/homepagev1.js` and `pages/homepagev2.js` both confirmed to still import/render correctly, file is 73 lines/green band). Whoever eventually ships a real `/th` homepage should ADD a genuine `hrefLang="th"` pointing at the real Thai URL — this fix only removes the incorrect self-reference, it does not itself establish multi-locale hreflang.

## Related
- [[multi-market-i18n-analytics-migration]] — parent audit this was found under
- [[canonicalization-audit-checklist]] — broader canonical/hreflang checklist this bug should be cross-referenced against on future audits
