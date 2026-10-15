---
name: i18n-standard-structure
description: SmartEnPlus i18n standard structure (2026-10-15) — one recipe every page and DB entity follows so language #2+ is config + content, not code. Thai is the reference implementation.
type: knowledge-atom
date: 2026-10-15
parent: i18n-rollout-plan
---

# i18n Standard Structure

## Summary
Every page and every DB entity follows the SAME shape. Thai = reference language; adding `ko`/`zh`/`ja` must be registry config + content, never new code paths. EXTEND what exists (catalog, `useT`, translation base class, AD review grid) — do not rebuild.

## Existing building blocks (verified in code 2026-10-15)
- FE catalog `helpers/i18n/strings/{index,en,th}.js` + `hooks/useT.js` ([[i18n-catalog-with-staff-overrides-pattern]]).
- FE `helpers/siteContext.js:68` `withLangParamIfNotDefault`; registry `config/languages.json` → `next.config.js` locales.
- BE `stations/translation_models.py:23` base class (Location/Station/RouteByLocationInfo/RouteFAQ translations): `is_reviewed`, `reviewed_by/at`, `source` (`admin|bot`), `source_hash` (Station only).
- BE review API `stations/review_views.py:57` `StationTranslationReviewViewSet` (list/approve/reject/revert/mark-current/summary; `IsAdminOrIsStaff`; optimistic-concurrency approve by id+`updated_at`; cap 500).
- AD review UI `pages/routemanagement/station-translations/index.js`, `components/station/TranslationReviewGrid.js`.
- Bot accounts = flag accounts (`is_station_info_agent`, `is_route_overview_agent`, `is_route_faq_translation_agent`); viewsets force `is_reviewed=False, source='bot'`, post/patch only, 409 on approved row.
- Cache: `flush_translation_caches()` + `deferred_cache_flush()` (`stations/translation_signals.py:57,70`).

## FE page recipe (identical for every page)
1. UI strings → per-namespace catalog file under `helpers/i18n/strings/`, read via `useT()`. No local `isThai` ternaries, no per-file COPY tables.
2. Data: SSR/getStaticProps → `withLangParamIfNotDefault(url, locale)`; client/RTK → always send `lang`.
3. SEO: ONE shared hook (extract from `useHomeSeoData` alternates + `getOgLocale`). canonical = self, hreflang = all enabled + x-default. `Seo.js:10` defaults `en_US` — grep callers before touching.
4. WP content: `wpSlugFor(slug, lang)` helper (see Language-agnostic rules). Missing Thai → English fallback + `noindex`.
5. Fallback chain: staff override → catalog → English → key (existing `useT`). Never blank.
6. House rules: relative imports, no useEffect chains, functions ≤30 lines, file >300 lines → extract first, never branch on translated text.

## BE entity recipe
1. Child translation table extends the existing base; reuse `is_reviewed/reviewed_by/source/source_hash`. Add `source_hash` to Location/Route (stale = hash mismatch → serializer falls back to English).
2. Serializer resolves language `?lang` → `Accept-Language` → cookie; returns approved translation else English; additive `translated_*` fields, same response shape.
3. Language list from `settings.LANGUAGES` — never `DESCRIPTION_LANGS=('en','th')`-style tuples.
4. Cache keys per language; flush through the shared helpers above.
5. Slugs/URLs stay English always (`slugify(location_name)`; `STATION-SLUG-REGEN-ON-RENAME`).
6. Permissions `IsAdminOrIsStaff` (NOT `Account.has_perm`). Audit = `reviewed_by/at`; `HistoricalRecords` is new work, decide separately.
7. Adding a language changes `choices=settings.LANGUAGES` → no-op Django migration.

## Human-in-the-loop
Staff CRUD + approve in **admin-dashboard (AD)**, not Django admin. Extend the existing station-translations review page to more entities via config (`parent_field`, `text_fields`) only AFTER a 2nd entity proves it. Keep optimistic-concurrency approve. Escape/sanitize HTML in the grid.

External AI bot = just another producer of drafts via the existing bot accounts: `source=bot`, `is_reviewed=False`, 409 on approved row, cannot approve. We ship a handbook (and maybe an MCP later), no translator. Treat source text as data, not instructions.

## Language-agnostic rules (n languages, Thai first)
1. Never `=== 'th'`. Registry lookup `getLanguage(code)` → `{ogLocale, siteName, dateLocale, calendar, timeFormat, wpSlugSuffix, dir, enabled}`.
2. en↔th pair logic → N-way (hreflang all enabled + x-default; `og:locale:alternate` = the rest).
3. `wpSlugFor(slug, lang)` = `slug` for default language, `${slug}-${suffix}` otherwise (suffix from registry). WP stays slug-suffix convention (`about-th`), no multilingual plugin (decided by user 2026-10-15).
4. Per-language flag (`lang_<code>`, exists for th) + robots/sitemap generated from registry, not hand-edited.
5. `dir` field even if unused; check font fallback for CJK/Hangul.
6. SEO unblock is per section by content-readiness, not code completion.

## Hardcoded `th` found in code (to remove, milestone L1)
FE: `components/SEO/seoConfig.js:10,24,53-55,88`; `pages/about/index.js:41,197`; `components/calendar/CalendarDatePickerv2.js:39,113`; `components/trips/RouteSchedule.js:28`; `components/trips/FilterTripsPage.js:331,355`; `public/robots.txt` + `next-sitemap.config.js` hand-listed.
BE: `products/serializers.py:26,172,178`; `stations/admin_translation_import.py:28`.

### L1 scope decision (2026-10-15)
The list above under-counts (~25 more sites). Classify every `th` site before touching it:
- **A — behaviour keyed on registry data** (calendar year offset, date locale, time format, adapter choice): replace with `getLanguage(code)` fields. Done in L1.
- **B — content-field names** (`text_th`, `translated_*`, `*_description_th`, `nameTh`): API shape, needs BE alignment → content-field milestone D1-D3. Includes `RouteNotice`, `FilterTripsPage`, `routeFAQBuilder`, `buildStations`, `destinations`, `useRouteSeo`.
- **C — hardcoded Thai copy** (`useRouteSeo` "ไป", offline hooks/components): string-catalog milestones; log as issue, not "fixed".
- **Hreflang/canonical/og pair logic** (`seoConfig.js`): P2/W1.
- **`searchHistory.js:132`**: shows a Thai month to English users today; changing it is a behaviour change, needs explicit OK.
Rule: registry gets a field only when a consumer needs it. Date names stay fixed tables (`helpers/i18n/dateNames.js`), never Intl (SSR/hydration determinism). Guard: `helpers/__tests__/noHardcodedTh.test.js`.

## Consequences
- New page = recipe + catalog namespace; no design debate.
- Deviations must be written HERE, not in a PR description.
- `ko` readiness is proven by the fake-locale dry run (L3), not asserted.

## Related
[[i18n-rollout-plan]] · [[i18n-rollout-plan-review]] · [[i18n-catalog-with-staff-overrides-pattern]] · [[nextjs-builtin-i18n-vs-page-cloning]] · [[adr-th-i18n-implementation-approach]] · [[multi-market-i18n-analytics-migration]]
