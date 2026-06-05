# Production URL Rename Cost Framework

## Summary
Decision framework for whether to rename a production URL slug on smartenplus.co.th.

## Context
Needed during homepage terminology audit (2026-06-05). Multiple agents recommended URL renames without accounting for production SEO history and codebase reference count.

## Decision Framework

**Never rename if:**
- Codebase references > 100 (e.g. `/trips` = 141 refs across 31 component files)
- URL has multi-year Google indexing history + likely external backlinks
- Page is linked from footer, sitemap, service worker cache routes

**Rename acceptable if:**
- References < 30 AND no confirmed external backlinks
- OR: confirmed true duplicate content (two pages serving identical data) — consolidation justified despite cost
- Must always add 301 permanent redirect from old → new
- Must update sitemap to remove old URL

**Cost tiers:**
| Refs | SEO Age | Decision |
|------|---------|----------|
| >100 | Any | NEVER |
| 26–99 | Multi-year | HIGH risk — requires redirect + full QA |
| <25 | <1 year | MEDIUM — doable with redirect |
| <10 | Any | LOW — rename + redirect |

## SmartEnPlus Specific Verdicts (2026-06-05)
- `/trips` — 141 refs → NEVER rename
- `/activities` — 26 refs + /daytrips redirect already exists + multi-year indexing → keep, change display labels only
- `/locations` → `/destinations` consolidation → BLOCKED (different products, not true duplicates)

## How to Evaluate "True Duplicate"
Two pages are true duplicates only if:
1. Same API endpoint called
2. Same data structure rendered
3. Same user intent served

If any differs → NOT a duplicate. Do not add canonical or redirect.

## Redirect Chain Rule
Existing chains in next.config.js: `/daytrips` → `/activities`. Any new redirect must not create chains >2 hops. Google devalues chains >3 hops.

## Related
- [[nav-label-url-slug-two-layer-strategy]]
- [[locations-destinations-product-split]]
- [[nextjs-307-vs-301-product-reclassify]]
- [[homepage-terminology-audit-2026-06-05]]
