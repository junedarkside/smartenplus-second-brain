# SEO dev-requirements report — validation (2026-10-11)

## Summary
External 13-REQ SEO report (`2026-10-11-dev-requirements-seo-fixes.md`) validated against live prod (curl) + FE code, then reviewed by 2 agents against CLAUDE.md / coding standards / ISR+SEO rules. **STATUS 2026-10-13: 6 REQs (001, 002, 003/009, 004, 005, 007) IMPLEMENTED + merged to FE `develop`, NOT deployed.** See "Implementation status" below. Remaining: 006, 010, 011, 012, 013 (need BE `updated_at` or a decision). 008 dropped.

## Context
Report assumed App Router (`src/`, `notFound()`, `:from(lower)` redirect). FE is **Pages Router at repo root**; sitemap is hand-built in `lib/sitemap/*.js`. Same class of error as [[seo-aeo-geo-live-audit-2026-06-22/r6-external-reconciliation-2026-06-25|r6]] (external audit, wrong root causes). Treat external audits as symptoms, re-derive cause from code.

Full corrected report (addendum + standards review on top of original): [[source-report-validated]] (copy; Desktop original untouched). Browser dashboard: claude.ai/artifact/LAweA3oyZcr7FAKjVMv7o9 (private, v2).

## Implementation status (FE `develop`, 2026-10-13; one branch per fix, `--no-ff` merges, none deployed)
| REQ | Branch | Merge | What shipped |
|---|---|---|---|
| 003/009 | `fix/ref-routing` | `79f52698` | `beforeFiles` rewrite; exclusion regex built from new `config/reference-types.json` (single source for `next.config.js` + `[type].js`); `[type].js` unknown type → `notFound` 300; article catch rethrows (no `notFound`), missing article revalidate 300; `/ref/article/:slug` → `/ref/:slug` 308 |
| 001 | `fix/trips-hub-404` | `dc9239ca` | **Route API returns 200 with `routes:[]`+`contracts:[]` for unknown pairs (not 404).** Empty both → `notFound` 300; real 404 → `notFound`; contracts-only stays 200; 5xx/timeout stays soft |
| 004 | `fix/trips-case-redirect` | `163d30fd` | per-segment `slugify` compare in `getStaticProps` → 308 before API call; new `helpers/i18n/localePrefix.js` shared with `resolveNonRouteSlug`; empty slug skips redirect |
| 005 | `fix/help-category-canonical` | `53ab9c90` | one self `canonical` const for category + post. No `/th` help mirrors exist, so no locale prefix |
| 007 | `fix/hub-hreflang` | `344a4f83` | `seoConfig.js` `en-US/th-TH` → `en/th` (hrefs were already right) |
| 002 | `fix/trip-detail-404` | `90865583` | catch: `error.response?.status === 404` → `notFound` 300; extracted `TripDetailFallbacks.js` (page 517 → 482 lines) |

Checked locally (dev server on prod API) + unit tests + `next build` per PR. Full FE suite NOT green on baseline (39 failing suites on clean `develop`, 226 failed tests after PR1; only new failure = unrelated timing test `extractUniqueValues O(n)`). `FilterTripsPage.test.js` can't load (MUI icon import) on `develop` too.

## Corrections to the first write-up (found during implementation)
- `sectionMap` has **12** types, not 11 (`history` was missed). Wherever this note or the report says 11/7-hijacked: it is 12/8.
- REQ-003 second cause: the rewrite had `locale: false`. Under `i18n` that stops the source matching normal paths, so the rewrite never fired even after moving to `beforeFiles`. Removing it also fixed `/th/ref/<slug>`. See [[nextjs-rewrites-beforefiles-shadowed-by-dynamic-page]].
- REQ-001: the API does not 404 for unknown pairs; the fix keys on empty payload. See [[soft-404-api-returns-200-empty-payload]].

