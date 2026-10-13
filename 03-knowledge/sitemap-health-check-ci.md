# Sitemap Health Check (CI)

## Summary
`scripts/sitemap-check.js` (FE repo) fetches `server-sitemap.xml` + `sitemap-0.xml`, samples URLs per first path segment, and fails on anything that is not 200 (redirects count as failure), has a placeholder/`null`/missing `<title>`, or is `noindex`. Built for REQ-009 (SEO-REQ-VALIDATION) after 41 dead `/ref/<slug>` URLs sat in the sitemap.

## Policy
Only URLs that return 200 and are indexable belong in the sitemap. 404/410/3xx and noindex pages are excluded.

## Design choices
- **Sample, not full:** 25 per first path segment (`PER_GROUP`), ~240 URLs of ~4,510. Every section (`/ref`, `/trips`, `/th`, `/blog`...) is covered; a lone bad URL can still slip through. Raise `PER_GROUP` for a bigger sweep.
- **Separate workflow** (`.github/workflows/sitemap-check.yml`: after deploy, daily 03:00 UTC, manual) so a failing check never blocks or rolls back a deploy. `deploy.yml` is untouched.
- **GET, not HEAD:** the title check needs the body. `redirect: 'manual'` so 3xx is visible.
- No dependencies (Node 22 global `fetch`).

## Gotchas
- Jest `testMatch` only covers `__tests__/`, `components/`, `pages/`, `hooks/`, `helpers/`. A test under `scripts/` is silently "No tests found"; put it in root `__tests__/`.
- Sitemap sizes (2026-10-13): server 4,494 + sitemap-0 80, 60 overlap. GSC "Discovered pages" lags (showed 1,865 from an Oct 11 read).
- Workflow YAML was never run in Actions at merge time; check the first run after develop -> main.

## First run failed: cold-cache blip (2026-10-13, #489)
- 7 `/airport-transfer/<slug>` 404 right after deploy; all 200 minutes later. Not data: sitemap (`lib/sitemap/airport-transfer.js`) and page (`[slug].js`) both read the `Station` table.
- Cause (likely, unproven): deploy clears the ISR cache, `paths: []` + `fallback:'blocking'` (kept so build stays fast, pre-render was 8 min), check fires 241 cold renders, `/stationsinfo/` (heavy `get_contracts`) times out, `[slug].js:185-192` returns `notFound` for ANY error, cached 60 s.
- Fix: `recheckFailures` re-checks failures once after `RETRY_DELAY_MS` (default 60000, env override). Page untouched: re-throw = uncached 500 on never-generated paths; soft error props = indexable empty 200.
- If it still flakes: prewarm step after deploy, or drop the `workflow_run` trigger and keep the daily cron.

## Related
[[soft-404-api-returns-200-empty-payload]] · [[noindex-flag-decoupled-from-title-flag]] · [[seo-dev-requirements-validation-2026-10-11/overview]]
