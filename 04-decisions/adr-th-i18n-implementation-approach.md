# ADR: /th i18n Implementation Approach — 3-Specialist Review Reverses 2 of 3 Prior Decisions

## Status
superseded (partially) — see **ADDENDUM 2026-09-25 (same day)** below. Decision #1 (built-in i18n deferred) was overturned by the project owner later the same session, with the specialist findings accepted as real costs, not disputed as wrong. Decisions #2-#4 below stand unchanged. Original review remains accurate as a historical record — it was not wrong, its recommendation was knowingly overridden.

## Context
A pre-implementation planning session (grilling one decision at a time) had settled on: migrate `/th` routing to Next.js's built-in `i18n` config, adopt `next-i18next` for nav/footer translation, build a full-parity `/th` homepage (9+ sections), and gate `lookchang.com` work behind `/th` being "fully working." Before writing any code, the user asked for a 3-specialist review against this repo's actual CLAUDE.md and codebase — not just against abstract i18n best practice — specifically because a `console.warn` + `getCurrentLanguage()` fix earlier the same session had already shown the plan's assumptions weren't always accurate on inspection.

## Decision

### 1. REVERSED — built-in Next.js i18n routing migration: deferred, not scheduled
Original plan assumed this was a straightforward, incremental swap (`resolveLanguage()`/`SiteProvider`/`withLangParam` → `router.locale`). Next.js specialist found this false on two counts:
- **Hard breakage, not gradual migration**: enabling `i18n` strips the locale prefix from `useRouter().asPath` — `SiteContext.js` derives `language` from `asPath`, so every Thai page would silently misdetect as English the instant the config flips, until `SiteContext.js`/`_document.js` are rewritten in the *same commit*. No safe intermediate state exists.
- **Permanent, unconditional cost**: `i18n` has no per-page opt-out. It doubles the ISR build surface for all 21 non-dynamic `getStaticProps` pages — including ~19 that will never have Thai content — forever, not just during migration. Origin-fetch load against WordPress/Django on `revalidate: 60` pages doubles permanently.

SWE specialist independently corrected the scope estimate that had made the migration look smaller than it is: "39 SSR/SSG pages" was wrong (real: 3 `resolveLanguage` call sites, 17 `withLangParam` call sites, 8 `getStaticPaths` files) — but confirmed the underlying direction was still sound *in principle*, just not worth the permanent ISR cost for only 2 Thai pages today.

**Decision**: keep the current hand-cloned `pages/th/*` routing pattern. Do not adopt built-in i18n now. Revisit only when Thai page count grows enough to justify the permanent 2× ISR cost — not on a timeline, not "soon," genuinely gated on page count.

### 2. REVERSED — `next-i18next` for nav/footer: dropped in favor of the already-proven `COPY` pattern
Original plan: adopt a full i18n string-catalog library for ~11 hardcoded strings across 6 nav/footer files. SWE specialist called this direct over-engineering against CLAUDE.md's own "simplest solution only, no abstractions just in case" rule — the repo already has a working pattern shipped the same session in `ContactUs.js` (local `COPY = {en, th}` object + `useSite()`, zero new dependency). Next.js specialist independently confirmed the real cost of the alternative: `next-i18next` requires `serverSideTranslations()` added to every page rendering the (global) nav/footer — effectively all pages — which is where a large blast-radius number actually becomes true, just not the routing-migration reason originally assumed.

**Decision**: extend the `ContactUs.js` `COPY` pattern to nav/footer components directly (`components/layout/{main-header,footer,menu,NavDropdown,AccountLayout}.js`). Revisit `next-i18next` only if string count grows past what a handful of `COPY` objects can hold, or real pluralization/interpolation needs appear — neither true today.

### 3. CONFIRMED + WIDENED — backend Location/Route/Review translation gap
Django specialist confirmed the gap (no translation model for `Location`, `Route`, `Review`) and found a scope-widening fact the original discovery missed: **Popular Routes displays `Station.station_name` (departure/arrival), not `Route.route_name`** — translating `Route` alone would not translate what the homepage actually shows. `Station` also has no translation mechanism.