## Verdicts (live 2026-10-11)
| REQ | Verdict | Key fact |
|---|---|---|
| 001 `/trips/a/b` soft-404 | CONFIRMED | `/trips/zzzz/yyyy` 200, robots already `noindex,follow` (status is the bug). `[...slug].js:138` throws on any `!res.ok` → API 404 lands in soft `catch` (:200) → fix must read `res.status` before throw. Overlaps `SITEMAP-FOLLOWUP` (~450 noindex route URLs in sitemap). |
| 002 `/trips/detail/<fake>` | PARTLY | 200 but "Trip Not Available" + `noindex,nofollow` already. Only `catch` branch. File is **517 lines** (red) → extract first. |
| 003 `/ref/<slug>` | **CONFIRMED, worse** | 41 of 42 sitemap `/ref/*` URLs = 200 "Reference Type Not Found", homepage title, `index,follow`. Only `/ref/route` OK. They are real articles. Root cause below. |
| 004 mixed-case dup | CONFIRMED | `/trips/Phuket/Koh-Phi-Phi` 200, byte-identical, self canonical. Fix in `getStaticProps` (308), not `next.config` `:from(lower)` (invalid). |
| 005 help canonical | PARTLY | 9 category pages canonical `/help`; 45 posts already self. `/help/cancel-booking` is 404 not 200. `router.asPath` lacks locale prefix. |
| 006 sitemap lastmod | CONFIRMED | 2,182 of 4,475 entries share one minute. 9 files fake `new Date()`; `routes.js:44` omit-tag is the right pattern. |
| 007 hreflang | CONFIRMED (hubs only) | `seoConfig.js:65` `en-US/th-TH`; home + trip-detail use `en/th`. |
| 008 pagination canonical | **INVALID** | `/trips`, `/blog` have no server pagination. |
| 009 clean `/ref` from sitemap | REFRAMED | Don't delete — real articles; fix routing (003). Add CI check: every sitemap `<loc>` 200 + non-placeholder title. |
| 010 detail cannibalization | CONFIRMED count (1,739) | Business decision; deferred. |
| 011 title/meta | UNVERIFIED | Not re-measured. |
| 012 FAQPage | CONFIRMED | 0 FAQPage on `/trips/phuket/koh-phi-phi`. **Already diagnosed:** [[filter-trips-seo-faq-prop-dropped]] (`FilterTripsPage.js:235` suppresses; `RouteFAQ.js:8` opts out). Not "new components". |
| 013 dateModified | CONFIRMED | `2026-01-26T10:49:41` = WP blog post `modified`; needs BE route `updated_at`; fix in `getStaticProps` (:179) not hook. |

Sitemap actuals: 4,475 `<loc>`; 2,443 hub (incl `/th`); 1,739 detail; 42 `/ref`; 54 `/help`.

## REQ-003 root cause (the main finding)
`next.config.js:114-126` `rewrites()` returns an **array** (= afterFiles). Dynamic page `pages/ref/[type].js` matches first → no `sectionMap[type]` → placeholder 200. Rewrite `/ref/:slug((?!route|pier|location|terminology).*)` → `/ref/article/:slug` never fires. Direct `/ref/article/<slug>` also 404 (live).

Fix needs ALL of:
1. `rewrites()` → `{ beforeFiles:[ref rewrite], afterFiles:[/graphql] }`.
2. **Regex bug A:** prefix lookahead blocks slugs *starting with* `route`/`location`… → anchor with `$`.
3. **Regex bug B:** `sectionMap` has **12** types (route, pier, location, terminology, access, seasonal, safety, administrative, destination, crossborder, infrastructure, history; verified); rewrite excludes 4 → after step 1 the other 8 type pages get hijacked and 404. Build exclusion from `Object.keys(sectionMap)`.
4. `[type].js`: `if(!sectionMap[type]) return {notFound:true, revalidate:300}`; optional-chain `json.data.referenceArticles` in `getStaticPaths` (:310); `noindex` on placeholder.
5. `article/[slug].js`: catch (:364-369) returns `notFound` (violates ISR rule); missing-article `revalidate: 86400` → 300; canonical already self `/ref/${slug}` (:91) — don't add another; redirect `/ref/article/:slug` → `/ref/:slug`.
6. `/th/ref/<slug>`: rewrite has `locale:false`, no `/th` rule — decide.
Do NOT merge the two pages ([type].js 377 + article 370 lines → size budget).

