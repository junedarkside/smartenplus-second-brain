# Sitemap Generators Fail All-Or-Nothing

## Summary
One throwing sitemap generator inside `Promise.all` turns the whole `/server-sitemap.xml` into HTTP 500, and nothing alerts. It stayed broken ~24 days (2026-09-15 → 2026-10-09).

## Context
`pages/server-sitemap.xml/index.js` awaits 9 generators with `Promise.all`. `/sitemap.xml` (static index) keeps listing the dynamic sitemap, so Google just sees an error for every dynamic URL. Found only because a GSC report prompted a live `curl`.

## Problem
- Refactor `a918f290` left `route.updated_at || currentDateForNewRoutes` — variable never declared. Routes API sends **no `updated_at`**, so the fallback ran for every route → ReferenceError → 500.
- Second trap behind it: `new Date(undefined).toISOString()` throws RangeError, but an inner `try/catch` swallows it and **silently skips every route**. Fixing only the first bug would have produced a 200 sitemap with zero routes.
- Code assumed an API field existed; the real payload never had it. Mock-only tests would not catch it.

## Details
- Fix (FE `59e2bc27`): emit `<lastmod>` only when the API supplies a date; never fake it.
- Test with the **real prod payload shape** (curl the API once, keep keys), not an idealised mock.
- Check for stray identifiers: `eslint --env es2021,node --rule '{"no-undef":"error"}' lib/sitemap pages/server-sitemap.xml`.
- After any sitemap change: `curl -s -o /dev/null -w "%{http_code}" https://www.smartenplus.co.th/server-sitemap.xml` and count `<url>`.

## Decision
Minimal fix shipped. Fail-soft (`Promise.allSettled` + per-section counts) deferred as `SITEMAP-FAILSOFT` — scope creep for the bug fix.

## Related
[[sitemap-filter-by-inventory-or-recency]] · [[never-notfound-in-catch-block]] · [[tiered-empty-page-noindex-strategy]]
