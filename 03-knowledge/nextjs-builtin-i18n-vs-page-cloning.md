---
name: nextjs-builtin-i18n-vs-page-cloning
description: Next.js Pages Router has a built-in i18n config that routes one page file to every configured locale automatically — this codebase instead hand-clones a separate file per language (pages/th/about/index.js), which was already flagged as breaking down at language 3. Confirmed against official docs 2026-09-25. Initially deferred by specialist review (real costs: asPath breakage, permanent 2x ISR cost), then explicitly overturned by the project owner same day to avoid the cloning ceiling compounding — migration approved, not yet built.
type: knowledge-atom
date: 2026-09-25
parent: multi-market-i18n-analytics-migration
---

# Next.js Built-In i18n vs. This Codebase's Page-Cloning Pattern

## Summary
Next.js Pages Router ships a built-in `i18n` config (`next.config.js`) that automatically serves one page file at every configured locale path (`pages/about.js` → both `/about` and `/th/about`, zero extra files). This codebase instead manually clones a whole page file per language (`pages/about/index.js` + `pages/th/about/index.js`) — a self-built version of what the framework already does, without the framework's guarantees.

## Why It Matters
This is the direct cause of an already-logged scaling concern: the SWE+WordPress 4-expert audit (session #431, see [[multi-market-i18n-analytics-migration]]) independently found the one-page-per-language pattern "correct through language 2, becomes a real violation at language 3." Built-in i18n routing removes that ceiling for the routing layer specifically — it doesn't solve content translation (WordPress/Django still own that either way), but it removes the *file-cloning* tax entirely for pages that only need translated content, not a different layout.

## Detail
Confirmed via official docs (`nextjs.org/docs/pages/guides/internationalization`) 2026-09-25:
- `next.config.js`: `i18n: { locales: ['en', 'th'], defaultLocale: 'en' }` — sub-path routing gives every page in `pages/` a locale-prefixed route automatically; default locale has no prefix.
- `useRouter()` exposes `locale`/`locales`/`defaultLocale`; `getStaticProps`/`getServerSideProps`/`getStaticPaths` all receive `locale` in their context — this is a drop-in replacement for the path-string-checking `resolveLanguage()` in `helpers/siteContext.js`.
- Next.js auto-sets the `<html lang>` attribute from the detected locale — would resolve the already-logged `_document.js` soft-nav staleness bug (see loose ends in `master-state.md`) as a side effect, since it's framework-owned rather than this app's own server-only `getInitialProps` logic.
- `hreflang` is **not** automatic — docs explicitly say *"Next.js doesn't know about variants of a page so it's up to you to add the `hreflang` meta tags"* — the already-logged missing-hreflang gap on `/about`↔`/th/about` would still need manual work either way.

Three-tier customization model once on built-in i18n (not all-or-nothing):
1. **Most pages**: zero extra code — same component, different `locale`-scoped fetch.
2. **Some pages**: one file, small in-file branch for the specific section that genuinely differs (exactly the pattern just used to fix `ContactUs.js` — see [[sitecontext-language-branch-pattern]]).
3. **Rare pages**: a real second file, only when the *structure* differs, not just the text — the exception, not the default.

## Constraints / Gotchas
- **Does not work with `output: 'export'`** (static export) — docs state Internationalized Routing "does not integrate with `output: 'export'` as it does not leverage the Next.js routing layer." Confirmed 2026-09-25 this repo uses `output: 'standalone'`, not `'export'` — not a blocker here.
- **`asPath` strips the locale prefix — a hard breakage, not a gradual migration.** Confirmed 2026-09-25 by direct Next.js specialist review: once `i18n` is enabled, `useRouter().asPath` on `/th/about` returns `/about` (prefix stripped). `components/contexts/SiteContext.js` derives `language` from `asPath` — the moment `i18n` is turned on, every Thai page silently misdetects as English until `SiteContext.js` and `pages/_document.js` are rewritten to use `router.locale`/`context.locale` instead. This must happen in the **same commit** as the config change — there is no safe intermediate state where the config is on but the consumers haven't been cut over yet.
- **Build-time cost is a PERMANENT 2× multiplier, not a one-time migration cost, and has no per-page opt-out.** Confirmed 2026-09-25 via direct repo audit: this repo has 21 non-dynamic `getStaticProps` pages (homepage, `/about`, `/activities`, `/trips`, `/locations`, `/destinations`, `/operators`, blog index pages, etc.). Enabling `i18n` doubles every one of them — 2 builds, 2 ISR cache entries, 2 revalidation timers each — forever, including the ~19 pages that will never have Thai content. `revalidate: 60` pages double origin-fetch load against WordPress/Django permanently. There is no way to scope `i18n` to only the 2 pages that actually need it (the whole app is unprefixed-English-or-locale-prefixed, globally).
- **2026-09-25 DECISION, then OVERTURNED same day.** Specialist review initially deferred this (given only 2 pages need Thai content today, paying the permanent cost was judged not worth it) — see [[adr-th-i18n-implementation-approach]] for the full reasoning. Hours later, the project owner explicitly overturned the deferral: accepted both costs above knowingly, specifically to avoid the hand-cloned `pages/th/*` pattern's own known ceiling ("breaks at language 3," from an earlier 4-expert audit) compounding as more languages are eventually added. **Current status: migration approved, not yet built.** The specialist findings above are not disputed as wrong — they were weighed against a different cost (tech debt compounding across future languages) and the project owner chose to pay this cost now instead.
- Scope if/when built: every `pages/th/*` file needs consolidating back into its English counterpart, `resolveLanguage()`/`SiteProvider`/`withLangParam` call sites reworked to `router.locale` — real work, not a config flip, and per the `asPath` finding above, the `SiteContext.js` + config-enable piece lands in one atomic commit, not incrementally. `_document.js` and `withLangParam` are separable sub-branches per the SWE specialist's split-test analysis (see ADR).

## Related
- [[multi-market-i18n-analytics-migration]] — parent project; Phase 3's "correct through language 2" finding this atom explains the fix for
- [[nextjs-page-router-no-fallback-routing]] — the routing gap (`/th` 404s) this same built-in system would also close
- [[sitecontext-language-branch-pattern]] — the in-file branching pattern (tier 2 above) already in use for `ContactUs.js`
