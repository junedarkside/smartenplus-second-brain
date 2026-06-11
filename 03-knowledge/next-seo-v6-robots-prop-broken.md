# next-seo v6: robots prop silent no-op

## Summary
`<NextSeo robots={{...}} />` does NOT work in next-seo v6. The prop is ignored.

## Details
**What breaks:** Code like `<NextSeo robots={{ index: false, follow: false }} />` silently fails — no error, no effect. Page remains indexable even when intent is `noindex`.

**Why:** next-seo v6 dropped `robots` prop. Correct API: `<NextSeo noindex={true} nofollow={true} />`.

**Detection:** Grep `robots={` in pages/components. If found → broken on every use.

**Found in smartenplus-frontend (now fixed):**
- `pages/checkout/index.js:883-889`
- `pages/orders/index.js:194-197`
- `pages/bookings/index.js:592-595`

## Fix
Replace `robots={{ index: false, follow: false }}` with `noindex={true} nofollow={true}`.

## SSR note
**False constraint:** earlier audit thought ProtectedComponent null-SSR blocked noindex. NOT true. `<NextSeo noindex />` sits OUTSIDE ProtectedComponent tree → renders on SSR → meta tag emits. No blocker. Pages that had NO NextSeo at all (orders/[orderid].js, account/profile.js) just needed NextSeo added.

## Related
[[seo-wave2-audit-2026-05-23]] (auth pages deferred then overturned) · [[seo-sitemap-whole-site-audit-2026-06-11]] (P0-4 finding)
