# OG Image 1200x630 WebP

## Summary
The default OG image must be WebP 1200×630 at `public/og-image.webp` (not PNG 250×50). Social scrapers (Facebook, LINE, Twitter card) reject small/PNG OG and fall back to scraping the page, often producing broken previews.

## Context
Open Graph image dimensions are an unwritten social-platform contract: 1200×630 is the safe minimum that renders correctly on Facebook (1.91:1), LINE (similar ratio), Twitter `summary_large_image`, and LinkedIn. Smaller images get rejected outright by Facebook's scraper. PNG is not rejected but is 3-5x larger than WebP at the same visual quality, slowing first-paint of share previews.

## Problem
Finding F7 in `website-audit-full-2026-06-06/overview.md`: the existing `public/og-image.png` was 250×50 — too small, wrong format, and referenced from `<DefaultSeo>` as the only site-wide social card. Every share from the site (every blog post, every trip page, every activity) had a broken or low-resolution preview. The same issue was flagged twice across audits before anyone fixed the underlying asset.

## Details
Required artifact:

```
public/og-image.webp   (1200×630, WebP, ~30-80 KB, brand-on-light background)
```

Source-of-truth reference in `pages/_app.js`:

```js
const DEFAULT_SEO = {
  openGraph: {
    images: [
      {
        url: `${getSiteUrl()}/og-image.webp`,
        width: 1200,
        height: 630,
        alt: 'SmartenPlus',
      },
    ],
  },
  twitter: { cardType: 'summary_large_image' },
};
```

Page-level override: pages with their own social card declare a wider/taller image but keep the same format and minimum 1200px width.

## Decision
Site OG asset is committed at `public/og-image.webp` 1200×630. Per-page OG is allowed but must inherit format (WebP) and minimum dimension (1200×630). PNG is not banned but discouraged for new work.

## Tradeoffs
- Pro: every share looks correct across all major platforms.
- Pro: WebP is ~70% smaller than equivalent PNG — faster scrape, faster preview.
- Con: WebP requires a one-time asset build step; designers working in Figma/PSD need an export recipe.
- Con: changing the asset requires cache invalidation in Facebook's debugger (`https://developers.facebook.com/tools/debug/`).

## Consequences
- All social-share previews resolve to one canonical asset, with per-page overrides layered on top.
- The path `public/og-image.webp` is a contract — renaming requires updating `<DefaultSeo>` and OG meta in lockstep.
- Every new page that needs a social card should pull from this spec, not invent new dimensions.

## Related
- [[structured-data-schema-patterns]] — `image` fields in JSON-LD often reuse the same OG asset; both must be 1200×630.
- [[seo-canonical-getsiteurl-pattern]] — `og-image.webp` URL is composed from `getSiteUrl()`.
