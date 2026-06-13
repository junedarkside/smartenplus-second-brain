# SEO Canonical Getsiteurl Pattern

## Summary
All canonical URLs in Next.js must use `getSiteUrl()` from `utils/blog/seoHelper.js` and return `https://www.smartenplus.co.th` — never `https://smartenplus.co.th` (no www).

## Context
Hardcoded wrong-canonical recurs in every per-page audit. The bug reappears because Next.js has multiple places to declare canonicals (`_app.js`, dynamic `[...].js` routes, `getStaticProps` return shapes, per-page `<NextSeo>`), and each one can drift independently.

## Problem
- Per-page audits repeatedly surface `https://smartenplus.co.th/...` canonicals that should be `https://www.smartenplus.co.th/...`.
- The inconsistency fragments PageRank and causes Google to index both versions.
- One-line mistake, but recurs because each new page author re-derives the URL inline.

## Details
The single source of truth lives in `utils/blog/seoHelper.js`:

```js
export const getSiteUrl = () => 'https://www.smartenplus.co.th';
```

All canonicals, OG URLs, and JSON-LD `@id`/`url` fields must compose from this helper:

```js
import { getSiteUrl } from 'utils/blog/seoHelper';
const canonical = `${getSiteUrl()}/trip/${slug}`;
```

Required call sites:
- `pages/_app.js` — global `<DefaultSeo canonical={getSiteUrl()} />`
- `pages/[...].js` dynamic routes — every `getStaticProps` builds canonical from helper
- Per-page `<NextSeo>` blocks — `canonical` prop sourced from helper
- JSON-LD `url`/`@id` — both must match the canonical

## Decision
Centralize the site URL behind one helper. Reject any PR that hardcodes `smartenplus.co.th` (with or without www) in a new canonical declaration.

## Tradeoffs
- Pro: one fix point, no drift between code paths.
- Pro: easy to test (mock `getSiteUrl`).
- Con: a typo in the helper propagates everywhere; needs an integration test asserting all canonicals start with `https://www.`.

## Consequences
- Every audit must `grep` for `smartenplus.co.th` in canonicals, OG, and JSON-LD.
- Future domain migrations = change one line, redeploy.
- New schema/SEO code is required to import the helper — add a lint rule or code-review checklist item.

## Related
- [[structured-data-schema-patterns]] — JSON-LD `url`/`@id` must match the canonical from this helper.
- [[seo-homepage-specialist-team]] — homepage canonicals are the highest-traffic site; same helper, same rule.
- [[blog-canonical-url-wp-subdomain-bug]] — WP subdomain canonicalization uses the same helper, different ruleset.
