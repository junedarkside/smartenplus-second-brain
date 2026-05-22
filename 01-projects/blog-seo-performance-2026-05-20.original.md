---
name: blog-seo-performance-2026-05-20
description: Blog index + detail page SEO, performance, and HMR fixes — what was done, what was skipped, and why
metadata:
  type: project
---

# Blog SEO & Performance Optimization

## Summary
Two-session effort to audit and optimize blog index (`pages/blog/index.js`) and blog detail (`pages/blog/[slug].js`) pages for Core Web Vitals, SEO signals, and HMR stability.

## What Was Done

### Session 1 — `0f38cf8` (2026-05-19)
- `getSiteUrl()` — env-only canonical base URL (no hardcoded domain)
- `Article` → `BlogPosting` JSON-LD schema type
- Added `inLanguage`, `wordCount`, `articleSection` to schema
- `og:locale: en_US`, `robots` meta, deduplicated org schema
- `useMemo([posts])` on seoConfig to prevent recalc on every render
- `priority={true}` on featured BlogCard image (LCP fix)
- `aspect-video` class on featured card container (CLS fix)
- `revalidate: 60 → 300` on blog index ISR
- `/_next/static/` Cache-Control immutable header

### Session 2 — `6b655d6` (2026-05-20)

**Performance**
- `relatedPosts` + `relatedRoutes` now fetched in parallel via `Promise.allSettled` — saves one full sequential network round-trip per page generation (`[slug].js:212`)
- `getBlogTargetURL` moved to module-level stable const — prevents BlogCard child re-renders on every index render (`index.js`)
- `StandardBreadcrumb` changed from `ssr:false` → `ssr:true` — breadcrumb now in SSR HTML for SEO crawlers

**Images**
- Author avatar in BlogPostDisplay: MUI `<Avatar src>` → `next/image` with `fill` + `sizes="34px"` (`BlogPostDisplay.js:152`)
- `secure.gravatar.com` added to `next.config.js` remotePatterns (was throwing unconfigured-host error)
- BlogCard both variants: added `sizes` attribute — featured `40vw`, grid `33vw` — browser downloads correctly-sized image per viewport

**GraphQL**
- `mediaDetails { width height }` added to `POST_BY_SLUG` query — OG image dimensions now real values, not hardcoded 1200×630 defaults (`api.js:233`)

**SEO**
- `twitter:creator` added to BlogPostHeader twitter config

**HMR / Fast Refresh fixes**
- `BlogPostContent.js`: module-level `let DOMPurify = null; if (typeof window)` conditional require → `getDOMPurify()` function — module-level conditional require breaks webpack HMR module graph tracking
- `useBlogAnalytics.js`: `useCallback([blogPost])` + `useEffect([blogPost, trackBlogView])` → `[blogPost?.databaseId]` — object ref as dep = new ref every render = infinite loop + repeated `POST /api/track-blog-view`
- `BlogPostDisplay.js`: same `useEffect([blogPost])` fix; imports reordered (static imports must precede all `const` declarations — violating this breaks Fast Refresh)

## What Was Skipped and Why

| Skipped | Reason |
|---------|--------|
| ISR `300 → 120` | Blog content changes daily not every 2 min. 300s fine |
| `commentCount` in JSON-LD schema | Optional, low ranking signal, adds noise |
| `speakable` schema field | Overkill for this site |
| RegExp caching in `highlightSearchTerms` | Micro-optimization, not measurable |
| `smartenpus-transportation-booking-online.webp` rename | Filename typo IS the real filename in `/public/` — renaming breaks import |
| CategoryMenu `ssr:false` | CategoryMenu reads client-only state (selected category) — ssr:false intentional |

## Key Patterns to Reuse

- **Stable function refs**: define `const getFn = (a, b) => ...` at module level outside component — never inline in JSX prop
- **Parallel secondary fetches**: after primary data resolves, wrap secondary fetches in `Promise.allSettled([...])` not sequential `await`
- **HMR-safe module init**: never `if (typeof window) { require(...) }` at module level — wrap in function called at render time
- **useEffect deps**: never pass whole object — use stable primitive (`id`, `slug`) as dep

## Related
- [[nextjs-patterns]]
- [[master-state]]
