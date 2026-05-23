# SEO Wave 2 Audit — 2026-05-23

## Summary
Post-PersistGate-fix audit by 3-agent team (SEO + SSR + Frontend Quality). Found second wave of OG image relative URL bugs, hydration risks, and residual NEXT_PUBLIC_SITE_URL references missed by the original fix. All findings verified against live code.

## Context
Previous session fixed the root SSR blocker (`_app.js` PersistGate) and OG image relative URLs in `seoHelper.js` + `trips/index.js`. This audit ran immediately after — branch `260523-fix/trips-og-image-and-site-url-env` live in production. Audit covers all 49 pages in `pages/` (excluding `/api/`).

## Status
OPEN — fix branch not yet created. Ready to implement next session.

---

## P0 — Critical (fix first, breaks crawlers/Facebook)

### C1 — airport-transfer relative OG image
- **File:** `pages/airport-transfer/index.js:65–66`
- **Bug:** `url: bgDefault.src` + `secureUrl: bgDefault.src` → relative `/_next/static/media/...`
- **Fix:** `const siteUrl = process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th'; url: \`${siteUrl}${bgDefault.src}\``

### C2 — blog/categories/index.js hydration mismatch + stale var
- **File:** `pages/blog/categories/index.js:17`
- **Bug:** `typeof window !== 'undefined' ? window.location.origin : process.env.NEXT_PUBLIC_SITE_URL || 'https://smartenplus.co.th'`
  - SSR gets undefined env var → falls to hardcoded (no `www`)
  - Client gets `window.location.origin` → different value → hydration mismatch
  - Still uses reverted `NEXT_PUBLIC_SITE_URL`
- **Fix:** Replace entire expression with `const SITE_URL = process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th';` (no `typeof window` needed — `getSiteUrl()` from `utils/blog/seoHelper.js` already does this correctly, just import it)

### C3 — blog/categories/[slug].js same hydration + relative images
- **File:** `pages/blog/categories/[slug].js:32, 50, 150`
- **Bug:** Same `typeof window` pattern at :32. Raw `bgDefaultImage1.src` (relative) at :50 (OG image fallback) and :150 (JSON-LD url field)
- **Fix:** Replace :32 with `getSiteUrl()` import. Lines :50 and :150: `\`${SITE_URL}${bgDefaultImage1.src}\`` 

---

## P1 — Major (hurts SEO ranking / social sharing)

### M1 — blog/search/[...slug].js stale var + relative image
- **File:** `pages/blog/search/[...slug].js:129, 164`
- **Bug:** `:129` still `NEXT_PUBLIC_SITE_URL || NEXT_PUBLIC_DOMAIN`. `:164` `searchImageUrl` resolves to bare `bgDefaultImage1.src` (relative path) as final fallback
- **Fix:** `:129` → `getSiteUrl()`. `:164` → `const defaultAbsolute = \`${siteUrl}${bgDefaultImage1.src}\`; const searchImageUrl = blogImage?.src || blogImage || defaultAbsolute;`

### M2 — DefaultSeo in _app.js missing openGraph.url + images[]
- **File:** `pages/_app.js:33–46`
- **Bug:** `DefaultSeo` has no `openGraph.url` and no `openGraph.images[]`. Any page without explicit OG image → Facebook infers from page content
- **Fix:**
  ```js
  openGraph={{
    type: 'website',
    locale: 'en_US',
    url: process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th',
    siteName: 'SmartEnPlus',
    images: [{
      url: `${process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th'}/smartenplus.png`,
      secureUrl: `${process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th'}/smartenplus.png`,
      width: 250,
      height: 50,
      alt: 'SmartEnPlus',
    }],
  }}
  ```
  Note: `/smartenplus.png` already exists in `public/` (referenced in `getPublisherData()` in seoHelper.js)

### M3 — privacy/index.js description copy-paste bug
- **File:** `pages/privacy/index.js:24`
- **Bug:** `description` content says "Terms and Conditions" — this is the Privacy Policy page
- **Fix:** Replace with correct privacy-focused description

### M4 — forum/createtopic.js missing secureUrl
- **File:** `pages/forum/createtopic.js:61–66`
- **Fix:** Add `secureUrl: <same value as url>` to `openGraph.images[0]`

### M5 — forum/index.js missing secureUrl
- **File:** `pages/forum/index.js:90–97`
- **Fix:** Add `secureUrl: <same value as url>` to `openGraph.images[0]`

### M6 — locations/[slug].js missing secureUrl
- **File:** `pages/locations/[slug].js:159–167`
- **Fix:** Add `secureUrl: <same value as url>` to `openGraph.images[0]`

### M7 — help/index.js relative image
- **File:** `pages/help/index.js:45`
- **Bug:** `const selectedGroupImage = bgDefaultImage1.src` → relative path passed downstream
- **Fix:** `const siteUrl = process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th'; const selectedGroupImage = \`${siteUrl}${bgDefaultImage1.src}\``

