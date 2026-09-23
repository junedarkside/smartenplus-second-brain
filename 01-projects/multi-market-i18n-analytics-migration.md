# SmartEnPlus — Multi-Market i18n / Analytics Migration

## Summary
Plan to extend the existing GA4/GTM/Meta Pixel/GSC setup for a Thai market (`lookchang.com`) and a future Korean market — NOT a rebuild. Path-based `/th` on the existing domain first; domain mapping (`lookchang.com` → `/th`) layered on later as a thin rewrite. Triggered by an external consultant report; this doc replaces that report's assumptions with ground truth from a full codebase audit plus 3 independent opus-level reviews.

## Status
**NOT STARTED — planning only.** Two independently-fixable bugs found during the audit (R2 hreflang, R3 currency) have since been fixed and merged to `develop` (see Fixed below) — those are done, not part of the deferred migration work. The migration itself (site/language context, `/th` routing, Thai product data, analytics extension, LookChang domain, Korean market) has not started. Revisit when dev bandwidth allows or a Thai/Korean launch date firms up. Other in-flight work (seat-check feature, per `master-state.md` Section 1) takes precedence unless redirected.

## Fixed (2026-09-23, merged to develop)
- **R2 — hreflang self-reference**: homepage declared `hrefLang="th"` pointing at its own English-only URL, conflicting with `openGraph.locale: 'en_US'` on the same page. Fixed to `hrefLang="en"` at `components/FrontPage/Seo.js:34`. Matches the `en`/`x-default` self-reference pattern already used in `tripDetailSEOUtils.js` and the structured-data hooks. Commit `b27b20a0`, branch `fix/seo-hreflang-th-alternate`.
- **R3 — currency hardcoding + missing fallback**: `purchase` (`useOmisePayment.js:150`) had no fallback and could emit `undefined` currency to GA4 for the revenue event; `add_to_cart` (`BookButton.js:209`) and `begin_checkout` (`checkout/index.js:524`) hardcoded `"THB"` regardless of viewer-selected currency. All three now use `currentRate?.currency || 'THB'`, matching the existing correct pattern in `CartButton.js:75`. Commit `996803eb`, branch `fix/analytics-currency-hardcode`. See `[[analytics-currency-dataLayer-hardcode]]` for full detail.

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

## Named risk: unversioned GTM container
The marketing tag layer (Meta Pixel + any future market-segmented tags) lives entirely in a GTM container this repo cannot version, diff, or CI-check. `[[gtm-custom-html-ignores-consent-mode]]` is direct proof of the cost: a consent leak was invisible to code review, caught only by production network trace, and the documented GTM per-tag consent-settings escape hatch doesn't even render on this container (cause unknown). Any phase depending on GTM-side configuration must be verified by a **dated network-trace artifact** recorded in the vault (cold no-consent load tags / post-consent tags / consent-mode default state) — never assumed correct from a code read. Standing risk, not a one-time gate.

## Phased plan
Only 5 phases survive audit scrutiny with real starting points in this codebase. Do not blanket-adopt the original report's 12-phase structure as pre-validated — 4 of its load-bearing assumptions about this codebase were wrong.

- **Phase 0 — currency + hreflang bug fixes.** DONE (see Fixed above).
- **Phase 1 — Analytics audit.** DONE. This doc's findings section is the artifact.
- **Phase 2 — Site/Language Context.** Starts from nothing (`siteContext` doesn't exist) — new build. Must declare `NEXT_PUBLIC_DOMAIN` (via `helpers/constants.js:32`) as its single domain source in writing and must not add a 5th source; full canonical-domain consolidation is a Phase 2.5 follow-on, not a precondition (the 30+ file spread makes full consolidation-first inversion of risk order). Note `next-sitemap.config.js:1` is build-time and can never read a runtime resolver — any "single source" claim must carve this out.
- **Phase 3 — `/th` routing.** Builds on the inert `middleware.js` stub; must compose with, not replace, the NextAuth export. Side note for whenever reached: this phase will itself shift `page_view` volume via `routeChangeComplete` once locale-prefixed URLs exist — expected reporting noise, not a regression.
- **Phase 4 — Thai Django products.** Cross-repo (`smartenplus-backend`), not audited this session — needs its own audit pass when reached.
- **Phases 5-12 (report's original)** — Analytics Extension, Thai Ecommerce, LookChang Domain, GA4 Cross-Domain, GSC, Production Monitoring, `/th`→domain Migration, Final SEO Verification. Recorded as an explicitly **unvalidated block**: not assessed against this codebase, no Korean domain exists, no business commitment on timing. Re-audit each individually when actually reached. R1 (GA4 dual-path) blocks Phase 5 specifically; R4/R6 (GTM blind spot) applies as a standing check to every phase in this block that touches GTM config.
- Production safety rules from the original report (§27) kept — they match this project's own don't-break-production doctrine.

## Open questions
- Korean domain: still TBD. Nothing Korean-specific should be built until a real domain/timeline exists.
- Confirm whether the dual/triple GA4 tagging is intentional (deliberate redundancy) or accidental drift — a product/analytics-owner call, not resolvable from code alone.

## Loose ends (tracked in `master-state.md`)
- Delete genuinely-dead `components/GoogleAnalytics/GoogleAnalytics.js`.
- Reconcile the dual/triple GA4 page-view sources before Phase 5.
- `pages/checkout/index.js` is 1290 lines (red band, >500) — pre-existing debt, unrelated to the currency fix, needs its own split-evaluation session.
- `checkout/index.js:524` fires `begin_checkout` via raw `window.dataLayer?.push` instead of the `isGTMEnabled()` + `sendGTMEvent` pattern used elsewhere — fires in dev too. Not fixed alongside the currency change (would shift *when* the event fires — a behaviour change).
- `view_item_list` (`helpers/gtmUtils.js:36-51`) has no `currency` and no `price`/`value` field at all — different defect class than R3, needs its own fix threading prices into `formatGtmItem`.
- `NEXT_PUBLIC_SITE_URL` single-call-site fork risk in `components/trips/TripSummary.js:90`.

## Related
[[checkout-flow]] · [[architecture]] · [[gtm-custom-html-ignores-consent-mode]] · [[currency-context-price-rendering-rule]] · [[analytics-currency-dataLayer-hardcode]] · [[seo-canonical-getsiteurl-pattern]] · [[canonicalization-audit-checklist]]
