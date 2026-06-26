# Next.js Dev Stale Module Cache

## Summary
`npm run dev` caches compiled modules in `.next/`. After editing a module (especially one feeding SSR JSON-LD / `getStaticProps` output), a **running** dev server can serve the **stale compiled** version on the next request — making a just-applied fix look "not fixed". Clear `.next/` (or restart) before verifying SSR/SEO changes.

## Problem
Twice in one session (SEO r7 + r8 verification), a JSON-LD edit was confirmed in the source file + eslint-clean, but `curl localhost:3000/...` still showed the **old** output:
- r7: dropped the Yoast `@graph` append in `BlogPostSchemaGenerator.js`; first dev curl still showed the `Article` node pointing at `blog.smartenplus.co.th`.
- r8: synthetic-review removal looked absent on the first curl.

Both resolved only after `rm -rf .next` + fresh `npm run dev`.

## Why
Next dev compiles modules on first request and reuses the compiled artifact. Fast-refresh usually recompiles on edit, but for modules reached through `getStaticProps`/SSR data paths (or when a prior dev session left `.next/` populated), the stale artifact can win. `fallback: 'blocking'` + ISR-style caching compounds it.

## Fix / workflow
Before verifying any SSR/SEO/JSON-LD change locally:
```bash
rm -rf .next && npm run dev
```
Then curl. Do NOT trust a curl from a dev server that was started before the edit, even after HMR — confirm with a clean `.next`.

## Detection
If source clearly has the fix but `curl` shows old output → stale `.next`. Don't re-debug the code; clear the cache first.

## Related
- [[seo-aeo-geo-live-audit-2026-06-22/r6-external-reconciliation-2026-06-25]] (r7/r8 verification false-positives)
- [[isr-client-rtk-stats-seo-pattern]] — related SSR-vs-client data caveat