---

## P2 — Minor (separate branch, non-blocking)

| File | Line | Issue | Fix |
|------|------|-------|-----|
| `pages/privacy/index.js` | 23 | Manual `<title>` bypasses `titleTemplate` | Replace `<Head><title>` with `<NextSeo title="Privacy Policy" ...>` |
| `pages/terms/index.js` | 25 | Same — manual `<title>` | Same fix pattern |
| `pages/about/index.js` | 44 | Same — manual `<title>` | Same fix pattern |
| `pages/forum/[...slug].js` | 82–95 | Hardcoded `https://smartenplus.co.th` (no www, no env var) | Use `getSiteUrl()` |
| `pages/bookings/index.js` | — | Auth page: zero SEO meta, no canonical, no robots directive | Add `<NextSeo noindex title="My Bookings">` |
| `pages/checkout/index.js` | — | Same — only bare `<title>`, no noindex | Add `<NextSeo noindex title="Checkout">` |
| `pages/help/[...slug].js` | 87–93 | OG `images[]` missing `width` + `height` | Add `width: 1200, height: 630` |

---

## Tech Debt (separate branch, non-urgent)

- 21 pages mix `<Head>` manual tags + `<NextSeo>` → potential duplicate meta
- 15+ pages missing `canonical` link tag
- Component size violations (tracked separately — not SEO impact):
  - `pages/homepagev2.js` — 584 lines
  - `pages/trips/index.js` — 716 lines
  - `pages/trips/detail/[...slug].js` — 469 lines
  - `components/forms/checkout/Passengers.js` — 1,146 lines
  - `components/search/SlideCalendar2.js` — 1,035 lines

---

## Confirmed OK — Do Not Re-Audit

- `utils/blog/seoHelper.js` — all 4 cases use absolute `defaultImageUrl`. secureUrl present on post case. PASS.
- `pages/_app.js` PersistGate structure — DefaultSeo/Head/Component above gate. PASS.
- `pages/trips/index.js` ogImagePath — absolute, 2-tier fallback. PASS.
- `pages/homepagev2.js` aboutURL — 2-tier, no NEXT_PUBLIC_SITE_URL. PASS.
- `pages/trips/detail/[...slug].js` noindex — conditional on `lowestRate === null`. Intentional. PASS.
- Raw `<img>` tags in production — zero found. PASS.
- Dev pages noindex (`pages/dev/*.js`) — correct. PASS.

---

## Recommended Branch Strategy

```
260523-fix/seo-wave2-og-and-hydration   ← P0 + P1 (C1-C3, M1-M7)
260523-fix/seo-wave2-minor              ← P2 items
(future) tech-debt/seo-canonical-meta  ← tech debt (canonicals, duplicate Head, component size)
```

---

## Verification After Fix

```bash
# Hydration check — no typeof window in render path
grep -r "typeof window" pages/blog/

# NEXT_PUBLIC_SITE_URL should be zero
grep -r "NEXT_PUBLIC_SITE_URL" pages/ utils/ .github/

# OG image relative paths — zero remaining
grep -rn "bgDefaultImage1\.src\|bgDefault\.src" pages/ | grep -v "getSiteUrl\|SITE_URL\|siteUrl\|defaultImageUrl"

# curl check — head count should be 14+
curl -s https://www.smartenplus.co.th/ | grep 'next-head-count'
curl -s https://www.smartenplus.co.th/airport-transfer | grep 'og:image'
curl -s https://www.smartenplus.co.th/blog/categories/bus | grep 'og:image'
```

---

## Related
- [[og-image-ssr-fix-2026-05-23]] — previous session: PersistGate root cause + seoHelper fix
- [[og-image-inferred-audit-2026-05-23]] — session before: secureUrl site-wide + homepage domain fallback
- [[nextjs-patterns]] — PersistGate SSR blocker + OG absolute URL rules
- [[homepage-seo-performance-deep-review-2026-05-21]] — original 30-finding SEO audit
