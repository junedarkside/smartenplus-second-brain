# OG Image "Inferred" Warning — Site-Wide Audit 2026-05-23

## Summary
Facebook Sharing Debugger shows `og:image` as "inferred" across homepage and all blog pages. Two separate root causes, neither introduced by recent commits — both pre-existing in production.

## Problem
Facebook debugger warning: "Should specify og:image explicitly even though value may be inferred from other tags."

- **Homepage**: `og:title = www.smartenplus.co.th` (domain only, no real title). `og:description` empty.
- **Blog pages**: `og:image` tag present but no `og:image:secure_url` → Facebook treats it as inferred.

## Root Cause 1 — Homepage SEO component crash

**File:** `pages/homepagev2.js:192`
```js
const aboutURL = process.env.NEXT_PUBLIC_DOMAIN;  // undefined in production
// → domainURL = "undefined/"
```

**File:** `components/FrontPage/Seo.js:8`
```js
const pageOrigin = new URL(domainURL).origin;  // TypeError: "undefined/" is not a valid URL
```

`new URL("undefined/")` throws → `Seo` component crashes → no OG tags rendered → Facebook infers everything from the domain.

**Why it's undefined:** `NEXT_PUBLIC_DOMAIN` is only in `.env.local` (= `http://localhost:3000`). It is **absent from `.env.production.sample`** and therefore not set on the production server. Has been broken since June 2025 (commit `c69662c`).

**Fix:** Replace `process.env.NEXT_PUBLIC_DOMAIN` with `getSiteUrl()` from `utils/blog/seoHelper.js` which falls back to `'https://www.smartenplus.co.th'`.

## Root Cause 2 — Missing `og:image:secure_url` on blog pages

`next-seo` only emits `<meta property="og:image:secure_url">` when `secureUrl` is passed in the images array. Facebook requires this to confirm the image is served over HTTPS. When absent, it marks `og:image` as "inferred."

**Already fixed:** `components/blog/BlogPostHeader.js` (post detail) — fixed in commit `1dd9d01` 2026-05-23.

**Still broken:**

| File | Issue |
|------|-------|
| `pages/blog/index.js` | `og:image` present, `secureUrl` missing |
| `pages/blog/categories/index.js` | Same |
| `pages/blog/categories/[slug].js` | Same |
| `pages/blog/tags/[slug].js` | No `openGraph` at all (blogImage defined but unused) |
| `pages/blog/search/[...slug].js` | No `openGraph` at all (blogImage defined but unused) |
| `pages/blog/tags/index.js` | No `openGraph` at all |

## Decision

Fix both root causes in branch `260523-fix/og-image-homepage-and-blog`:

1. `pages/homepagev2.js` — `getSiteUrl()` instead of `process.env.NEXT_PUBLIC_DOMAIN`
2. `components/FrontPage/Seo.js` — add `secureUrl: ogImagePath` to images array
3. Blog pages — add `secureUrl` or add missing `openGraph` blocks

## Fix Pattern

```js
// Import (already available in blog files)
import { getSiteUrl } from '../../utils/blog/seoHelper';

// Absolute URL construction
const siteUrl = getSiteUrl(); // → 'https://www.smartenplus.co.th'
const imageUrl = img.src.startsWith('http') ? img.src : `${siteUrl}${img.src}`;

// Images array — secureUrl is the only required addition for existing og:image
images: [{
  url: imageUrl,
  secureUrl: imageUrl,  // ← adds og:image:secure_url meta tag
  width: 1200,
  height: 630,
  alt: title,
}]
```

## Tradeoffs

- `getSiteUrl()` hardcodes `'https://www.smartenplus.co.th'` — fine for production, wrong in staging/dev. Same tradeoff as existing blog SEO code. Acceptable given current deployment model.
- No env var change needed — `NEXT_PUBLIC_DOMAIN` stays as-is for other uses.

## Related

- [[blog-seo-performance-2026-05-20]] — prior blog SEO work
- [[homepage-seo-performance-deep-review-2026-05-21]] — original audit that caught og:locale and DefaultSeo gaps
