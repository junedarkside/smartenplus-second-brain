---
name: trip-detail-page-review
description: 3-agent review of pages/trips/detail/[...slug].js — perf, SEO, code quality findings with verified line numbers
metadata:
  type: project
---

# Trip Detail Page Review — 2026-05-20

> ⚠️ **SUPERSEDED 2026-06-16** — Predates the server-side SEO refactor. `useTripSEO.js` was **deleted** and replaced by `helpers/seo/tripDetailSEOUtils.js` + a rewritten `components/trips/detail/TripDetailSEO.js` (schema moved into `getStaticProps`). The SEO findings below citing `useTripSEO.js` (e.g. S8) were resolved in that refactor — see [[trip-detail-seo-aeo-geo-audit-2026-06-16/r2-leader-synthesis]] (7/7 HIGH fixed). Findings retained as historical record; candidate for [[08-archive]].

## Summary
3-agent team (SSR/Perf · SEO · Code Quality) reviewed `pages/trips/detail/[...slug].js`. 24 issues found. Leader-filtered — false positives removed.

## Context
Branch `260520-update/recommend-route`. ~481 lines. ISR (revalidate: 300). RTK Query for contract refresh, dynamic imports. *(2026-05-20: SEO via client `useTripSEO` hook; **deleted 2026-06-16**, now server-side `tripDetailSEOUtils.js`.)*

---

## PERFORMANCE ISSUES

### 🔴 P1 — Reviews double-fetch (line 222–241)
Client mount fetches entire `/product-detail/${slug}/` for `data.reviews`. ISR already baked reviews in `productData`. Redundant fetch of large object.
**Fix:** Remove useEffect. Use `productData.reviews` from ISR. If fresh needed, add dedicated `/reviews/?slug=` endpoint.

### 🔴 P2 — `isClient` forced double-render (line 65, 174–177)
`useState(false)` + `useEffect(() => setIsClient(true), [])` forces second render every page load. Gates reviews fetch, passed to `TripDetailHero`. CLS + INP degradation.
**Fix:** Remove `isClient` and its useEffect. Tied to P1.

### 🔴 P3 — `require()` inside `loading:` render fn (line 44–49)
```js
loading: () => {
  const { FeaturedImageHeaderSkeleton } = require('...'); // runs on every loading render
  return <FeaturedImageHeaderSkeleton />;
}
```
**Fix:** Move to top-level static import.

### 🔴 P4 — `DynamicStandardBreadcrumb` has `ssr: false` (line 19)
Breadcrumb absent from static HTML. Googlebot misses it. JSON-LD breadcrumb in TripDetailSEO orphaned.
**Fix:** Remove `{ ssr: false }`. StandardBreadcrumb is simple nav — no need for client-only.

### 🟡 P5 — `refetchOnFocus/Reconnect` too aggressive (line 84–85)
`refetchOnFocus: true` + `refetchOnReconnect: true` on useCheckContractQuery. Tab switch = API hit. Defeats ISR for static fields.
**Fix:** Keep `refetchOnMountOrArgChange: true`. Remove `refetchOnFocus` and `refetchOnReconnect`.

### 🟡 P6 — `domainURL` from `router.asPath` unstable at hydration (line 116)
`router.asPath` empty during SSR → canonical URL wrong first render → passed to TripDetailSEO → extra re-render when router stabilizes.
**Fix:** Use `router.isReady` guard or derive canonical from `productData.slug` (static, SSR-available).

### 🟡 P7 — `setTimeout(100)` scroll hack (line 251)
Fragile. 100ms may not suffice on slow devices.
**Fix:** Use `requestAnimationFrame` or `router.isReady` guard.

### 🟢 P8 — `console.log` in production build path (line 424)
Build-time noise in `getStaticPaths`. Remove.

---

## SEO ISSUES

### 🔴 S1 — Day-tour redirect is 307, should be 301 (line 468)
```js
permanent: false, // 307 temporary — no link equity transfer
```
Day tours never at `/trips/detail` — redirect permanent by design.
**Fix:** `permanent: true` → 308 redirect. Consolidates link equity to `/daytrips/detail/`.

### 🔴 S2 — Emoji `✅` in `<title>` (line 128)
Mojibake in some crawlers. Wastes 3 chars of 60-char SERP budget.
**Fix:** Remove `✅`. Plain `starting at THB ${lowestRate}`.

