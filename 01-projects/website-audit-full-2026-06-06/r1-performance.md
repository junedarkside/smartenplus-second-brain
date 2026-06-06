---
name: r1-performance
description: Performance/CWV specialist findings — Speed 40/100 root cause. Maps audit C1-C3 + H1-H5 to SmartEnPlus file:line evidence.
type: specialist-finding
parent: website-audit-full-2026-06-06
specialist: Performance/CWV Engineer
date: 2026-06-06
---

# R1 — Performance/CWV Engineer

## Pre-existing wins (NOT work to do)

- `next.config.js:8` — `compress: true` already set
- `next.config.js:16` — `formats: ['image/webp', 'image/avif']` already set
- `next.config.js:122-128` — HSTS + Permissions-Policy present
- `pages/_app.js:33-66` — DefaultSeo present with full OG/Twitter
- `pages/server-sitemap.xml` exists at `pages/server-sitemap.xml` (referenced in `next-sitemap.config.js:10-12`)
- `helpers/imageOptimization.js:41-53` — `convertToWebP()` already adds `?format=webp&quality=N` for S3 URLs
- `components/UI/FeaturedImageHeader.js:18-32` — uses `priority={true}`, `placeholder="blur"`, `getOptimizedImageSizes('hero')`, `getOptimalImageQuality()`

## Findings (file:line evidence)

### PERF-1 — Inter woff2 not preloaded (Audit H2)
- **Severity:** High
- **Audit ID:** H2
- **File:line:** `pages/_document.js:20-22`
- **Evidence:**
  ```
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
  ```
  Preconnect exists. `rel="stylesheet"` triggers render-blocking fetch. No `<link rel="preload" as="font">`.
- **Fix:** Add `<link rel="preload" as="font" type="font/woff2" href="<woff2 url>" crossOrigin="anonymous" />`. Woff2 URL must be extracted from Google Fonts CSS response.
- **Impact:** FCP -0.3s, eliminates FOIT
- **Effort:** small (1-2 hrs to identify woff2 URL + add preload)
- **Risk:** low — preload for woff2 is widely supported
- **Variance:** can self-host Inter via `next/font` instead — eliminates 3rd-party CSS call entirely (separate PR, ~2 hrs)

### PERF-2 — Inline `style={{}}` concentration in ProfileMenu + OrderDetail (Audit C3)
- **Severity:** Critical (matches audit C3 "66 inline style blocks")
- **Audit ID:** C3
- **File:line:** Top 5 offenders (213 total in `components/`):
  - `components/auth/ProfileMenu.js` — 20 instances
  - `components/order/OrderDetail.js` — 18
  - `components/layout/layout.js` — 14
  - `components/search/ProductSearchForm2.js` — 9
  - `components/search/ProductSearchForm.js` — 8
- **Evidence (ProfileMenu.js:20):**
  ```
  boxShadow: '0 8px 24px rgba(0,0,0,0.10), 0 2px 8px rgba(0,0,0,0.06)',
  ```
  Most are `boxShadow`, dynamic transform (rotate/translate), and conditional colors. Not arbitrary Tailwind.
- **Fix:** Audit each:
  - Static `boxShadow` → extract to `BUTTON_CONFIG.elevated.boxShadow` in `designSystem.js`
  - Dynamic transforms (loading spinners) → keep inline (required for runtime state)
  - Conditional colors → use `clsx` + existing design tokens
- **Impact:** FCP -0.5s, caching improvement, ~10KB reduction
- **Effort:** medium (3 hrs for audit + extraction)
- **Risk:** low if scoped to static values only

### PERF-3 — Inter loaded via render-blocking stylesheet (Audit H2 secondary)
- **Severity:** Moderate
- **Audit ID:** H2 (related to PERF-1)
- **File:line:** `pages/_document.js:22`
- **Evidence:** `<link rel="stylesheet">` for Google Fonts blocks rendering until CSS parsed.
- **Fix:** Switch to `next/font/google` with `Inter` (auto-self-hosts, eliminates render-blocking external CSS).
- **Impact:** FCP -0.2s, eliminates 3rd-party DNS
- **Effort:** medium (2-3 hrs — verify no FOUT, test CLS, add to `_app.js`)
- **Risk:** medium — FOUT possible if font swap behavior differs

