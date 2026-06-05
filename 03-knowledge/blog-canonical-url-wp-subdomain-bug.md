# Blog Canonical URL — WordPress Subdomain Bug

## Summary
Blog post canonical tags resolved to `blog.smartenplus.co.th` (WP subdomain) instead of `www.smartenplus.co.th/blog/...`, causing Google to not index main-domain blog URLs.

## Problem
Google Search Console: "Alternate page with proper canonical tag" — user-declared canonical = `https://blog.smartenplus.co.th/...`, Google-selected canonical = same. Main-domain URL treated as duplicate, skipped from index.

## Root Cause
`components/blog/BlogPostHeader.js` line 12 (before fix):

```javascript
const ogUrl = seoPost?.seo?.opengraphUrl?.replace('http://blog.smartenplus.co.th', `${siteUrl}/blog`) ||
  `${siteUrl}/blog/${blogPost.slug}`;
```

WordPress Yoast SEO returns `opengraphUrl` as `https://blog.smartenplus.co.th/...` (HTTPS).

`String.replace('http://...')` looks for `http://` → protocol mismatch → replace silently fails → `String.replace()` with no match returns **original string unchanged** (not falsy) → `||` fallback never fires → `ogUrl` = raw WP subdomain URL → canonical tag = `blog.smartenplus.co.th`.

## Fix Applied (2026-06-05)

**`components/blog/BlogPostHeader.js`** — derive canonical from slug only:
```javascript
const ogUrl = `${siteUrl}/blog/${blogPost.slug}`;
```

**`pages/help/[...slug].js`** — fix replace regex + standardize www:
```javascript
// Before
const jsonSchema = seoPost?.seo?.schema?.raw?.replace(/http:\/\/blog.smartenplus.co.th(?!\/wp-content\/uploads)/g, 'https://smartenplus.co.th/help/faqs');
const ogUrl = seoPost?.seo?.opengraphUrl?.replace('http://blog.smartenplus.co.th', 'https://smartenplus.co.th/help/faqs');
canonical: `https://smartenplus.co.th${router.asPath}`,

// After
const jsonSchema = seoPost?.seo?.schema?.raw?.replace(/https?:\/\/blog\.smartenplus\.co\.th(?!\/wp-content\/uploads)/g, 'https://www.smartenplus.co.th/help/faqs');
const ogUrl = seoPost?.seo?.opengraphUrl?.replace(/https?:\/\/blog\.smartenplus\.co\.th/, 'https://www.smartenplus.co.th/help/faqs');
canonical: `https://www.smartenplus.co.th${router.asPath}`,
```

## Rules Going Forward

1. **Blog canonical:** always derive from `${siteUrl}/blog/${slug}`. Never use `seoPost?.seo?.opengraphUrl` for canonical.
2. **WP subdomain replaces:** always regex `/https?:\/\/blog\.smartenplus\.co\.th/` — string `'http://...'` silently fails on HTTPS input.
3. **www prefix:** all canonicals = `https://www.smartenplus.co.th`. Use `getSiteUrl()` from `utils/blog/seoHelper.js`.

## Commits
- `3d30407` — fix(seo): fix blog canonical URLs pointing to WP subdomain
- `b0fce4f` — docs(claude): add SEO canonical URL gotchas to CLAUDE.md

## Related
- [[master-state]]
