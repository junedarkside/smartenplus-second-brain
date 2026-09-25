# SmartEnPlus — Multi-Market i18n / Analytics Migration

## Summary
Plan to extend the existing GA4/GTM/Meta Pixel/GSC setup for a Thai market (`lookchang.com`) and a future Korean market — NOT a rebuild. Path-based `/th` on the existing domain first; domain mapping (`lookchang.com` → `/th`) layered on later as a thin rewrite. Triggered by an external consultant report; this doc replaces that report's assumptions with ground truth from a full codebase audit plus multiple rounds of independent opus-level review.

## Status
**NOT STARTED — planning only.** Four independently-fixable bugs found during the audit (R2 hreflang, R3 currency, R1 GA4 consent-bypass, R4 begin_checkout value-conversion) have since been fixed and merged to `develop` (see Fixed below) — those are done, not part of the deferred migration work. The migration itself (site/language context, `/th` routing, Thai product data, analytics extension, LookChang domain, Korean market) has not started. Revisit when dev bandwidth allows or a Thai/Korean launch date firms up. Other in-flight work (seat-check feature, per `master-state.md` Section 1) takes precedence unless redirected.

## Fixed (2026-09-23, merged to develop)
- **R2 — hreflang self-reference, fixed twice.** Homepage declared `hrefLang="th"` pointing at its own English-only URL, conflicting with `openGraph.locale: 'en_US'` on the same page. First fix (`b27b20a0`, branch `fix/seo-hreflang-th-alternate`) swapped the value to `hrefLang="en"` at `components/FrontPage/Seo.js:34` — correct in source, but the alternate tags were placed inside `next-seo`'s `additionalLinkTags` prop, which keys its rendered React elements by `href+rel`, not `hrefLang`. Both alternate entries shared the same `href`/`rel`, collided on the same key, and React silently dropped one — live browser verification (`view-source`) caught only `x-default` rendering, `en` missing. Root-caused by reading `next-seo`'s source directly (`node_modules/next-seo/lib/next-seo.js`); the 3 files originally cited as "precedent" for the first fix actually all use the correct, dedicated `languageAlternates` prop instead. Corrected fix (`61500409`, branch `fix/seo-hreflang-languagealternates-prop`) moved both entries there, matching those precedents exactly. Verified live post-fix via curl against a fresh dev build — both tags present.
- **R3 — currency hardcoding + missing fallback**: `purchase` (`useOmisePayment.js:150`) had no fallback and could emit `undefined` currency to GA4 for the revenue event; `add_to_cart` (`BookButton.js:209`) and `begin_checkout` (`checkout/index.js:524`) hardcoded `"THB"` regardless of viewer-selected currency. All three now use `currentRate?.currency || 'THB'`, matching the existing correct pattern in `CartButton.js:75`. Commit `996803eb`, branch `fix/analytics-currency-hardcode`. See `[[analytics-currency-dataLayer-hardcode]]` for full detail.
- **R1 — GA4 consent-bypass, found and fixed.** The direct-gtag `<GoogleAnalytics>` path (`layout.js:252`) had zero read of the cookie consent banner's stored choice, firing `gtag('config', ...)` for every non-dev visitor regardless of Accept/Decline — the same bug class as the already-documented Meta Pixel/GTM consent leak (`[[gtm-custom-html-ignores-consent-mode]]`), via a second, independent path this repo actually controls. Fixed via a shared `helpers/cookieConsent.js` (exports `CONSENT_KEY`, `hasAnalyticsConsent()`) plus a `CONSENT_CHANGED_EVENT` window event so `Layout` (which has no shared state with the sibling `CookieConsentBanner`) picks up an Accept click same-session, no reload needed. Commit `f750ebc6`, branch `fix/ga4-respect-cookie-consent`. Live-verified in browser both with and without the site's `NEXT_PUBLIC_DEVELOPMENT` dev-mode override: Decline stays blocked in all cases, Accept activates GA4 immediately.
- **R4 — `begin_checkout` value-conversion, found in a post-merge review of R3, fixed after a wrong fix was caught mid-review.** R3 fixed `begin_checkout`'s `currency` field but left `value`/`price` as raw, unconverted THB numbers — so post-R3 the event said e.g. `{currency:"USD", value: 3500}` where 3500 was still baht, a self-contradicting payload *worse* than the pre-R3 state (wrong label but at least a consistent number). A BD-lens review flagged this as a hard blocker on promoting to `main` — inflated checkout-value signals for non-THB traffic are exactly the shape that misleads funnel/abandonment analysis, and GA4 history can't be corrected retroactively. The first proposed fix (`data.total_price / rate`) was itself wrong — `total_price` doesn't exist anywhere in the cart API response (confirmed via backend-wide grep) — applying it would have turned `undefined` into `NaN`. Corrected fix uses the real field names (`data.grand_total`, `item.sub_total`, confirmed against both the backend serializers and a same-file precedent at `checkout/index.js:1192`). Commit `9055a9bd`, branch `fix/analytics-begin-checkout-value-conversion`. **Live-verified with a real booking**: added a real THB 1,000 trip to cart, reached `/checkout`, captured the actual dataLayer event — `value: 1000`/`price: 1000`, finite numbers, matching the Cart Summary sidebar exactly.

