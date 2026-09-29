---
name: nextjs-i18n-locale-detection-default-redirect
description: Next.js built-in i18n defaults localeDetection to true, silently 307-redirecting "/" to the browser's preferred locale. Found + fixed 2026-09-29.
type: knowledge-atom
date: 2026-09-29
parent: multi-market-i18n-analytics-migration
---

# Next.js i18n `localeDetection` Default Redirects `/`

## Summary
Adding `i18n: { locales, defaultLocale }` to `next.config.js` (Pages Router) turns on `localeDetection` **by default**. Any visitor whose `Accept-Language` (or `NEXT_LOCALE` cookie) prefers a non-default locale gets a `307` from `/` to `/<locale>`.

## Why It Matters
On SmartEnPlus, every Thai-language browser opening the homepage was sent to `/th`, where most body content was still English. Nothing in the config mentions detection, so it's easy to ship unnoticed. Googlebot sends no `Accept-Language`, so SEO checks don't catch it — only real Thai browsers see it.

## Detect
```bash
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' -H 'Accept-Language: th' http://localhost:3000/
# 307 http://localhost:3000/th  → detection is on
```

## Fix
```js
i18n: { locales: ['en', 'th'], defaultLocale: 'en', localeDetection: false }
```
Locale then comes only from the URL (`/th/*`). Re-check before adopting `i18n.domains` (lookchang.com), where detection interacts with domain routing.

## Related
- [[nextjs-builtin-i18n-vs-page-cloning]]
- [[multi-market-i18n-analytics-migration]]
