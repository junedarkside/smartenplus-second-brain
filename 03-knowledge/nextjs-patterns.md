# Next.js Patterns

## Summary
SmartEnPlus Next.js 14 patterns. Pages Router, Redux Toolkit, RTK Query, ISR, dynamic imports.

## ISR Cache
Trip detail: `revalidate: 300` (5 min). Deploy clears `smartenplus_next_cache` Docker volume. Without volume cleanup, ISR persists stale across deploys.

**`revalidate` is ignored in `next dev`:** `getStaticProps` runs on every request in dev mode regardless of `revalidate` value. ISR only activates in production (`next build` + `next start`). Changing `revalidate` to fix local dev 429s is ineffective. Fix 429s in dev at the backend layer (response cache, throttle rate). See [[isr-429-cold-start-fix-2026-05-23]].

**`getStaticPaths` is build-time only:** Never runs during ISR revalidation at runtime. Only `getStaticProps` runs on ISR revalidation. A dynamic route's `getStaticPaths` hitting an API endpoint is a build concern, not a runtime 429 concern.

## Dynamic SSR Disable
`dynamic(() => Promise.resolve(Index), { ssr: false })` for pages depending on client state (cart, auth). Never add `getServerSideProps` to these.

## RTK Query
- `refetchOnMountOrArgChange: false` — prevents 429 on frequent pages
- `skip` for conditional queries — don't fetch until params ready
- Transform data in RTK endpoint, not components
- `next/image` always, never raw `<img>`

## DatePicker
Store Date objects in Formik. Format to string ONLY at API boundary. Strings in Formik → comparison bugs + timezone issues.

## State Management
- `useState` — UI-only (modals, tabs, inputs)
- Redux — cross-component (cart, auth, checkout)
- `useMemo` — derived values inline
- Max 3 prop levels → move to Redux

## Component Patterns
- Named exports only
- Fetch in parent, pass as props
- Hook when logic >20 lines or reused
- `next/dynamic` + `ssr: false` for heavy components
- No inline objects/arrays in render

## Error Handling
Helpers return `null` + `console.warn`. Never throw from utilities. Guard clauses at function tops.

## Redux Fallback Props
Fresh page load = cold Redux = stale/empty data. Pattern: accept URL-derived props, use `reduxValue || propValue`. `StickySearchBar`: `fromLocationRedux || fromSearch`. `SearchCover`: `fromLocationRedux || initialFromLocation`. Redux wins when populated; URL/prop is fallback.

## Hydration Error Prevention

6 rules + PersistGate SSR blocker pattern. Mismatch in `_app.js` → HMR infinite refresh across all pages.
→ See [[nextjs-hydration-rules]]

## OG Image — Absolute URLs Required

Next.js static imports (`import img from './file.webp'`) produce relative paths like `/_next/static/media/file.hash.webp`. Using `.src` directly in `og:image` = relative URL = Facebook/crawlers can't fetch.

**Fix:** always prepend site URL:
```js
// BAD
const ogImagePath = bgDefaultImage1.src;  // "/_next/static/media/..."

// GOOD
const siteUrl = process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th';
const ogImagePath = `${siteUrl}${bgDefaultImage1.src}`;
```

Applies to: `generateBlogSEO()` fallback images, `trips/index.js`, any page using imported static assets as OG image. WP/CDN image URLs (`https://smartenplus-wp-s3...`) are already absolute — no change needed. Fixed in `f8d9907` + `61134c9`.

## Related
- [[architecture]]
- [[payment-integration]]
- [[hydration-infinite-refresh-fix-2026-05-20]]
- [[isr-429-cold-start-fix-2026-05-23]]
- [[og-image-ssr-fix-2026-05-23]]