### PERF-4 — `server-sitemap.xml` exists but no `data-href` deferred stylesheet detected
- **Severity:** Informational
- **Audit ID:** H4
- **File:line:** Searched codebase for `data-href` CSS pattern — 0 hits in source code
- **Evidence:** Audit claims 1 deferred stylesheet. May be from external 3rd-party widget (Cloudflare Insights per H5) or non-configurable GTM injection.
- **Fix:** Investigate via Chrome DevTools "Coverage" tab. Likely tied to H5 (Cloudflare beacon).
- **Impact:** TBD (depends on stylesheet size)
- **Effort:** small (30 min investigation)
- **Risk:** low

### PERF-5 — Cloudflare Insights beacon overhead (Audit H5)
- **Severity:** Moderate
- **Audit ID:** H5
- **File:line:** Searched `_document.js`, `_app.js` for `cloudflareinsights` — 0 hits in source
- **Evidence:** Likely injected by Cloudflare (server-side or via Worker).
- **Fix:** Verify if actively monitored. If no dashboard user → disable in Cloudflare dashboard. If needed → defer with `<script defer>`.
- **Impact:** -50ms per page
- **Effort:** trivial (5 min in Cloudflare dashboard)
- **Risk:** low — analytics only

### PERF-6 — Search inputs use 14px font (triggers iOS zoom) (Audit MM1)
- **Severity:** Critical
- **Audit ID:** MM1
- **File:line:** `components/search/ProductSearchForm2.js:231, 260, 283, 311` — multiple `text-sm` classes
- **Evidence:**
  ```
  className={`text-sm md:text-sm text-decoration-none ...`}
  ```
  Also `components/search/SearchDialogTrigger.js:19` — `text-sm`
- **Fix:** Change `text-sm` → `text-base` in search inputs (and update `INPUT_CONFIG.base` in `designSystem.js:188` to enforce)
- **Impact:** Fixes iOS auto-zoom bug. ~30 min work.
- **Effort:** trivial (30 min)
- **Risk:** low — visual change is <2px
- **Note:** Design system already has `body: 'text-sm sm:text-base'` scale but search forms override it

### PERF-7 — `getOptimizedImageSizes` limited to 4 types (Audit H3 follow-up)
- **Severity:** Informational
- **Audit ID:** H3 (image dimension enforcement)
- **File:line:** `helpers/imageOptimization.js:23-32`
- **Evidence:** Only `hero | gallery | thumbnail | card` types. All use `fill` mode in FeaturedImageHeader, so dimensions controlled by parent. `width/height` not set in audit image samples.
- **Fix:** Audit `<Image>` usages for missing explicit dimensions. Use Next.js `placeholder="blur"` + aspect-ratio containers for known-size cards.
- **Impact:** CLS -0.05
- **Effort:** medium (2-3 hrs to audit all `<Image>`)
- **Risk:** low

## Pre-existing scripts analysis (Audit C2 — 10 sync scripts)

- `_document.js` — only 1 script (`<NextScript />`). Not 10.
- `_app.js:80-85` — GTM via `next/third-parties/google` with `strategy="afterInteractive"` ✓
- Audit's "10 sync scripts" likely refers to combined bundle chunks at runtime
- Next.js auto-splits — manual `defer/async` not needed for `next/script` calls
- **Verdict:** Audit C2 partially miscounted. GTM/Omise (3rd party) are unavoidable sync.

## Top 3 Wins

1. **PERF-1/3 — Inter font preload/self-host** (1-3 hrs, FCP -0.5s)
2. **PERF-2 — Extract inline styles to design tokens** (3 hrs, FCP -0.5s)
3. **PERF-6 — 14px → 16px in search inputs** (30 min, iOS zoom fix)

## Key Files

- `pages/_document.js` — font preconnect, Inter stylesheet
- `next.config.js` — image formats, compress, headers
- `helpers/imageOptimization.js` — `getOptimizedImageSizes`, `convertToWebP`
- `helpers/designSystem.js` — `TOUCH_TARGET`, `INPUT_CONFIG` (typography enforcement)
- `components/UI/FeaturedImageHeader.js` — hero Image with priority + blur
- `components/auth/ProfileMenu.js` — top inline-style offender (20)
- `components/order/OrderDetail.js` — 18 inline styles
- `components/layout/layout.js` — 14 inline styles
- `components/search/ProductSearchForm2.js` — 9 inline styles + 14px text-sm

## Related

[[homepage-seo-performance-deep-review-2026-05-21]] (prior SEO+perf audit, 30 findings — most already fixed)
