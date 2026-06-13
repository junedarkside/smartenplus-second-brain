# DefaultSeo Fallback Pattern

## Summary
Every Next.js `_app.js` needs `<DefaultSeo>` from `next-seo` with `defaultTitle`, `titleTemplate`, `description`, `openGraph` (including `siteName`, `locale: 'th_TH'`), and `twitter` (with `site: '@smartenplus'`). Pages without a per-page `<NextSeo>` get zero metadata if this is missing.

## Context
`next-seo`'s `<DefaultSeo>` is the safety net. Without it, a route that forgets `<NextSeo>` ships to Google with no title, no description, no OG tags. Audits of `/orders/`, `/booking/`, and dynamic catch-all routes repeatedly flag missing metadata — the root cause is always the same: no `<DefaultSeo>` at the app root.

## Problem
- Forgetting `<NextSeo>` on a single page produces silently unindexed, unshareable pages.
- No DRY mechanism: each page author has to repeat the same OG/twitter boilerplate.
- Search engines and social scrapers fall back to heuristics that hurt CTR.

## Details
Add to `pages/_app.js`:

```js
import { DefaultSeo } from 'next-seo';
import { getSiteUrl } from 'utils/blog/seoHelper';

const DEFAULT_SEO = {
  defaultTitle: 'SmartenPlus — Book Transport & Tours in Thailand',
  titleTemplate: '%s | SmartenPlus',
  description: 'Book airport transfers, day tours, and transport across Thailand. Real-time availability, instant confirmation.',
  openGraph: {
    type: 'website',
    locale: 'th_TH',
    url: getSiteUrl(),
    siteName: 'SmartenPlus',
    images: [{ url: `${getSiteUrl()}/og-image.webp`, width: 1200, height: 630 }],
  },
  twitter: {
    cardType: 'summary_large_image',
    site: '@smartenplus',
  },
};

export default function App({ Component, pageProps }) {
  return (
    <>
      <DefaultSeo {...DEFAULT_SEO} />
      <Component {...pageProps} />
    </>
  );
}
```

Pages can override per-route with `<NextSeo title="..." description="..." />`. The `titleTemplate` automatically suffixes.

## Decision
Mandate `<DefaultSeo>` in every Next.js app at `_app.js`. Reject any merge to a new project skeleton without it. Treat a missing `<DefaultSeo>` as a blocker in code review.

## Tradeoffs
- Pro: one config block covers all unconfigured pages.
- Pro: consistent brand voice (titleTemplate, OG siteName) across thousands of pages.
- Con: pages that need to fully override (e.g., error pages) must explicitly set `titleTemplate={null}`.
- Con: changing the default description requires a careful reindexing window.

## Consequences
- New page authors get a working baseline for free.
- Per-page SEO is incremental: start from default, override only what differs.
- Audits should fail loudly if `_app.js` lacks `<DefaultSeo>`.

## Related
- [[structured-data-schema-patterns]] — schema lives below metadata; the same fallback principle applies to JSON-LD.
- [[seo-homepage-specialist-team]] — homepage builds on `defaultTitle` with richer per-section schema.
- [[seo-canonical-getsiteurl-pattern]] — `getSiteUrl()` is the URL source for `openGraph.url`.
