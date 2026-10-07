# TH BreadcrumbList Missing /th/ Locale Prefix

## Summary
`router.asPath` in Next.js i18n routing never includes the locale prefix — TH BreadcrumbList `item` URLs resolve to EN paths.

## Problem
`useRouteSeo.js:24` builds `domainURL` from `router.asPath`. In Next.js Pages Router with i18n, `router.asPath` is always the path without locale prefix (e.g. `/trips/hatyai/koh-lipe` even when viewing `/th/trips/hatyai/koh-lipe`). Result: TH BreadcrumbList position 4 `item` URL = `http://localhost:3000/trips/hatyai/koh-lipe` — the EN canonical, not the TH canonical.

This also affects `WebPage` schema `url`/`@id` for TH.

## Fix
```js
// useRouteSeo.js:24 — prepend locale when non-default
const cleanPath = router.asPath.split('?')[0].split('#')[0];
const pathWithLocale = locale !== 'en' ? `/${locale}${cleanPath}` : cleanPath;
const domainURL = useMemo(() => `${aboutURL}${pathWithLocale}`, [aboutURL, pathWithLocale]);
```

`locale` is available from `useRouter()` — it IS the active locale, unlike `asPath`.

## Detection
```bash
# Curl TH page, grep BreadcrumbList item URLs — will show EN path
curl -s https://www.smartenplus.com/th/trips/hatyai/koh-lipe | grep -o '"item":"[^"]*"'
```

## Context
Found 2026-10-07 SEO audit. Discovered via structured-data check of `/th/trips/hatyai/koh-lipe`.

## Related
[[trip-route-page-seo-aeo-geo-audit]] · [[seo-canonical-getsiteurl-pattern]]
