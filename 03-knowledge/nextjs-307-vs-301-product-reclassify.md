# Next.js 307 vs 301 — Product Reclassification Risk

## Summary
Keep `permanent: false` (307) on product-type redirects — 301 causes permanent browser/CDN cache pollution if product reclassified.

## Why It Matters
Products change type (e.g., DAY_TOUR → TRANSPORTATION). After 301, users + CDNs stuck on old path — ISR revalidation cannot undo cached 301 in browser.

## Detail
```js
// CORRECT for product-type redirects
return {
  redirect: {
    destination: `/daytrips/detail/${slug.join('/')}`,
    permanent: false, // 307 — intentional, NOT a mistake
  }
}
```

301 permanently caches in browser + CDN. If operator reclassifies product back, those users never see new route without clearing cache.

307 has lower SEO link equity transfer but safe for mutable classifications.

## Constraints / Gotchas
- OPPOSITE of usual SEO advice ("always use 301")
- Document with comment so future devs don't "fix" it
- `TRANSPORTATION_CATEGORIES` constant must stay in sync across `getStaticPaths` + `getStaticProps` — divergence causes silent routing failure, no build error

## Related
- [[nextjs-patterns]]
- [[trip-detail-deep-review]]