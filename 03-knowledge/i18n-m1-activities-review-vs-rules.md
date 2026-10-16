# i18n M1 Activities — Review vs CLAUDE.md Rules

## Summary
3 read-only agents (code-reviewer, react-specialist, seo-specialist) reviewed Thai i18n M1 (PR-a/b/c, FE develop `d99d89fe`) against FE `CLAUDE.md`, and assessed readiness of next milestone M1d (`DayTripBookingWidget.js`). Date: 2026-10-16. No code changed.

## Context
M1a-c merged to develop, not deployed. Next = M1d booking widget. `docs/development/CODING_STANDARDS.md` and `docs/operations/SEO.md` were permission-denied to agents again, so only `CLAUDE.md` rules were checked (WP-subdomain canonical rules unchecked; looks N/A for activities files).

## Verdict
M1 a-c largely compliant. **M1d NOT ready**: split the widget first. Two real correctness/SEO gaps (FAQ JSON-LD mismatch, missing `/th` sitemap URLs).

## Findings (ranked)

### High
1. **M1d target not ready.** `components/activities/detail/DayTripBookingWidget.js` is 539 lines (red, only red component in scope). `handleAddToCart` ~135 lines, >15 branches. ~40 hardcoded English strings (toasts l.221-343, labels l.383-466, buttons l.501-532). External English sources: `AVAILABILITY_ERROR_MESSAGES` (constants/dayTripConstants), `getCapacityErrorMessage` (helpers/passengerCapacity), `AGE_RANGE_LABELS` (helpers/dateHelper). Adding keys would reach ~600 lines.
2. **FAQPage JSON-LD does not match visible FAQ.** `helpers/seo/dayTripSEOUtils.js:262-282` = price/duration/payment questions; visible FAQ (`ExperienceFAQ.js`, `experienceFAQBuilder.js:26-43`) = bring/age/difficulty/cancellation. On `/th` the schema mixes Thai tourName with English Q/A. Handoff claim "JSON-LD via tEn" is **wrong**: the file has no `tEn` import, only English literals. Fix: build schema from `buildExperienceFAQItems(contract, t)` (match visible text) or drop FAQPage on `/th`. Update `dayTripSEOUtils.test.js`. Note: agent says Google retired FAQ rich results 2026-05-07 (unverified) → value is AEO/consistency.
3. **Sitemap has no `/th` activities URLs.** `lib/sitemap/products.js:18,64` emit unprefixed only. `lib/sitemap/routes.js:9-15,69` already loops indexable languages — copy that, skip untranslated contracts (noindex).

### Medium
4. `DayTripCard.js:71` `formatContractDuration(workingContract)` has no `t` → Thai browse cards show "3 Days". Pass `t`; keep `dayTripSEOUtils.js:267` English.
5. `dayTripSEOUtils.js` (79,81,88,141,207,238-239,265-278): meta description, keywords, breadcrumb "Home"/"Activities", fallbacks, `SERVICE_CATEGORY_LABELS` English. Description English was a decision; breadcrumb names inconsistent with index page (`t('breadcrumb.home')`).
6. Debug `console.log` (DayTripBookingWidget.js:255-263, dev-guarded) + 4 `console.error` (309-312).
7. `DayTripDetailPage.js` 293 lines, body ~230 lines; `formatDateForApi` called 3×; undocumented eslint-disable l.86.
8. `DayTripCard.js` 296 lines, 5 duplicated caption Typography blocks l.191-250 (~40 lines); stray indent l.65.
9. `helpers/i18n/strings/en.js` + `th.js` 712 lines each (red) → split by domain.

### Low
- Unused `IconButton` import `DayTripMobileBookingBar.js:15`.
- `t = tEn` default (getTrustBadges, formatContractDuration, experienceFAQBuilder): caller forgetting `t` silently gets English on /th.
- `[...slug].js:90` `console.log("Pre-building...")`; header comment says `/daytrips/detail/` (route is `/activities/detail/`).
- `dayTripSEOUtils.js:12-13` `const siteUrl` between imports.
- `useActivityDetailLabels.js:11-18` closures not memoized.
- `FilterDayTripsPage.js:21-29` props→state effect w/ eslint-disable (pre-existing); `DayTripList.js:44` debug effect.
- `NextBreadcrumbs.js:80-92` `Crumb` state initialised once from props → possible stale text on locale switch (check /th ↔ EN). Crumb click now client-side nav (was full load).
- Thai brand: `_app.js:92` template "%s | SmartEnPlus" vs registry Thai siteName "LookChang" — confirm intent.
- `priceValidUntil` = now+30d changes every ISR rebuild (valid).
- hreflang uses bare `en`/`th`, not `en-US`/`th-TH` — confirm intent.
- No component tests for browse/detail components (helpers/hooks tested).
- Dead code: `DayTripDetailHeader.js`, `DayTripHero.js` (no importers) → separate cleanup PR.

## M1d plan (recommended order)
1. Extract from widget: label/message builders (success l.285-304, button l.501-532, share `bookCategories`), pure helper for ADULT/CHILD/INFANT lookup (`convertToRatecard`/`calculatePrice`), cart-submit hook/error-toast mapping (l.314-343). No behavior change; EN snapshot/RTL tests per branch (category × tour type × error status) first.
2. Then i18n via `useT`; keys in `helpers/i18n/strings/activityDetail.{en,th}.js`; `tEn` for non-hook helpers; `formatDisplayDate` for dates; consider `AdapterDateFns` Thai locale.
3. Route `AVAILABILITY_ERROR_MESSAGES`, `getCapacityErrorMessage`, `AGE_RANGE_LABELS` through `t`.

**Do not translate / touch:** 429 handler regex on backend text "Expected available in (\d+) seconds"; `error.data?.message?.includes('no longer available')`; validation order/conditions, toast durations, `disabled` logic; don't add `t` to the l.367 date-sync effect deps. Plural: two keys (or `{count}`+plural), EN output byte-identical.

Importers of widget: `PremiumBookingPanel:56`, `DayTripMobileBookingBar:42/182` (dynamic), `DayTripDetailPage:31` (dynamic). Props `{contract, selectedDate, onDateChange, cardSx}`; payload `{user, contract_id, traveling_date, contract_ratecard, adult, child, infant, product_type}` → toast.success → `router.push('/checkout')`.

## Passes
EN/TH key parity (`activityDetail.*` both 119 lines, placeholders match; compared by eye, not script). No `@/` imports, no `server-*` patterns. Helpers/`useT`/`tEn` never throw (warn + key). Helper `t` is last param, positional args unchanged, tests cover EN+TH. No hardcoded English in other browse/detail/shared components. Canonical self-referencing per locale, hreflang en/th/x-default, `og:locale th_TH`, untranslated contract → noindex + English canonical, title brand not doubled, ISR revalidate covers `/th/activities/detail/*`. No TODO/FIXME in scope. Callers of changed helpers compatible.

## Vault correction
Master-state says `robots.txt` has `Disallow: /th`. Agent found no such line in `public/robots.txt` (languages.json `th.indexable: true`). Verify live before trusting; update master-state if stale.

## Not verified
Function length/branch/param counts for components other than DayTripCard, DayTripDetailPage, DayTripBookingWidget. Any test/build run. Live `curl` checks:
`curl -s https://www.smartenplus.co.th/th/activities/detail/<slug> | grep -Ei 'canonical|hreflang|og:locale|robots|FAQPage'`

## Related
[[master-state]]