**Decision**: backend phase is `LocationTranslation` + `RouteTranslation` + likely a station-name translation path (not scoped to a single new model yet), sized medium (not small), mirroring the proven `ContractTranslation` pattern (additive-only migrations, existing serializer keys unchanged, low production risk — confirmed via direct read of `operators/models.py`, `products/serializers.py`, `middleware/language.py`). Admin-dashboard staff-entry UI is an explicit separate ticket, not part of this phase (mirrors `ContractTranslation`'s own gap — Django-admin-only today).

**Reviews: will not be translated.** User-generated content — machine translation is a trust problem, not just an engineering one (publishes words under someone's name they didn't write). Show reviews as-authored regardless of locale, zero backend work.

### 4. RESOLVED — indexing vs. lookchang.com sequencing debate
All 3 specialists independently agreed: no technical coupling between un-blocking `/th` from search indexing and starting `lookchang.com` infrastructure (DNS/nginx) — product/timing call only, they can run in parallel. Django specialist added a narrower, more accurate gate than what was assumed: the backend already has the full language contract working end-to-end (`request.LANGUAGE_CODE` → serializer fallback to English), so `/th` pages can ship and even index with zero translation rows — they'll just render English content under Thai URLs, which is a thin-content SEO risk, not a functional break. **The real gate is content-readiness for the specific sections being indexed, not an infrastructure or "`/th` fully working" gate.**

## Consequences
- Revised phased plan written to `~/.claude/plans/check-vault-and-thai-polymorphic-lantern.md` (local plan file, not vault-persisted verbatim — see that file for the 7-phase breakdown).
- [[nextjs-builtin-i18n-vs-page-cloning]] updated with the concrete `asPath`/ISR-doubling findings from this review — the atom previously documented the option abstractly; now documents the specific reason it was deferred.
- No code written yet from either the original plan or this revision — this ADR and the plan file are the record of a review pass, not an implementation.
- Unflagged risk surfaced by SWE specialist, not yet assigned an owner: `next-sitemap.config.js`/`public/robots.txt` are generated + checked in, hardcode `/th` disallow — nobody owns updating these when `/th` un-blocks.
- Pre-existing CLAUDE.md Constraint 7 (NO TECH DEBT) violation surfaced, not yet fixed: `helpers/siteContext.js:45-47` has a "Phase 3 will consolidate this" comment instead of a linked issue.

## ADDENDUM 2026-09-25 — Decision #1 overturned by project owner, same day

While starting implementation of Phase 1 (nav/footer translation, no `i18n` involvement), a real discovery — nav labels come from a live backend API + static fallback, not hardcoded component strings — led to the user asking a bigger question: *"won't this get worse with more languages? We keep having to create more and more pages, isn't that tech debt?"*

That's a correct read of the situation, already on record in this vault independently: the hand-cloned `pages/th/*` pattern (kept per Decision #1 above) was flagged by an earlier 4-expert audit as "correct through language 2, becomes a real violation at language 3." Decision #1 above chose to accept that ceiling now, in exchange for not paying the built-in-i18n migration's permanent 2× ISR cost until a 3rd language is real (no Korean timeline/domain exists).

**The user was explicitly asked to confirm they understood and accepted the specialist-identified costs before overturning**: (1) `SiteContext.js`/`_document.js` must be rewritten in the exact same commit as the `i18n` config change — `asPath` strips the locale prefix the instant the config is live, so there's no safe gradual path; get the cutover wrong and every Thai page silently misdetects as English. (2) The ISR build cost doubles permanently across 21 pages that don't need Thai content, starting immediately, not just during a migration window.

**User's answer**: proceed anyway — worth accepting both costs now specifically to avoid the clone-per-language ceiling compounding as more languages are eventually added, rather than defer the cost to a point where more pages exist and the eventual migration is larger.

**Revised decision**: do the built-in i18n migration now, broken into the sub-branches the SWE specialist already proposed in the original review (not re-litigated, same evidence): `next.config.js` config + `getStaticPaths` verification (must land in the same commit as `SiteContext.js`'s `router.locale` cutover, per the `asPath` finding) → `_document.js` fix (separable, fixes the known soft-nav staleness bug as a side effect) → `withLangParam` re-source (17 call sites, one commit) → fold `pages/th/about/index.js` back into `pages/about/index.js`. Nav/footer translation (Decision #2, unchanged) now builds on `router.locale` from the start instead of the old path-string resolver.

This is a judgment call the specialist review correctly informed but does not override — the review's job was to surface real costs accurately, which it did; whether those costs are worth paying now vs. later is a product decision the project owner is entitled to make differently than the recommendation, with the tradeoff made explicit rather than skipped.

## Related
- [[adr-lookchang-domain-mapping-approach]] — prior ADR on the domain-mapping mechanism specifically (nginx vs. next.config.js rewrites); this ADR is about the `/th` engineering approach, a different but related scope
- [[multi-market-i18n-analytics-migration]] — parent project
- [[nextjs-builtin-i18n-vs-page-cloning]] — updated same day with this ADR's concrete findings, and again with the addendum's overturn
- [[sitecontext-language-branch-pattern]] — the `COPY` pattern being extended to nav/footer per decision #2, now built on `router.locale` per the addendum
