# Pages Router `notFound` Return Shape

## Summary
In Next.js **Pages Router**, a 404 is returned by `return { notFound: true }` from `getStaticProps`/`getServerSideProps` — NOT by calling `notFound()` (that's App Router). Returning a thrown/empty `props` object instead yields a **200 with error UI** or a **500**, both bad for SEO.

## Problem
`pages/help/[...slug].js` `getServerSideProps` had no `notFound` path. On a missing/failed WP fetch it returned `props: { data: null, error }`. The component then dereferenced `data.title` on null → **500** on 53 of 57 help pages. External audit flagged "500s" but prescribed App Router `notFound()` (wrong for this repo).

## Pattern
```js
export async function getServerSideProps(context) {
  let data = null, error = null;
  try { /* fetch */ } catch (e) { error = '...'; }

  // 404 when the entity is genuinely absent OR the fetch failed hard.
  // Converts would-be 500s + empty-200s into clean 404s (stops crawl-budget drain).
  if (error || !data) {
    return { notFound: true };
  }
  return { props: { data } };
}
```
- `getStaticProps`: same `return { notFound: true }` (also accepts `notFound: true` for a single dynamic path).
- `getServerSideProps`: same.
- App Router: `import { notFound } from 'next/navigation'; if (!x) notFound();` — different API, do not mix.

## When to use
- Any dynamic route (`[slug]`, `[...slug]`) where the backing entity may not exist.
- Guard BOTH the whole-object-null case AND the missing-required-field case:
  ```js
  if (!stationData || !stationData.station_name) return { notFound: true };
  ```
  (The destinations "Travel to undefined" bug was a missing-field case — `getStaticProps` guarded the object but not the field.)

## Gotcha
A 200-with-garbage-content ("Travel to undefined", empty error div) is **worse** than a 404 — Google indexes thin/doorway pages. Prefer a hard 404 when the data to render a real page isn't there.

## Related
- [[seo-aeo-geo-live-audit-2026-06-22/r6-external-reconciliation-2026-06-25]] (C3 help 500→404, C2 destinations)
- [[ref-url-structure-live-vs-code]] — file path vs public URL gotcha on the same route family
