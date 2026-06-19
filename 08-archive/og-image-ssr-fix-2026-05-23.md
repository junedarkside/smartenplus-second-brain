# OG Image SSR Fix 2026-05-23

## Summary
All OG meta tags missing from server-rendered HTML site-wide. Root cause: `PersistGate loading={null}` in `_app.js` suppressed entire app during SSR. Secondary: relative paths used as OG image URLs.

## Status
FIXED — branch `260523-fix/trips-og-image-and-site-url-env` — pending merge → develop → main

## Context
Previous session fixed `og:image "inferred"` warning (commit `074b51e`). This session found production still showing empty title/description/og:image on ALL pages. opengraph.dev scraper confirmed blank meta. Assumed deployment issue at first — then reproduced locally via `curl + grep`.

## Root Causes

### RC1 — PersistGate suppresses all SSR (CRITICAL)
`pages/_app.js` had `PersistGate loading={null}` wrapping `DefaultSeo`, `Head`, `Layout`, and `<Component>`. `PersistGate` renders `null` server-side until redux-persist rehydrates (client only). Result: zero meta tags in HTML.

**Diagnosis command:**
```bash
curl -s http://localhost:3000/ | grep 'next-head-count'
# Bad:  content="2"   (only charset + viewport)
# Good: content="14"  (full meta suite)
```

**Fix — `pages/_app.js` commit `ac6f8aa`:**
- Hoisted `DefaultSeo`, `Head`, `Layout`, `<Component>` above `PersistGate`
- `PersistGate` now only wraps `RefreshTokenHandler` + `DevToolsProvider` (client-only)
- Verified: homepage title, og:title, og:description, og:image all present in SSR HTML

### RC2 — Relative OG image paths in seoHelper.js
`bgDefaultImage1.src` (Next.js static import) = `/_next/static/media/...` (relative). Used as fallback `og:image` URL in `generateBlogSEO()` for all cases (category, tag, index, post). Facebook can't fetch relative URLs → og:image load error.

**Fix — `utils/blog/seoHelper.js` commit `f8d9907`:**
```js
const defaultImageUrl = `${SITE_URL}${bgDefaultImage1.src}`;
// All fallback image refs replaced with defaultImageUrl
```

### RC3 — trips/index.js relative ogImagePath + no domain fallback
`pages/trips/index.js:355` used `smartenplusImage.src` (relative) directly as `ogImagePath`. Line 316 had no fallback for `NEXT_PUBLIC_DOMAIN`.

**Fix — commit `61134c9` + `4644fac`:**
```js
const aboutURL = process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th';
const ogImagePath = `${aboutURL}${smartenplusImage.src}`;
```

### RC4 — Redundant NEXT_PUBLIC_SITE_URL (tech debt caught)
Previous commit added `NEXT_PUBLIC_SITE_URL` to deploy.yml. `NEXT_PUBLIC_DOMAIN` already in GitHub Secrets with correct value. Two vars = same data = tech debt. Reverted in `4644fac`. `getSiteUrl()` simplified to 2-tier: `NEXT_PUBLIC_DOMAIN || hardcoded`.

## Branch Commits (in order)
| Commit | Fix |
|--------|-----|
| `61134c9` | trips/index.js absolute ogImagePath + domain fallback |
| `f8d9907` | seoHelper.js absolute fallback image URLs |
| `4644fac` | Remove redundant NEXT_PUBLIC_SITE_URL |
| `ac6f8aa` | **_app.js PersistGate SSR fix — the root cause** |

## Tech Debt Found (team audit — separate branch needed)
From 3-agent SEO/HTML semantic audit:
- 21 pages mix `<Head>` manual tags + `DefaultSeo` → duplicate meta
- 18 pages hardcode `<title>` bypassing `titleTemplate`
- 15+ pages missing canonical
- `pages/trips/detail/[...slug].js` has `noindex` — verify if intentional
- `pages/privacy/index.js` description says "Terms and Conditions" (copy-paste bug)
- `DefaultSeo` in `_app.js` missing `images` array and `url` field

## Verification
```bash
# Local: confirm SSR meta present
curl -s http://localhost:3000/ | grep -oP '<title>[^<]*</title>'
curl -s http://localhost:3000/ | grep 'property="og:title"'

# Blog post
curl -s "http://localhost:3000/blog/SLUG" | grep 'og:title\|og:image'

# Production: Facebook Sharing Debugger
# https://developers.facebook.com/tools/debug/
```

## Related
- [[og-image-inferred-audit-2026-05-23]] — previous session fix (secureUrl site-wide)
- [[nextjs-patterns]] — PersistGate SSR blocker pattern + OG absolute URL rule
- [[homepage-seo-performance-deep-review-2026-05-21]] — original SEO audit