## Audit findings (ground truth vs. the external report)

**Exists, reusable:**
- **GA4 runs on TWO live paths, not one.** GTM (`pages/_app.js:105-110`) AND a direct-gtag path via `@next/third-parties/google`, rendered at `components/layout/layout.js:252`, gated by `enableGA4` state that resolves `true` for nearly every visitor (`layout.js:162,177-186`). A third source — a manual `dataLayer.push({event:'page_view'})` on every `routeChangeComplete` (`pages/_app.js:36-42`) — means GA4 page-views have up to three concurrent sources today. Possible double-counting, not confirmed but plausible. Must be reconciled before Phase 5 (analytics extension) — see Phase gating below.
- The only genuinely dead analytics file is `components/GoogleAnalytics/GoogleAnalytics.js` (a third, separate, unimported direct-gtag component) — do not confuse with the live path above.
- Consent Mode v2 correctly sequenced in code (`pages/_app.js:93-104` beforeInteractive → GTM loads → `CookieConsentBanner.js:7-23` updates + pushes `consent_granted`). **Caveat**: `[[gtm-custom-html-ignores-consent-mode]]` has production-measured evidence this exact setup previously leaked (Meta Pixel ignored consent entirely). Code sequencing is right; whether the deployed GTM container still has the trigger fix is unverifiable from this repo — network trace only.
- GA4 ecommerce taxonomy already shipped: `view_item_list`, `view_item`, `add_to_cart`, `view_cart`, `begin_checkout`, `purchase` (+ custom `recommendation_purchase`).
- Sitemap (`next-sitemap`), robots.txt, GSC verification meta tag (`pages/_app.js:80-83`), per-page-type canonical URL utilities — all exist, single-domain only.

**Confirmed absent (true greenfield):**
- Meta Pixel: zero `fbq()` calls anywhere in repo. Entirely GTM-container-configured (external, unversioned). See `[[gtm-custom-html-ignores-consent-mode]]`.
- `NEXT_PUBLIC_META_PIXEL_ID`: present only in one developer's untracked `.env.local`, absent from all committed env samples — not a shipped config, low-stakes local cleanup.
- i18n/locale routing: zero. No `next-i18next`, no `i18n` block in `next.config.js`, no `/th` path, no `router.locale` usage anywhere.
- Site/market/language context: zero. No `siteContext`, no resolver.
- `middleware.js` is an inert stub: `export { default } from "next-auth/middleware"`, `matcher: []`. Clean slate for a future domain/locale resolver — but any new logic must compose with, not replace, the NextAuth export.
- Canonical domain string spread across 30+ files reading `NEXT_PUBLIC_DOMAIN` directly, plus a build-time-only hardcoded literal in `next-sitemap.config.js:1`, plus `getSiteUrl()` consumers, plus a single-call-site `NEXT_PUBLIC_SITE_URL` fork risk in `components/trips/TripSummary.js:90`. Must be reckoned with before a domain resolver can be trusted — see Phase gating.

