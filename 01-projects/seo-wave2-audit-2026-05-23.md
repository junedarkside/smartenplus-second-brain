# SEO Wave 2 Audit — 2026-05-23

## Summary
Post-PersistGate-fix audit by 3-agent team (SEO + SSR + Frontend Quality). Found second wave of OG image relative URL bugs, hydration risks, and residual NEXT_PUBLIC_SITE_URL references missed by the original fix. All findings verified against live code.

## Context
Previous session fixed the root SSR blocker (`_app.js` PersistGate) and OG image relative URLs in `seoHelper.js` + `trips/index.js`. This audit ran immediately after — branch `260523-fix/trips-og-image-and-site-url-env` live in production. Audit covers all 49 pages in `pages/` (excluding `/api/`).

## Status
OPEN — confirmed bugs logged. Implementation pending. Branch: `260523-fix/seo-wave2-og-and-hydration`

---

## Audit Team Results (2026-05-23)

3-agent team traced all P0/P1/P2 findings against live `main` HEAD. Key updates:

### M5, M6 — ALREADY FIXED
- `forum/index.js:93` — `secureUrl: ogImagePath` already present. No change needed.
- `locations/[slug].js:165` — `secureUrl: ogImagePath` already present. No change needed.
- Audit was against older version. Current code clean.

### P2 → P1 Promotions (3 items)
| Item | File | Issue | Why promoted |
|------|------|-------|-------------|
| P2-1 | `privacy/index.js` | description says "Terms and Conditions" | Active SEO mislead — crawlers get wrong page description |
| P2-5 | `bookings/index.js` | zero SEO meta, no noindex | Auth-gated — crawl budget leak, should be noindex |
| P2-6 | `checkout/index.js` | only bare `<title>`, no noindex | Same — auth-gated, zero public SEO value |

### P2-4 Refuted
`forum/[...slug].js:82-95` hardcoded URL is in help sub-section. Forum's own canonical at :56 correctly uses `NEXT_PUBLIC_DOMAIN`. Issue real but confined to help widget — P2 appropriate.

### Tech Debt Counts — VERIFIED
- "21 pages mix Head+NextSeo" — plausible, not inflated
- "15+ missing canonicals" — understated, actual ~20-25

---

## Confirmed Ship List

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

### M5 — forum/index.js secureUrl
- **File:** `pages/forum/index.js:90-97`
- **Status:** ALREADY FIXED — `secureUrl: ogImagePath` at :93. No change needed.
- **Audit note:** Fix was applied after report written. Current code clean.

### M6 — locations/[slug].js secureUrl
- **File:** `pages/locations/[slug].js:159-167`
- **Status:** ALREADY FIXED — `secureUrl: ogImagePath` at :165. No change needed.
- **Audit note:** Fix was applied after report written. Current code clean.

### M7 — help/index.js relative image
- **File:** `pages/help/index.js:45`
- **Bug:** `const selectedGroupImage = bgDefaultImage1.src` → relative path passed downstream
- **Fix:** `const siteUrl = process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th'; const selectedGroupImage = \`${siteUrl}${bgDefaultImage1.src}\``

---

## P2 — Minor (separate branch, non-blocking)

| File | Line | Issue | Priority | Notes |
|------|------|-------|----------|-------|
| `pages/privacy/index.js` | 23 | Manual `<title>` bypasses `titleTemplate` | **→ P1** | description also says "Terms" (see M3) — dual bug |
| `pages/terms/index.js` | 25 | Same — manual `<title>` | P2 | |
| `pages/about/index.js` | 44 | Same — manual `<title>` | P2 | |
| `pages/forum/[...slug].js` | 82–95 | Hardcoded `https://smartenplus.co.th` in help sub-section | P2 | Forum canonical at :56 correct. Issue confined to help widget. |
| `pages/bookings/index.js` | — | Auth page: zero SEO meta, no noindex | **→ P1** | crawl budget leak — auth page has no public SEO value |
| `pages/checkout/index.js` | — | Same — only bare `<title>`, no noindex | **→ P1** | same — auth-gated, no public content |
| `pages/help/[...slug].js` | 87–93 | OG `images[]` missing `width` + `height` | P2 | |

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

## Confirmed Ship List (from audit team)

### Ship Now — `260523-fix/seo-wave2-og-and-hydration`
| ID | File | Line | Bug | Fix |
|----|------|------|-----|-----|
| C1 | `airport-transfer/index.js` | 65-66 | bgDefault.src relative | siteUrl template |
| C2 | `blog/categories/index.js` | 17 | hydration mismatch + stale env var | getSiteUrl() import |
| C3 | `blog/categories/[slug].js` | 32,50,150 | same hydration + relative at :50,:150 | getSiteUrl() + siteUrl template |
| M1 | `blog/search/[...slug].js` | 129,164 | NEXT_PUBLIC_SITE_URL stale + :164 relative fallback | getSiteUrl() + siteUrl template |
| M2 | `_app.js` | 33-46 | DefaultSeo missing url + images[] | add openGraph url + images |
| M3 | `privacy/index.js` | 24 | description says "Terms and Conditions" | correct privacy description |
| M4 | `forum/createtopic.js` | 61-66 | secureUrl missing | add secureUrl: ogImagePath |
| M7 | `help/index.js` | 45 | bgDefaultImage1.src relative | siteUrl template |

M5, M6: already fixed — no-op.

### P2-Promoted to Same Branch
| ID | File | Issue |
|----|------|-------|
| P2-1 | `privacy/index.js` | description copy-paste (same as M3, but also :23 title bypass) |
| P2-5 | `bookings/index.js` | add `<NextSeo noindex title="My Bookings">` |
| P2-6 | `checkout/index.js` | add `<NextSeo noindex title="Checkout">` |

### Separate Branch — P2 Minor
| File | Line | Issue |
|------|------|-------|
| `terms/index.js` | 25 | Replace `<Head><title>` with `<NextSeo>` |
| `about/index.js` | 44 | Same |
| `forum/[...slug].js` | 82-95 | getSiteUrl() in help sub-section |
| `help/[...slug].js` | 87-93 | Add width/height to OG images |

### Future — Tech Debt Branch
- 21 pages mix `<Head>` + `<NextSeo>` (canonical deduplication + duplicate meta cleanup)
- ~20-25 pages missing canonical tags
- Component size violations (homepagev2 584L, trips 716L, detail 469L, Passengers 1146L, SlideCalendar2 1035L)

---

## Recommended Branch Strategy
```
260523-fix/seo-wave2-og-and-hydration   ← P0 + P1 confirmed + P2-promoted
260523-fix/seo-wave2-p2-minor            ← P2 items (terms, about, forum help, help/[...slug])
(future) tech-debt/seo-canonical-meta   ← tech debt
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
