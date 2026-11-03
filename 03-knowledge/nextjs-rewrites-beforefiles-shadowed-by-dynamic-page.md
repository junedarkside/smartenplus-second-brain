# Next.js rewrite shadowed by a dynamic page

## Summary
`rewrites()` returning an array is `afterFiles`: a matching `pages/x/[param].js` wins first, so the rewrite never fires. Use `{ beforeFiles, afterFiles }`.

## Context
SmartEnPlus `/ref/<slug>`: `pages/ref/[type].js` served every article slug as a 200 "Reference Type Not Found" (`index,follow`, homepage title). 41 of 42 sitemap URLs affected for months; the 404 flagged in the 2026-06 audit had silently become a soft-200.

## Details (all three needed)
1. Array form = afterFiles. Return `{ beforeFiles: [...], afterFiles: [...] }`; put the shadowed rewrite in `beforeFiles`.
2. `locale: false` on a source under `i18n` stops it matching normal paths (they carry no locale segment in the matcher). Drop it for ALL rewrites, proxies included. Dropping it fixed `/th/ref/<slug>`. (Earlier advice to keep it for `/graphql`-style proxies was wrong: it 404'd the blog search, see below.)
3. The exclusion regex must list every real static type, anchored with `$`: `/ref/:slug((?!a$|b$).+)`. A bare prefix lookahead blocks slugs that merely start with `route` or `location`.
4. Build the exclusion list from the same JSON the page uses (`config/reference-types.json`, 12 types), so adding a type cannot reopen the bug.
5. Redirect the internal target (`/ref/article/:slug` → `/ref/:slug`, permanent) so only one URL is indexable.

## Second casualty: `/graphql` proxy (2026-11-03)
The `/graphql` → WP rewrite kept `locale: false` (commit `719f9ee7`, i18n enable). Prod `POST /graphql` (and `/th/graphql`) returned Next 404 HTML while `POST /api/graphql` returned 200. All client `internalfetcher` calls failed: blog search suggestions, `/blog/search/<q>`, `/blog` + category load-more. Fix (FE develop `23f1323b`): `helpers/internalfetcher.js` → same-origin `/api/graphql` proxy, dead rewrite removed, 3 unit tests. Why the proxy over dropping `locale:false`: testable before deploy, no dependence on rewrite matching under i18n. Cause is consistent with Next docs but was not reproduced locally. Detection: `curl -X POST <prod>/graphql` after any `next.config.js` rewrite or i18n change.

## Debug trap
Regex looked right in isolation; only a request-level debug log in `[type].js` showed which page served it. Test the rewrite with `next dev` + curl on a real slug AND every static type, not by reading the regex.

## Tradeoffs
Two pages stay (type index + article) instead of one merged page: keeps each under the size budget, costs a rewrite.

## Related
[[soft-404-api-returns-200-empty-payload]] · [[never-notfound-in-catch-block]] · [[seo-dev-requirements-validation-2026-10-11/overview]]
