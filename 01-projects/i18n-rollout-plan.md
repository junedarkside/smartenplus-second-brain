---
name: i18n-rollout-plan
description: SmartEnPlus i18n rollout plan (2026-10-15) — page + DB content + WordPress + multi-language milestones, each with browser and vault done-checks. Thai first, n languages later.
type: project
date: 2026-10-15
parent: multi-market-i18n-analytics-migration
---

# i18n Rollout Plan (Thai first → n languages)

## Summary
Finish Thai across UI pages, DB content, and WordPress content using one language-agnostic recipe ([[i18n-standard-structure]]), then add languages by runbook. Reviewed by 3 agents ([[i18n-rollout-plan-review]]). Visual board: local dashboard (scratchpad HTML, regenerate from this table). `/th` stays robots-blocked until per-section content readiness (S1).

## Status snapshot (scan 2026-10-15)
- Done (`useT`): homepage `homepagev2.js`, `/trips`, `/locations`, `/destinations` + `[slug]`, site chrome (nav/footer/drawer/chat).
- `/about`: **functionally done** — Thai body = WP page `about-th` (`pages/about/index.js:197`); local `COPY` table only holds SEO/loading/error chrome. Debt = structure only (`I18N-ABOUT-TABLE`, milestone L1/W1).
- NOT done: `/activities` (+detail), `/airport-transfer` (+slug), `/operators` (+slug), `/locations/[slug]`, `/trips/[...slug]` + `trips/detail`, account/bookings/orders/guest-order/my-trip, privacy/terms/404/help/blog/forum/rate-review, checkout, offline strings, BE emails.
- Vault `I18N-DISCOVERY-PAGES` was stale: `/destinations` already uses `useT`. `lang` param already wired (`withLangParamIfNotDefault`) in `airport-transfer`, `trips/[...slug]`, `trips/detail`, `activities/detail` → those need UI strings only.

## Per-milestone done checklist (all)
- Branch from `develop` (`feat/i18n-<slice>`), never `main`; document current behaviour (props, callers, side effects) first.
- `npm run build` + `npm test`; `wc -l` (extract first if >300); no TODO/console.log.
- Browser: `/th/<page>` Thai, `lang="th"`, `og:locale th_TH`, `view-source` hreflang/canonical, console clean, API calls carry `lang`; `/<page>` English identical; unapproved/missing → English.
- Vault: `master-state.md` entry + commit hash, `log.md`, tick `I18N-DISCOVERY-PAGES`.

