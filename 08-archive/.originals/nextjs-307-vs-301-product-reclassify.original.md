# Next.js 307 vs 301 — Product Reclassification Risk

## Summary
Keep `permanent: false` (307) on product-type redirects — 301 causes permanent browser/CDN cache pollution if product is reclassified.

## Why It Matters
Products can change type (e.g., DAY_TOUR → TRANSPORTATION). After a 301, users and CDNs are permanently stuck on the old path — ISR revalidation cannot undo a cached 301 in a user's browser.

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

301 permanently caches in browser + CDN. If operator later reclassifies product back, those users never see the new route without clearing cache.

307 has lower SEO link equity transfer but is safe for mutable classifications.

## Constraints / Gotchas
- This is the OPPOSITE of the usual SEO advice ("always use 301")
- Document with a comment in code so future devs don't "fix" it
- `TRANSPORTATION_CATEGORIES` constant must be kept in sync across `getStaticPaths` + `getStaticProps` — divergence causes silent routing failure with no build error

## Related
- [[nextjs-patterns]]
- [[trip-detail-deep-review]]
