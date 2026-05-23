# Webpack Image .src OG Absolute URL Rule

## Summary

Webpack `import img from './file.webp'` produces relative paths like `/_next/static/media/file.hash.webp`. Using `.src` directly in `og:image` = relative URL = Facebook/crawlers can't fetch.

## Problem

```jsx
// BAD — relative path in OG image
const ogImagePath = bgDefaultImage1.src;  // "/_next/static/media/..."
// Facebook sees: og:image = "/_next/static/media/file.hash.webp" ❌
```

## Fix

Always prepend site URL:

```jsx
// GOOD
const siteUrl = process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th';
const ogImagePath = `${siteUrl}${bgDefaultImage1.src}`;
// Facebook sees: og:image = "https://www.smartenplus.co.th/_next/static/media/file.hash.webp" ✅
```

## Rule

Static imports for OG images → always prefix with `NEXT_PUBLIC_DOMAIN`.

## Affected Files (audit findings)

- `pages/airport-transfer/index.js:65-66` — bgDefault.src relative
- `pages/blog/categories/index.js` — typeof window hydration mismatch
- `pages/blog/categories/[slug].js` — bgDefaultImage1.src relative at :50, :150
- `pages/blog/search/[...slug].js` — :164 relative fallback
- `pages/help/index.js:45` — selectedGroupImage bare relative

WP/CDN image URLs (`https://smartenplus-wp-s3...`) already absolute — no change needed.

## Related
- [[persistgate-ssr-suppresses-head-component]]
- [[nextjs-patterns]]
- [[og-image-ssr-fix-2026-05-23]]