## Milestones
| # | Milestone | Browser / vault check |
|---|---|---|
| L0 | Registry v2 (`languages.json` + dateLocale, calendar, timeFormat, wpSlugSuffix, dir, enabled); `getLanguage()`; BE mirror from settings | unit tests; th unchanged |
| L1 | Remove hardcoded `th` (7 spots in standard-structure note) | `/th/*` identical; hreflang view-source |
| L2 | robots + sitemap generated from registry, per-language ready state | robots output; fake `xx` |
| P0 | Vault sync (destinations done, about done, add missing pages) | vault diff |
| P1 | `pages/api/revalidate.js:26` revalidates `/th/*`; BE sender sends locale (hard dep for approve→`/th`) | approve in AD → `/th` updates; ISR hit/miss |
| P2 | Shared SEO hook; owner for `public/robots.txt` + `next-sitemap.config.js` | view-source 3 pages |
| P3 | Staff perms grant (`pages_info.add/change_sitetext`); `ContractTranslation` row count; `source_hash` on Location/Route | counts in vault |
| W0 | WP inventory: existing `-th` pages; content-team authoring checklist (privacy-th, terms-th, help-th…) | vault list |
| W1 | `helpers/wordpress/langQuery.js` `wpSlugFor`; migrate `/about` (parity) | `/th/about` identical |
| W2 | `/privacy`, `/terms` Thai (content team authors WP pages) | `/th/privacy`, `/th/terms`; missing → EN + noindex |
| W3 | Guide posts by tag (`GET_ALL_POSTS_BY_TAG`) on destinations/locations/airport-transfer slugs: Thai tag `<tag>-th`, fallback English | `/th/destinations/<slug>` |
| W4 | Homepage WP data (`GET_HOMEPAGE_WORDPRESS_DATA`) + trips `POST_BY_SLUG` | `/th`, `/th/trips/<route>` |
| W5 | `/help` + FAQs; `/blog` (Thai blog or declare EN-only: canonical EN, no hreflang) | decision logged |
| M1 | `/activities` + detail | `/th/activities` |
| M2 | `/airport-transfer` + slug | `/th/airport-transfer/<slug>` |
| M3 | `/operators` + slug (419 lines → extract first) | `/th/operators/<slug>` |
| M4 | `/locations/[slug]`, `/trips/[...slug]`, `trips/detail` | `/th/trips/<slug>` + hreflang |
| D1 | Station/Location approve→flush→`/th` loop in AD + FE (Release B flow) | AD approve → `/th/locations` |
| D2 | Route overview/FAQ: BE exists → wire FE + AD entity config | `/th/airport-transfer/<slug>` |
| D3 | Contract/Operator text (after P3 row count; migration + signal perf check) | `/th/trips/<slug>` after approve |
| S1 | Per-SECTION SEO unblock by content readiness; noindex stays on English-body `/th` | robots, sitemap, GSC |
| M5 | account / profile / bookings / orders / guest-order / my-trip (profile 463 lines extract first; `/th` auth redirects keep `callbackUrl`) | login flow under `/th` |
| M6 | `/404`, `/forum`, `/rate-review`, `/ref` | each `/th` |
| R1 | Split `checkout/index.js` (1295) + `PaymentComponent.js` (867), parity-verified, sonnet floor | guest + auth flow unchanged |
| M7 | Checkout strings — payment checklist below | full flow under `/th` |
| M8 | Offline strings + BE emails (independent) | DevTools offline; sample email |
| L3 | Fake `xx` locale dry run: build, `/xx/trips`, `--language xx` import, bot POST `xx` | zero-hardcode list |
| L4 | `06-systems/add-a-language-runbook.md` (registry → catalog file → BE settings+migration → names import → AD review → handbook → flag → SEO) | follow runbook only on `xx` |
| D4 | AFTER go-live: `06-systems/i18n-ai-translation-handbook.md` for the EXTERNAL AI bot (existing bot accounts, drafts only, never approve) | 5 external drafts → AD queue as `bot`, not live until approved |
| L5 | Language #2 (needs real domain/timeline from user) via runbook | per runbook |

Order: L0–L2 + P0–P3 early → W/M1–M4 + D1–D3 → S1 → M5/M6 → R1→M7, M8 parallel → L3/L4 → go-live → D4 → L5.

## Payment checklist (M7)
Never branch on translated text; keep 409 mapping (`payment_pending`, `amount_locked`, `Order already paid`); poll `successful||paid`; `resetCart` on order pages only; guest `?email=`; `isPaymentLocked` cleared only by `onUnlockPayment()`; `cancelState.success` guards; countdown from backend `expires_at`; `useOmisePayment.js` absent from diff. Language never in the money payload.

## Cut (not doing)
Generic polymorphic `/translations/<entity>/` API; abstract base extraction (exists); new bot credential type; MCP server (until a real bot owner); Django-admin review UI.

## Rollback
Feature flag `lang_th` (exists) = kill switch; un-approve in AD reverts to English.

## Open questions
- Language #2 + domain/timeline (user).
- `HistoricalRecords` on translation models, or `reviewed_by/at` enough?
- Blog: Thai blog or EN-only?

## Related
[[i18n-standard-structure]] · [[i18n-rollout-plan-review]] · [[multi-market-i18n-analytics-migration]] · [[release-b-thai-names-runbook]] · [[adr-th-i18n-implementation-approach]]

