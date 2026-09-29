---
name: i18n-catalog-with-staff-overrides-pattern
description: SmartEnPlus UI-text i18n pattern (2026-09-30) — frontend catalog as default + fallback, backend SiteText rows as per-language staff overrides, pure useT lookup, SSR-seeded where SEO matters.
type: knowledge-atom
date: 2026-09-30
parent: multi-market-i18n-analytics-migration
---

# i18n: Code Catalog + Staff Overrides

## Summary
Static UI text lives in one frontend catalog (`helpers/i18n/strings.js`, same keys per language, parity test). Staff can override any key for any language in Django admin (`SiteText(key, language, value)`), no deploy. `t(key)` = staff override → catalog (current language) → English catalog → key.

## Ownership rule
- Catalog = default UI text (code, reviewed, tested).
- `SiteText` = staff overrides of catalog keys.
- Translation child tables = structured content (nav, footer, products).

## Design choices that mattered
- **Pure hook:** `useT` reads a context (`SiteTextContext`, default `{}`, no API imports); a separate `SiteTextProvider` inside the Redux Provider does the fetch. Keeps `t()` free of network side effects and existing tests working without a store.
- **No seed:** seeding the catalog's values into the DB creates a second copy that silently shadows later code edits. Empty table = catalog everywhere.
- **`currentData` not `data`:** RTK `data` keeps the previous argument's result, so a language switch would briefly show the other language's text.
- **SSR seed where it matters:** homepage `getStaticProps` fetches overrides for `context.locale` and passes them as the provider's initial value — server and first client render agree (no hydration mismatch), crawlers see staff text.
- **Backend:** route above any `<slug:slug>` catch-all; cache check `is not None` (an empty `{}` is a valid hit); signal clears `site_text_v1_*` (all languages); `HistoricalRecords` audit trail.

## Limits
A brand-new language still needs one frontend deploy (`next.config.js` `locales` is build-time). Homepage HTML reflects edits after ISR regeneration (≤1h) unless on-demand revalidation is added.

## Related
- [[sitecontext-language-branch-pattern]] (superseded per-component COPY approach)
- [[nextjs-hydration-rules]]
