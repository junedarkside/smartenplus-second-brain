# /ref/* URL Structure: Live URL vs Code File Path

## Summary
The Next.js page file for reference articles is at `pages/ref/article/[slug].js` but the **live public URL** is `/ref/{slug}` (no `/article/` segment). These are different. Multiple prior audits confused the file path with the public URL and drew incorrect conclusions.

## Facts (live verified 2026-06-22)

| URL | HTTP status | Notes |
|-----|:-----------:|-------|
| `/ref/{slug}` | **200 OK** | Correct live URL |
| `/ref/article/{slug}` | **404** | File path ≠ public URL |

- `server-sitemap.xml` generates `/ref/{slug}` — **CORRECT**
- `CitationSection.js:32` generates `https://www.smartenplus.co.th/ref/${slug}` — **CORRECT**
- `pages/ref/article/[slug].js:91` canonical: `https://www.smartenplus.co.th/ref/${slug}` — **CORRECT**
- `sitemap-0.xml` lists 41 `/ref/article/{slug}` URLs — **WRONG — all 404**

## What is actually broken
`sitemap-0.xml` contains 41 `/ref/article/{slug}` URLs that all return 404. These must be removed and replaced with `/ref/{slug}` format. This is a `next-sitemap.config.js` / build configuration problem, not a page component bug.

## What is NOT broken (despite prior audit claims)
- The page component canonical is correct
- The server-sitemap is correct
- `CitationSection.js` generates correct URLs
- The `/ref/` content system as a whole is functional

## Audit history of this confusion
- `r1-seo` (2026-06-22): called `/ref/{slug}` canonical "wrong path" — incorrect
- `r3-synthesis` (2026-06-22): said "bonus bug: pages self-canonical to `/ref/{slug}` (wrong path)" — incorrect
- `r4-peer-review` (2026-06-22): said `CitationSection.js` generates "broken `/ref/article/` URLs" — incorrect
- `r5-live-reaudit` (2026-06-22): live HTTP verification corrected all above

## Fix
Remove `/ref/article/*` entries from `sitemap-0.xml` generation in `next-sitemap.config.js`. Redeploy + clear ISR cache.

## Related
[[seo-aeo-geo-live-audit-2026-06-22/r5-live-reaudit]] · [[canonicalization-audit-checklist]] · [[seo-sitemap-whole-site-audit-2026-06-11]]