History: r3 (2026-06-22) P0-B flagged "41 `/ref/article/*` in sitemap 404"; sitemap was since changed to `/ref/<slug>` but routing never worked → 404 became soft-200 placeholder. Same 41 pages, still invisible to search.

## Rules for every fix (from reviewers)
- `notFound` from `catch` **only for confirmed 404**; never 5xx/timeout (caches 404 over ISR slot).
- `notFound` `revalidate: 300` not 3600 (`fallback:'blocking'` hides routes created < 1h ago).
- Prod deploy must clear `smartenplus_next_cache` volume or stale 404/redirect persists. Add to acceptance of 001–005.
- `/th/` mirrors need same fix for 001, 004, 005.
- 004: reuse `slugify`; extract locale-prefix logic from `resolveNonRouteSlug.js:19-20` into shared helper; per-segment compare (loop guard); 308; loop-curl acceptance (vault `TRIPS-SINGLE-SEGMENT-LOW`: redirect `revalidate` not confirmed honoured).
- 005: canonical = `getSiteUrl()` + locale prefix ([[seo-canonical-getsiteurl-pattern]], [[th-breadcrumb-locale-prefix-bug]] same `router.asPath` flaw).
- 006: one `lastmodTag(date)` helper in `lib/sitemap/utils.js` (return `''` + `console.warn`, never throw), not 9 hand edits.
- 007: hreflang hrefs = canonical = sitemap mirrors; next-seo dedupes alternates sharing href ([[hreflang-th-tag-self-referencing-bug]]).
- Size: `trips/detail/[...slug].js` 517 (red), `help` 358, `ref/[type].js` 377, `ref/article/[slug].js` 370, `useRouteSeo.js` 256 (yellow — new FAQ builder goes in `routeFAQBuilder.js`).

## Caveat
SEO reviewer was denied `docs/operations/SEO.md` — canonical/`/th` conclusions come from code + vault notes. Re-check against that file before implementing.

## Deploy + verify (user steps, then Claude sweeps prod)
1. Merge FE `develop` → `main`; clear `smartenplus_next_cache` volume (ISR persists otherwise).
2. Sweep: 42 sitemap `/ref/*` → 200, distinct real titles, 0 placeholder; `/ref/nonexistent` 404; `/ref/article/<slug>` 308; `/trips/zzzz/yyyy` + `/trips/detail/<fake>` 404 (EN + `/th`); `/trips/Phuket/Koh-Phi-Phi` 308 lowercase, loop-curl; `/help/booking-process` self canonical; hub hreflang `en`/`th`.
3. GSC: resubmit sitemap (see `SITEMAP-FOLLOWUP`).

## Still open
006 (`lastmodTag` helper, needs BE `updated_at` on locations/stations/operators), 013 (`trips/[...slug].js` `lastModified`, needs route `updated_at`), 012 ([[filter-trips-seo-faq-prop-dropped]]), 010 (business), 011 (re-measure first). REQ-009 CI check (every sitemap `<loc>` 200 + non-placeholder title) NOT built. `docs/operations/SEO.md` still unread (permission-denied to agents); canonical/`/th` rules unchecked against it.

## Recommended order (original)
Week 1: **003**, 001, 002 (extract first), 004, 005, 007. Week 2: 006 (needs BE `updated_at`), 012, 013, 011. Later: 010. Dropped: 008; 009 merged into 003. One branch per fix from `develop` (`fix/ref-routing` first).

## Related
[[seo-aeo-geo-live-audit-2026-06-22/r6-external-reconciliation-2026-06-25|r6 external-audit reconcile]] · [[filter-trips-seo-faq-prop-dropped]] · [[sitemap-filter-by-inventory-or-recency]] · [[seo-canonical-getsiteurl-pattern]] · [[docker-standalone-isr-revalidate-gap]]
