# NextSeo After an Early Return Never Reaches SSR HTML

## Summary

A page that returns a skeleton or error view BEFORE rendering `<NextSeo>` ships no robots/canonical meta in the server HTML. The `DefaultSeo` from `_app.js` wins, so a page marked `noindex` in code is served `index,follow` to crawlers.

## Symptom

```
curl -s localhost:3055/rate-review | grep -o '<meta name="robots"[^>]*>'
-> <meta name="robots" content="index,follow"/>   (code had noindex: true)
```

## Root Cause

Client-rendered pages start in a loading state on the server (`useSession` status `'loading'`, `useState(true)` for fetches). Early returns for loading/error/auth-gate come before `<NextSeo>`, so SSR output has no page-level SEO. Found on `pages/rate-review/index.js` (noindex never reached SSR) and `[reviewSlug].js` (M6a2, #517).

## Fix

Render `<NextSeo {...seo} />` in every branch (loading, error, gate, success). Hooks already run above the early returns. Guard with a jest test that renders each branch and asserts the `noindex`/`nofollow` props, and always verify with `curl` on the built app.

## Related

[[persistgate-ssr-suppresses-head-component]] [[noindex-flag-decoupled-from-title-flag]] [[nextseo-titletemplate-double-brand]]