## Corrected architecture (vs. the original report)
1. GA4 is **not** cleanly GTM-only — a future `site`/`market`/`language` resolver must reach both the GTM dataLayer path and the direct-gtag `layout.js:252` path, or one will silently miss market dimensions. Reconciling to a single tagging path is worth doing as part of Phase 5, not just layering context on top of the ambiguity.
2. Meta Pixel has no in-repo surface — "extend existing Meta Pixel" is not a code task here, it's a GTM-container-configuration task (external, unversioned — see Named risk below) plus wiring the same `site`/`market`/`language` dataLayer keys so GTM can segment by them.
3. The original report never mentioned the currency hardcoding/missing-fallback bugs (fixed, see above) or the GTM dual-path issue — both found only by auditing this codebase directly, not from the report's generic best-practice assumptions.
4. **The report's `site`/`market`/`language` 3-axis model does not match this system — corrected to 1 axis, `language`.** Found during Phase 2 design (below): for every actually-planned market, all 3 columns move in lockstep (SmartEnPlus/international/en, LookChang/Thailand/th, future-Korean-brand/Korea/ko). The Django backend's real committed data model has no `market`/`site`/`tenant` field anywhere — only `language`. Building a 3-axis resolver would invent a parallel taxonomy the backend doesn't share.

## HEADLINE FINDING — the backend already has a live i18n system; "new build" was the wrong framing

