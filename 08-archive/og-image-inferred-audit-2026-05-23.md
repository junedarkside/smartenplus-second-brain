# OG Image "Inferred" Warning — Site-Wide Audit 2026-05-23

**STATUS: COMPLETED 2026-05-23 — merged main `190e2a2` — live in production**

## Summary
Facebook Sharing Debugger shows `og:image` as "inferred" across homepage and all blog pages. Two separate root causes, neither introduced by recent commits — both pre-existing in production. Fixed site-wide (24 files).

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

**Fix:** Inline 3-tier fallback — do NOT import `getSiteUrl()` (wrong module boundary — that lives in blog utilities):
```js
const aboutURL = process.env.NEXT_PUBLIC_SITE_URL || process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th';
```

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

## Scrutiny Corrections (2026-05-23)

Original fix plan had two errors caught by scrutiny:

1. **Homepage fix**: Do NOT use `getSiteUrl()` — it lives in `utils/blog/seoHelper.js` (blog-specific). Importing into `homepagev2.js` crosses module boundaries. Use inline 3-tier fallback instead.
2. **Blog pages**: `utils/blog/seoHelper.js` exports `generateBlogSEO()` which already handles `tag`, `index`, `category` types. The `tag` case currently lacks `openGraph`. Fix the helper once, then call it from pages — don't copy `secureUrl` inline to 6 separate files.
3. **Scope**: `search/[...slug].js` already has a `seo` object + LD+JSON — it's not a blank slate. Its inline fallback chain misses `NEXT_PUBLIC_DOMAIN` as middle tier (inconsistent with `getSiteUrl()`).

## Decision

Fix both root causes in branch `260523-fix/og-image-homepage-and-blog`:

1. `pages/homepagev2.js:192` — inline 3-tier fallback (no import change):
   ```js
   const aboutURL = process.env.NEXT_PUBLIC_SITE_URL || process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th';
   ```
2. `components/FrontPage/Seo.js` — add `secureUrl: ogImagePath` to images array
3. `utils/blog/seoHelper.js` — add `openGraph` block with `secureUrl` to `tag` and `index` cases in `generateBlogSEO()`
4. `pages/blog/tags/[slug].js` + `pages/blog/tags/index.js` — use `generateBlogSEO()` or add `openGraph` inline
5. `pages/blog/search/[...slug].js` — fix inline fallback to 3-tier, add `openGraph`
6. Audit remaining blog pages: `grep -rL "secureUrl" pages/blog/`

## Fix Pattern

```js
// Homepage — inline only, no import
const aboutURL = process.env.NEXT_PUBLIC_SITE_URL || process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th';

// Seo.js and blog pages — secureUrl addition
images: [{
  url: imageUrl,
  secureUrl: imageUrl,  // ← adds og:image:secure_url meta tag
  width: 1200,
  height: 630,
  alt: title,
}]
```

## Tradeoffs

- Inline fallback for homepage avoids cross-module import — matches existing `getSiteUrl()` logic without coupling.
- Using `generateBlogSEO()` as central helper means one fix propagates to all blog page types vs. patching N files individually.

## Related

- [[blog-seo-performance-2026-05-20]] — prior blog SEO work
- [[homepage-seo-performance-deep-review-2026-05-21]] — original audit that caught og:locale and DefaultSeo gaps
