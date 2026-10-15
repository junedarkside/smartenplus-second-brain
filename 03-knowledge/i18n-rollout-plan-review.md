---
name: i18n-rollout-plan-review
description: 3-agent review (FE rules, BE+AD, architecture/risk) of the i18n rollout plan, 2026-10-15 — what was wrong in the first draft and what changed.
type: knowledge-atom
date: 2026-10-15
parent: i18n-rollout-plan
---

# i18n Rollout Plan — Review (2026-10-15)

## Summary
First plan draft built things that already exist and missed hard dependencies. Three sonnet read-only reviewers checked it against CLAUDE.md rules and real code. Plan rewritten: [[i18n-rollout-plan]]; recipe: [[i18n-standard-structure]].

## FE rules review
- Verified: `hooks/useT.js`, `withLangParamIfNotDefault` (`helpers/siteContext.js:68`), `config/languages.json`; "done" page list accurate.
- Wrong: catalog is `strings/` directory, not `strings.js`; `lang` param already wired in 5 pages (airport-transfer, trips, trips/detail, activities/detail) → UI strings only; `activities/detail` + `trips/detail` missing from plan.
- "Shared SEO helper" not real: `Seo.js:10` defaults `en_US`; only `useHomeSeoData` builds alternates → extract a hook, grep callers first.
- Size gates: `checkout/index.js` 1295 and `PaymentComponent.js` 867 (red), `profile.js` 463 and `operators/[slug].js` 419 (orange) → extract before adding `t()`. Added R1 refactor milestone + M7 payment checklist.
- Process gaps added: branch from `develop`, `npm run build` + test gate, EN parity snapshot, `callbackUrl` on `/th` auth redirects, `revalidate.js` caller grep.
- Limit: reviewer could not read `CODING_STANDARDS.md` / `CODE_PATTERNS.md`.

## BE + AD review
- Plan said "no translation UI in AD" and "extract TranslationBase" — both wrong: base exists (`stations/translation_models.py:23`), AD review grid + BE review viewset exist. D-1 and the generic API cut.
- Field names corrected: `is_reviewed` (not `status`), `source='bot'` (not `ai`), `source_hash` Station-only; no stale state yet.
- `HistoricalRecords` not used on translation models; permission class is `IsAdminOrIsStaff`, not `Account.has_perm`.
- Bot safety already exists (flag accounts, forced drafts, 409). Do not invent a credential type.
- Cache helpers: `flush_translation_caches` / `deferred_cache_flush`. `LocationTranslation` flushes on every write (perf note for bot batches).
- Keep optimistic-concurrency approve (id + `updated_at`) — mandatory.
- Generic API/UI feasible only via `parent_field` / `text_fields`; per-entity field sets differ (`station.desciption` typo in model).
- `ContractTranslation` is a plain model; migrating it needs row-count check first.

## Architecture / risk review (ranked)
1. Go-live gate was wrong: needs per-section content readiness, not "all milestones". No milestone owned SEO unblock; `public/robots.txt` + `next-sitemap.config.js` are hand-edited with no owner.
2. `pages/api/revalidate.js:26` never revalidates `/th/*` → staff approval would not reach ISR pages. Hard dependency → P1.
3. New abstractions (TranslationBase, generic API, MCP) not backed by any ADR — cut.
4. Bot safety invariants must be server-enforced and tested (no approve, no overwrite of approved row, new draft instead); prompt-injection: source/translated text is untrusted data; sanitize HTML in AD grid; length cap + field allowlist; idempotency + rate limits.
5. "`ko` = config only" is false until proven: `next.config.js` locales are build-time, hardcoded `th` in robots/`og:locale`/`wpSlug`/resolver → L3 fake-locale dry run.
6. Checkout/account sit under the payment boundary; emails (M8) independent of FE gate.

## Added after review (user)
- Multi-language track L0–L5; WP content track W0–W5 (WP = slug-suffix `-th`, no plugin); `/about` corrected to functionally done.

## Decision log
- Cut: generic API, base extraction, MCP, new bot credential, Django-admin UI.
- Kept: AI bot external, drafts only, staff approve in AD.

## Related
[[i18n-rollout-plan]] · [[i18n-standard-structure]] · [[i18n-catalog-with-staff-overrides-pattern]] · [[adr-th-i18n-implementation-approach]]