Found during Phase 2 design work (not this doc's original audit): `smartenplus-backend` already ships a **complete, production-live 12-language i18n system**, shipped 2026-01-25 (`docs/archive/phase-summaries/phase4-multilanguage.md`, 37/37 tests passing) —
- `middleware/language.py` — a `LanguageMiddleware`, registered live in `MIDDLEWARE`. Resolution priority: `?lang=th` query param → `Accept-Language` header → `smartenplus_lang` cookie → `'en'` default.
- `settings.py:307-325` — `LANGUAGE_CODE='en'`, 12 `LANGUAGES` including `th` and `ko`.
- `operators/models.py:1154` — `ContractTranslation` model, `unique(contract, language)`, 7 translatable fields, cascade delete.
- `products/serializers.py:810-880`, `operators/serializers.py:654` — `translated_name`/`translated_description`/etc. `SerializerMethodField`s reading `request.LANGUAGE_CODE`, falling back to the untranslated field.

**The frontend is already consuming this, by accident, undocumented, in production right now**: `components/order/OrderDetail.js:196` reads `item.contract?.translated_name || item.contract?.name`. A user with a Thai-locale browser already gets Thai contract names today — non-deterministically, because the frontend never sends a language signal and the backend's `Accept-Language` fallback picks it up straight from the browser.

**Corrected framing** (supersedes the earlier "Phase 2 starts from nothing" line below): *Phase 2 builds the frontend half of a language contract whose backend half already exists and is live. It is greenfield in code, constrained in design — the backend's ISO-639-1 vocabulary is the given, not something Phase 2 invents.*

**Consequence for Phase 4** ("Thai Django products"): cheaper than this doc originally implied — infrastructure exists, only content population (`ContractTranslation` rows) + field consumption remain. **Real hazard**: the moment Phase 2 starts sending a language signal, the backend immediately serves any existing translated rows. If rows exist prematurely, partially-translated content could appear in production with no deploy involved. **Verify the current `ContractTranslation` row count before Phase 2 ships anything that sends `Accept-Language`.**

## Named risk: unversioned GTM container
The marketing tag layer (Meta Pixel + any future market-segmented tags) lives entirely in a GTM container this repo cannot version, diff, or CI-check. `[[gtm-custom-html-ignores-consent-mode]]` is direct proof of the cost: a consent leak was invisible to code review, caught only by production network trace, and the documented GTM per-tag consent-settings escape hatch doesn't even render on this container (cause unknown). Any phase depending on GTM-side configuration must be verified by a **dated network-trace artifact** recorded in the vault (cold no-consent load tags / post-consent tags / consent-mode default state) — never assumed correct from a code read. Standing risk, not a one-time gate.

## Phased plan
Only 5 phases survive audit scrutiny with real starting points in this codebase. Do not blanket-adopt the original report's 12-phase structure as pre-validated — 4 of its load-bearing assumptions about this codebase were wrong.

- **Phase 0 — currency + hreflang + consent-gate + begin_checkout bug fixes.** DONE (see Fixed above — R2, R3, R1, R4, all merged to `develop`, not yet promoted to `main`).
- **Phase 1 — Analytics audit.** DONE. This doc's findings section is the artifact.
- **Phase 2 — Site/Language Context.** DESIGNED, not yet implemented — full spec in `## Phase 2 design` below (3 rounds of opus review: SWE/Next.js/Architecture design, then a 4th gap-analysis pass against CLAUDE.md). `siteContext` doesn't exist in the frontend, but see the Headline Finding above — this is not greenfield design, it's building the frontend half of an already-live backend contract. Must declare `NEXT_PUBLIC_DOMAIN` (via `helpers/constants.js:32`) as its single domain source in writing and must not add a 5th source; full canonical-domain consolidation is a Phase 2.5 follow-on, not a precondition (the 30+ file spread makes full consolidation-first inversion of risk order). Note `next-sitemap.config.js:1` is build-time and can never read a runtime resolver — any "single source" claim must carve this out.
- **Phase 3 — `/th` routing.** Builds on the inert `middleware.js` stub; must compose with, not replace, the NextAuth export. Side note for whenever reached: this phase will itself shift `page_view` volume via `routeChangeComplete` once locale-prefixed URLs exist — expected reporting noise, not a regression.
- **Phase 4 — Thai Django products.** Cross-repo (`smartenplus-backend`), not audited this session — needs its own audit pass when reached.
- **Phases 5-12 (report's original)** — Analytics Extension, Thai Ecommerce, LookChang Domain, GA4 Cross-Domain, GSC, Production Monitoring, `/th`→domain Migration, Final SEO Verification. Recorded as an explicitly **unvalidated block**: not assessed against this codebase, no Korean domain exists, no business commitment on timing. Re-audit each individually when actually reached. R1 (GA4 dual-path) blocks Phase 5 specifically; R4/R6 (GTM blind spot) applies as a standing check to every phase in this block that touches GTM config.
  - **OWNERSHIP DECIDED (2026-09-25):** user (project owner) is accountable for the LookChang Domain sub-item specifically. **Explicit gate**: work on `lookchang.com` domain mapping does not start until `smartenplus.co.th/th` (Phase 3) is working properly — no separate date set beyond that gate. This resolves the "no business commitment on timing" gap for this one sub-item; the rest of the Phases 5-12 block remains unowned/unscheduled as before. Full 3-lens (BD/SWE/Architecture) review of the domain-mapping approach → [[adr-lookchang-domain-mapping-approach]]. Before resuming this item: fix the two cheap items (SSR-default landmine + remaining English UI chrome on `/th/about`) as prerequisites, independent of the `/th`-working-properly gate.
  - **PREREQUISITES SHIPPED (2026-09-25):** both cheap items fixed, branch `fix/th-about-ssr-default-and-chrome`, not yet merged to `develop`. (1) `getCurrentLanguage()` now `console.warn`s when called server-side instead of silently defaulting to English — see [[nextjs-builtin-i18n-vs-page-cloning]] for why this gap exists at all. (2) `ContactUs.js` now branches its static strings by language via `useSite()`, zero prop changes to its 4 callers — pattern documented at [[sitecontext-language-branch-pattern]]. 29/29 tests pass, production build succeeds, DOM content verified live.
  - **NEW FINDING (2026-09-25): `/th` itself 404s, only `/th/about` exists.** Surfaced via user testing. Confirmed as expected Next.js Pages Router behavior, not a bug — no file exists at `pages/th/index.js`, and the router has zero fallback from a child route to its parent path. Full mechanism explained in [[nextjs-page-router-no-fallback-routing]]. Root cause of the broader pattern: this codebase hand-clones a page file per language instead of using Next.js's built-in `i18n` routing config, which would make `/th` (and every future `/th/*` page) resolve automatically from the same file as its English counterpart — see [[nextjs-builtin-i18n-vs-page-cloning]] for the full comparison and a 3-tier customization model. Not yet decided whether to migrate; documented as an option, not scheduled.
- Production safety rules from the original report (§27) kept — they match this project's own don't-break-production doctrine.

## Phase 2 design — Site/Language Context (spec, not yet implemented)

Designed via 3 parallel opus reviews (SWE, Next.js, Architecture) against the live codebase, then a 4th gap-analysis pass against CLAUDE.md rules/constraints. No code written — this is the spec for when Phase 2 starts.

### Axis model — 1 axis (`language`), not 3
See Headline Finding above. `language: 'en' | 'th'`, ISO-639-1, matches the backend's already-committed vocabulary. Not a boolean (too lossy against the backend's real vocabulary), not 3 axes (`site`/`market`/`language` — invents a taxonomy the backend doesn't share). Brand identity (siteName/domain/logo) is a *derived lookup table keyed by language*, never an independent input.

### Recommended shape
No Redux (a persisted stale locale could contradict the URL — real bug, not style; `store/index.js:173`'s whitelist mechanism). No `pageProps` threading (~56 of 93 pages have neither `getServerSideProps` nor `getStaticProps` — adding either would regress ISR). No `middleware.js` matcher activation — **critical trap found independently by 2 agents**: `middleware.js` currently re-exports `next-auth/middleware`; activating any matcher for locale detection would simultaneously auth-gate every matched route. Recommendation: delete the dead middleware export, don't build on it.

Pure resolver function + thin synchronous React Context, seeded from router/`pageProps`, never from `useEffect`:
```js
// helpers/siteContext.js — pure, no imports, no async
export const SUPPORTED_LANGUAGES = ['en', 'th']; // 'ko' later = one array element
export const DEFAULT_LANGUAGE = 'en';
export function resolveLanguage({ pathname = '' } = {}) {
  const p = (pathname || '').split('?')[0];
  return (p === '/th' || p.startsWith('/th/')) ? 'th' : DEFAULT_LANGUAGE;
}
```
Context (~20 lines, no `useState`/`useEffect`/fetch) mounted **outermost in `pages/_app.js`, above `<Provider store>`** — matches the shape of `helpers/cookieConsent.js` (this session's newest helper precedent: exported constants, guarded export, safe default, never throws), explicitly does NOT copy `CurrencyContext.js`'s async shape (that machinery exists only because currency is genuinely async — copying it here manufactures the `currency-context-infinite-fetch` bug class in a place it can't otherwise occur).

### Next.js mechanics (corrects a wrong premise in the original external report)
ISR does **not** need converting to SSR — locale-as-path-segment is exactly what `getStaticProps`/ISR already handles (`/trips/a/b` and `/th/trips/a/b` are independent cache entries). The trap is the opposite: a header-based approach would silently do nothing for the 21 ISR pages. Domain mapping (later phase) doesn't need middleware either — `next.config.js` `rewrites()` natively supports per-hostname conditions, confirmed against actual Next.js 14.2.33 source in this repo. The original report's "avoid rewrite loops" concern is a **confirmed non-risk** on this version (verified via source, explicit re-entrancy guard). **Highest-risk unknown to test before the domain-mapping phase**: does nginx forward the original `Host` header to the Next upstream? Every hostname-based rule depends on it; untested; one afternoon on staging de-risks the whole later phase.

### Payment/auth boundary (no prior draft named one — added during gap analysis)
Phase 2 touches `store/api/api-slice.js`, the base query every cart/checkout/seat-availability request flows through. Untouchable: the `publicEndpoints` allowlist and its guard comment (guest-cart AllowAny protection), the `await getSession()` call (don't reorder), `checkSeatAvailability`'s timeout config (unrelated seat-check work). `Accept-Language` must be set unconditionally, outside and before the public-endpoints check. **Language must never reach the money payload** — `hooks/useOmisePayment.js` must not appear in any Phase 2 diff.

**Scope correction from gap analysis**: an earlier draft claimed this covers "every API endpoint at once" — false. The app has 7 RTK Query slices; only 3 (`apiSlice`, `bookingsApi`, `otaApi`) get `Accept-Language` in Phase 2. ~39 `axios` call sites and 4 other RTK slices stay language-unaware — logged as a follow-on, not silently implied as covered.

### Branch plan — 4 branches, not one
1. `feat/site-context-resolver` — pure helper + Context + tests only, zero call sites. Ship first.
2. `feat/site-context-provider-mount` — `_app.js` mount + `_document.js` lang fix. Must be a verified no-op while only `en` resolves.
3. `feat/site-context-accept-language` — the `prepareHeaders` seam. Payment/auth-adjacent (see boundary above). **Gated on confirming the `ContractTranslation` row count first** — do not cut until confirmed.
4. `feat/site-context-brand-table` — brand lookup + SEO canonical *declaration only* (not the 29-file sweep — that's Phase 2.5).

### Scope: explicitly OUT of Phase 2
`/th` routing itself (Phase 3) · consuming `translated_*` fields (Phase 4) · domain mapping/`lookchang.com` (later, needs the nginx test first) · Korean (no domain/timeline) · UI translation-string catalog · language-switcher UI · any `market`/`site` field anywhere (a `market` field on `Contract` would create a real admin-dashboard dependency — market pickers, filters, backfill — that the translation-child-table shape avoids entirely) · GA4 dual-tagging reconciliation · `pages/checkout/index.js` (1293 lines, red band, untestable integration suite — if any branch would touch it, stop and defer to Phase 2.5).

### Model floor
`sonnet`, hard floor, no exceptions on any sub-branch — this touches auth code (`prepareHeaders`) and a new shared-helper signature, both explicitly named in CLAUDE.md's never-below-sonnet list.

## Open questions
- Korean domain: still TBD. Nothing Korean-specific should be built until a real domain/timeline exists.
- Confirm whether the dual/triple GA4 tagging is intentional (deliberate redundancy) or accidental drift — a product/analytics-owner call, not resolvable from code alone.

## Loose ends (tracked in `master-state.md`)
- Delete genuinely-dead `components/GoogleAnalytics/GoogleAnalytics.js`.
- Reconcile the dual/triple GA4 page-view sources before Phase 5.
- `pages/checkout/index.js` is 1293 lines (red band, >500) — pre-existing debt, unrelated to the currency fix, needs its own split-evaluation session.
- `checkout/index.js:523` fires `begin_checkout` via raw `window.dataLayer?.push` instead of the `isGTMEnabled()` + `sendGTMEvent` pattern used elsewhere — fires in dev too. Not fixed alongside the currency change (would shift *when* the event fires — a behaviour change).
- `view_item_list` (`helpers/gtmUtils.js:36-51`) has no `currency` and no `price`/`value` field at all — different defect class than R3, needs its own fix threading prices into `formatGtmItem`.
- `NEXT_PUBLIC_SITE_URL` single-call-site fork risk in `components/trips/TripSummary.js:90`.
- `begin_checkout`'s `item_id` uses the cart-item ID instead of `contract.id` — inconsistent with `add_to_cart`/`view_cart`/`purchase`, breaks item-level GA4 funnel joins. Found during R4's review, not fixed in that branch.
- `begin_checkout`'s `quantity` reads `item.children`, but the backend serializer field is `child` — other call sites in the same file use `item.children || item.child || 0` defensively, this one doesn't, likely under-counting children. Found during R4's review, not fixed in that branch.
- `__tests__/pages/checkout/index.integration.test.js` (734 lines) fails to run entirely on a broken relative-import path, unrelated to any fix this session. Needs a one-line path correction plus a check on whether its assertions still pass once loadable.
- 3 pre-existing failures in `hooks/__tests__/useOmisePayment.test.js`, confirmed unrelated to this session's changes each time the file was touched — needs its own tracking issue.
- **Found during Phase 2 design work** — `store/dayTripSlice.js:34` `selectedLanguage` is dead (zero production callers, only referenced in tests). Do not let Phase 2 build a second, competing language field — either remove this one or wire it to the new resolver.
- **Found during Phase 2 design work** — `pages/_app.js:20,114`: `GlobalPaymentWarning` imported and rendered only as a comment. Dead code, own ticket.
- **Found during Phase 2 design work, cross-repo (`smartenplus-backend`)** — need to verify the current `ContractTranslation` row count before Phase 2's `Accept-Language` branch ships (see Headline Finding above). Name an owner; log in the backend repo too per CLAUDE.md CROSS-REPO.

## Related
[[checkout-flow]] · [[architecture]] · [[gtm-custom-html-ignores-consent-mode]] · [[currency-context-price-rendering-rule]] · [[analytics-currency-dataLayer-hardcode]] · [[seo-canonical-getsiteurl-pattern]] · [[canonicalization-audit-checklist]]