### 🔴 S3 — Title exceeds 60-char SERP limit (line 122–130)
Format: `[Route] (HH:MM - HH:MM) with [Operator] starting at THB [price]` = 70–100 chars typically.
**Fix:** Restructure: `"[Route] from THB [price] | [Operator]"` — fits ~55 chars.

### 🔴 S4 — Description reuses title + filler (line 132)
```js
const description = `Book reliable transport from ${title}. Reserve now!`;
```
Title 72 chars → description 104+ chars (truncated). Title duplicated.
**Fix:** Pull from `productData.description` or `productData.route.route_info`.

### 🟡 S5 — `DynamicReviewListByProduct` has `ssr: false` (line 51)
Review text absent from static HTML. Googlebot misses reviews. AggregateRating claims reviews exist but crawlers can't verify.
**Fix:** Remove `ssr: false`.

### 🟡 S6 — Broken `aria-labelledby` (lines 350, 370)
```jsx
<section aria-labelledby="trip-details-heading">  // no element id="trip-details-heading"
<section aria-labelledby="reviews-heading">        // no element id="reviews-heading"
```
Screen readers announce nothing.
**Fix:** Add `<h2 id="trip-details-heading">` inside each section, or change to `aria-label="..."`.

### 🟡 S7 — "Pricing Unavailable" state indexable thin content (line 288)
`lowestRate === null` renders empty state but page stays indexed. Google sees thin content.
**Fix:** Return `notFound: true` from `getStaticProps` if no ratecard, or add `<meta name="robots" content="noindex" />`.

### 🟢 S8 — Fake phone/coords in LocalBusiness schema (`useTripSEO.js` ~line 290)
`"+66-2-123-4567"` placeholder. Hardcoded Bangkok coords regardless of route origin.
**Fix:** Remove phone/geo from schema if real values unavailable.

---

## CODE QUALITY ISSUES

### 🔴 C1 — `useCallback` imported, never used (line 1)
Dead import. Remove.

### 🔴 C2 — `capitalizeFirstLetter` imported, never used (line 11)
Dead import. Remove.

### 🔴 C3 — `.map()` returns array, coerced to comma-string in GTM event (line 193)
```js
item_variant: `${productDataForGTM?.transport_composit?.map((item) => item?.transport_composit) || ''} `
// → "Bus,Ferry " (accidental + trailing space)
```
**Fix:** `.join(' + ')` and trim trailing space.

### 🔴 C4 — Typo `'forword'` propagates to API/URL params (line 134)
```js
const defaultDirection = 'forword'; // should be 'forward'
```
If backend expects `'forward'`, direction filtering silently broken.
**Fix:** `'forward'`. Verify backend expected value.

### 🟡 C5 — `useMemo` on `.length` — zero benefit (line 135)
```js
const totalReviews = useMemo(() => reviews.length, [reviews]);
```
`.length` is O(1). No memoization needed.
**Fix:** `const totalReviews = reviews.length;`

### 🟡 C6 — `description` not memoized, recalculates every render (line 132)
`title` memoized but `description` derived inline.
**Fix:** Wrap in `useMemo`. Or fix S4 first, then memoize.

### 🟡 C7 — `notFound` no default value (line 60)
```js
const TripDetail = memo(({ productData, notFound }) => {
```
**Fix:** `notFound = false` explicit default documents intent.

### 🟢 C8 — `TRANSPORTATION_CATEGORIES` duplicated in same file (lines 400, 460)
Identical in `getStaticPaths` and `getStaticProps`.
**Fix:** Hoist to module level or import from `helpers/constants.js`.

---

## Quick-Win Order

| Priority | Fix | Effort |
|----------|-----|--------|
| 1 | C1+C2 dead imports | 30 sec |
| 2 | C4 typo `'forword'` | 1 line |
| 3 | S1 redirect `permanent: true` | 1 line |
| 4 | S2 remove emoji from title | 1 line |
| 5 | P3 move `require()` to top-level import | 3 lines |
| 6 | P4 remove `ssr: false` from breadcrumb | 1 char |
| 7 | P1+P2 remove reviews fetch + `isClient` | ~10 lines removed |
| 8 | C8 hoist `TRANSPORTATION_CATEGORIES` | 3 lines |
| 9 | S3+S4 rewrite title/description | 10 lines |
| 10 | S5 remove `ssr: false` from reviews | 1 char |

## Related
[[nextjs-patterns]] · [[blog-seo-performance]] · [[hydration-infinite-refresh-fix]] · [[recommendation-system]]