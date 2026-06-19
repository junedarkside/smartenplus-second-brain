# Next.js getStaticPaths + getStaticProps Constant Divergence Trap

## Summary
Sharing a category/type constant between `getStaticPaths` and `getStaticProps` is mandatory — not optional. Divergence is a silent routing failure: pages pre-built but redirected at runtime, no build error, no 404.

## Context
Extracted from [[trip-detail-deep-review]] (H8 finding). Discovered in `TRANSPORTATION_CATEGORIES` constant in trip detail page. Applies to any Next.js page using type/category filtering at both build-time path generation and runtime redirect logic.

## Problem

```js
// BAD — constants duplicated in two places
// getStaticPaths uses:
const CATEGORIES = ['TRANSPORTATION', 'TRANSFER']

// getStaticProps uses (different scope):
const PRODUCT_CATEGORIES = ['TRANSPORTATION']  // TRANSFER missing!
```

**Result:** `TRANSFER` slugs pre-built (getStaticPaths) but runtime redirects them away (getStaticProps missing TRANSFER) → silent routing failure. No build error, no 404 — just wrong redirect.

**Compounding factor:** Adding a new type (e.g., `'SHUTTLE'`) to paths but not to props means shuttle pages pre-built then redirected at runtime. No visibility until user reports broken URL.

## Fix

Module-level constant, imported in both functions:

```js
// GOOD — module level, single source of truth
const TRANSPORTATION_CATEGORIES = ['TRANSPORTATION', 'TRANSFER'];

export async function getStaticPaths() {
  // uses TRANSPORTATION_CATEGORIES
}

export async function getStaticProps({ params }) {
  // uses TRANSPORTATION_CATEGORIES — guaranteed same set
}
```

## Tradeoffs
- Module-level constant adds 1 line
- Eliminates entire class of silent routing failure
- Required, not optional — treat as mandatory pattern in any route-type filtered page

## Related
- [[nextjs-patterns]] — Next.js patterns home
- [[trip-detail-deep-review]] — source finding (H8)
- [[nextjs-307-vs-301-product-reclassify]] — related redirect correctness pattern
