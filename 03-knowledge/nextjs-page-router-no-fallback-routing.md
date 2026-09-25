---
name: nextjs-page-router-no-fallback-routing
description: Next.js Pages Router is strict file-to-route matching with zero fallback — a child route existing (pages/th/about/index.js) does not make its parent path (/th) resolve to anything. Confirmed against official docs + installed source (v14.2.33) 2026-09-25.
type: knowledge-atom
date: 2026-09-25
parent: multi-market-i18n-analytics-migration
---

# Next.js Pages Router Has No Fallback Routing

## Summary
Route resolution in Next.js Pages Router is a strict file-system lookup — one file maps to exactly one route, with no parent/child inheritance and no fallback to a "closest match." `pages/th/about/index.js` existing creates the route `/th/about` and nothing else; it does not make `/th` resolve to anything.

## Why It Matters
Easy to assume a nested page implies its parent path works too (or falls back to something sensible, like the default-language homepage). It doesn't. This surfaced as a real question this session: `smartenplus.co.th/th` 404s even though `smartenplus.co.th/th/about` works correctly — confirmed as expected behavior, not a bug.

## Detail
Confirmed via two independent sources 2026-09-25:
- Official docs (`nextjs.org/docs/pages/building-your-application/routing/pages-and-layouts`): *"each page is associated with a route based on its file name"* — no fallback/inheritance language anywhere in the routing docs.
- Installed source, this repo's exact version (`node_modules/next@14.2.33/dist/server/lib/router-utils/resolve-routes.js`): route resolution is a file-system match against `getDynamicRoutes()`/static routes; no logic anywhere walks up to a parent path on a miss.

A 404 is decided by the router **before** any application code runs — `_app.js`, `_document.js`, and any language-detection helper (e.g. `resolveLanguage()`) never execute on a 404, because no page component was matched to render them inside.

## Constraints / Gotchas
- This is unrelated to `next.config.js` `redirects()` or a custom `pages/404.js` — either of those *could* add a fallback, but neither exists in this codebase today.
- Also unrelated to Next.js's **built-in i18n routing** (`i18n` config block) — that system generates a route for every configured locale automatically from one file, which would make `/th` resolve for free if it were in use. See [[nextjs-builtin-i18n-vs-page-cloning]] for why this codebase doesn't use it yet.

## Related
- [[multi-market-i18n-analytics-migration]] — parent project this question came up under
- [[nextjs-builtin-i18n-vs-page-cloning]] — the alternative routing model that would make this a non-issue
