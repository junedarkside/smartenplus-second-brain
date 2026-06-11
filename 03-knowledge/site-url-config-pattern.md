# Site URL config pattern

## Problem
- Schema builders use `baseURL` (API domain `https://api.smartenplus.co.th`)
- OG/canonical need `NEXT_PUBLIC_DOMAIN` (front end `https://www.smartenplus.co.th`)
- Mixing both = broken URLs in structured data + OG
- Deploy default `smartenplus.co.th` (no scheme, no www) defeats fallback → apex/schemeless URLs

## Solution

**Per-file module const:**
```js
const siteUrl = process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th';
```

Use `siteUrl` for ALL schema URL fields (Organization.url, seller.url, breadcrumb items, og:url, canonical, etc). Never `baseURL` outside fetch calls.

**Deploy default (scripts/deploy-ghcr.sh):**
```bash
# Before
NEXT_PUBLIC_DOMAIN=${NEXT_PUBLIC_DOMAIN:-smartenplus.co.th}

# After
NEXT_PUBLIC_DOMAIN=${NEXT_PUBLIC_DOMAIN:-https://www.smartenplus.co.th}
```

**Code fallback pattern:**
```js
const siteUrl = process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th';
// Use siteUrl everywhere
```

Fallback catches dev/test; deploy default serves prod fallback; code never guesses.

## Files fixed (smartenplus-frontend 2026-06-12)
- `hooks/useTripSEO.js` — module `siteUrl` const, 2 refs removed
- `helpers/seo/dayTripSEOUtils.js` — module `siteUrl`, 8+ refs from baseURL swapped
- `lib/homepage/components/*StructuredData.js` (5 files) — hardcoded `https://smartenplus.co.th` → `https://www.smartenplus.co.th`
- `pages/activities/detail/[...slug].js` — canonical from baseURL.replace → NEXT_PUBLIC_DOMAIN
- `pages/server-sitemap.xml/index.js` — deploy default (already correct, just verify)

## Related
[[seo-sitemap-whole-site-audit-2026-06-11]] (P1-2, P2 host fixes)
