# /help/faqs WordPress GraphQL Returns Empty in Production

## Summary
`pages/help/faqs.js` `getServerSideProps` calls `POSTS_BY_FAQ_CATEGORY` WordPress GraphQL query which returns `data?.posts?.nodes = []` in production. The FAQPage schema renders as `{"@type":"FAQPage","mainEntity":[]}` — invalid for rich results, potentially penalized by Google.

## Problem
Two compounding bugs:

**Bug 1 — Data fetch broken in production:**
- `getServerSideProps` calls `POSTS_BY_FAQ_CATEGORY` GraphQL
- Returns empty array in prod (category slug or tag mismatch in WP)
- Catch block silently returns `{ props: { faqs: [] } }`
- FAQPage schema: `mainEntity: faqs.map(...)` → renders as `[]`
- Google requires ≥1 Q/A pair; empty FAQPage may trigger rich-result penalty

**Bug 2 — Answer text is client-only even when data loads:**
- Answer HTML sanitized by DOMPurify inside `useEffect` at line 43–47
- Rendered via `dangerouslySetInnerHTML` — client-only
- SSR crawlers (Googlebot, AI engines) receive only `<details>/<summary>` shell with empty content divs
- `stripHtml(p.content)` fallback goes into schema text server-side — OK
- But formatted answer display is JS-only

## Fix
1. Debug `POSTS_BY_FAQ_CATEGORY` query — check WP category slug in production vs staging
2. Add error logging in the catch block (currently silently swallows the empty result)
3. Move answer text rendering server-side: `stripHtml(post.content)` → render in SSR, no DOMPurify for crawlers
4. Fix `og:url` on `/help/faqs` — currently points to `https://www.smartenplus.co.th` (root), should be `https://www.smartenplus.co.th/help/faqs`

## Detection
```bash
# Verify live schema
curl -s https://www.smartenplus.co.th/help/faqs | grep -o '"mainEntity":\[[^]]*\]'
# If empty: mainEntity:[]
```

## Impact
- `/help/faqs` is the only dedicated FAQ page with schema infrastructure
- AEO score: 1/10 live (was counted as working in r4-peer-review — incorrect)
- Live verified empty 2026-06-22

## Related
[[seo-aeo-geo-live-audit-2026-06-22/r5-live-reaudit]] · [[wordpress-faqpage-deprecation-note]] · [[nextseo-v6-jsonld-silent-drop]]
