---
name: brand-name-constant-extraction
description: Extract brand name to single constant. "SmartEnPlus" wordmark vs "smartenplus.co.th" URL. Rename smartenpus-...webp typo.
type: knowledge-atom
date: 2026-06-06
parent: website-audit-full-2026-06-06-overview
---

# Brand Name Constant Extraction

## Summary
Add `BRAND_NAME = 'SmartEnPlus'` to `helpers/constants.js`. Replace all hardcoded `'SmartEnPlus'` strings. URL stays `smartenplus.co.th` (SEO debt, cannot change). Rename `smartenpus-...webp` filename typo.

## Context
Audit Identity P3: brand name inconsistency across codebase. Logo wordmark "SmartEnPlus" (capital E), URL "smartenplus.co.th" (lowercase, no E), DefaultSeo mixed, schema provider.name mixed, filename typo `smartenpus-...webp`.

## Problem
Hardcoded brand strings scattered across:
- `pages/_app.js:34, 35, 41, 47` (DefaultSeo)
- `lib/homepage/components/PopularRoutesStructuredData.js:31, 60` (provider)
- `lib/homepage/components/LocationsStructuredData.js:65, 71` (provider)
- `lib/homepage/components/ReviewsStructuredData.js:64, 66`
- `public/smartenpus-transportation-booking-online.webp` (typo)

## Pattern
**Constant** (`helpers/constants.js`):
```js
export const BRAND_NAME = 'SmartEnPlus';
```

**Usage** (replace hardcoded strings):
```js
import { BRAND_NAME } from '../../helpers/constants';
// ...
"name": BRAND_NAME,
"url": "https://smartenplus.co.th",  // URL stays
```

**Filename fix:**
- Rename `public/smartenpus-transportation-booking-online.webp` → `public/smartenplus-transportation-booking-online.webp`
- Update imports in `components/blog/BlogPostHeader.js:5`

## Decision
Standardize on "SmartEnPlus" wordmark for display. URL stays "smartenplus.co.th" (SEO debt, cannot change). Add `BRAND_NAME` constant. Rename typo file.

## Tradeoffs
- **Pro:** Single source of truth for brand name
- **Pro:** Easier to update if/when URL changes
- **Pro:** Fixes `smartenpus` typo (silent bug)
- **Con:** ~15-20 file changes (low risk, mechanical)

## Consequences
Reference [[nav-label-url-slug-two-layer-strategy]] for URL/label split rationale. Reference [[production-url-rename-cost-framework]] for URL change cost analysis.

## Broader Scope (2026-06-13 Audit)

Design system audit `design-system-audit` confirms 23 occurrences of brand string across `pages/_app.js` (DefaultSeo), `lib/homepage/components/*StructuredData.js` (provider.name), and the `public/smartenpus-*.webp` filename typo. The 5 files listed above are the highest-traffic subset; full list in the audit. The `BRAND_NAME` constant + rename is the only safe migration path.

## Related
[[website-audit-full-2026-06-06-overview|website-audit-full-2026-06-06]] · [[r3-leader-synthesis]] · [[r1-seo-ai]] · [[nav-label-url-slug-two-layer-strategy]]