## Progress tracker (update ONE row per session when a milestone passes its done-checklist)
| Milestone | Status | Commit / note |
|---|---|---|
| P0 vault sync | ✅ | 2026-10-15 |
| **L0 registry v2** | ✅ 2026-10-15 | FE `386993c0` → develop `13548eec` (pushed, not on main). Shipped `dateLocale`, `calendar`, `timeFormat` + `getLanguage(code)` (`getOgLocale` wraps it; `getBrand`/`BRANDS`/`LANGUAGE_OPTIONS` untouched). **Deviation from row:** `dir` → L2, `wpSlugSuffix` → W1, `enabled` → deferred until precedence vs runtime `lang_<code>` flag (`hooks/useEnabledLanguages.js:12`) is decided (rule: no field without a consumer). No BE mirror code (check manually: FE codes ⊂ BE `settings.LANGUAGES`). Verified: jest 43 pass / 1 fail (pre-existing, below), eslint clean, Chrome `/` `/th` `/th/about` og:locale + lang + Buddhist year unchanged, TH→EN switch OK. Reviewed by sonnet (no issues). |
| **Pre-existing red on develop (not L0):** | ⚠️ | `languageRegistry.test.js` "excludes every non-default locale from sitemap and robots" — `next-sitemap.config.js` `exclude` has no `/th`, `/th/*` (th now indexable? test stale, or config regressed — decide in L2/P2). 3 `useOmisePayment` tests also fail on develop. |
| **Add to L1 scope** | ⬜ | 4 missed hardcoded-th spots: `helpers/i18n/formatDisplayDate.js:7-9,31`, `components/trips/RouteNotice.js:6`, `components/autocompletesearch/utils/searchHistory.js:132`, `components/calendar/AdapterDateFnsBuddhist.js:5` (duplicate 543 offset). |
| **L1 registry-driven (class A)** | ✅ 2026-10-15 | FE branch `feat/i18n-l1-registry-driven` → develop `698c63b8` (pushed, not on main). New `helpers/i18n/calendarYear.js` (offset by registry `calendar`: gregory 0 / buddhist 543) + `dateNames.js` (Thai names per `dateLocale`, fixed tables, no Intl). `formatDisplayDate`, `AdapterDateFnsBuddhist` (duplicate 543 gone), `CalendarDatePickerv2` (adapter/locale from registry), `RouteSchedule` (`timeFormat`) no longer test `'th'`. Tests: parity oracle kept, fake `xx`/`yy` registry test, guard `noHardcodedTh.test.js`. Verified: jest 226 fail = baseline 226, 0 new; build ok; lint 0 errors; Chrome `/`, `/th`, `/th/about` meta + Buddhist calendar identical, console clean. Not tested by hand: TH→EN soft switch, trip search. **Deferred (decided):** class B content fields (`text_th`, `translated_*`, `RouteNotice.js:6`, `FilterTripsPage`, `routeFAQBuilder`, `buildStations`, `destinations`, `useRouteSeo`, offline hooks) → content-field milestone D1-D3 (needs BE alignment); class C hardcoded Thai copy → string-catalog milestones; `searchHistory.js:132` (`formatSearchTime` shows Thai month to English users — changing = behaviour change, needs user OK, separate ticket); `seoConfig.js` hreflang/canonical pair logic → P2/W1. Observed, not caused by L1: `/th/about` emits no hreflang tags (P2/W1). |

## How to start each new session (one milestone per session)
1. Say: "i18n next milestone" → read this note + [[i18n-standard-structure]] + `master-state.md` `I18N-DISCOVERY-PAGES`.
2. Take the first ⬜ milestone in the Order line (start: **L0 registry v2**, branch `feat/i18n-registry-v2` from `develop`). One milestone only.
3. Do it per the done-checklist (build + test + browser check + vault). Update the tracker above, `master-state.md`, `log.md`.
4. Visual board: `01-projects/i18n-rollout-dashboard.html` (open in browser; tick boxes are per-browser only, tracker table here is the source of truth).
5. Payment/checkout work (R1, M7): model floor sonnet, read payment gotchas first.
