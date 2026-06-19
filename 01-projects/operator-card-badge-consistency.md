# Operator Contract-Card Badge Consistency

> **SHIPPED TO PROD 2026-06-16 (#124).** Implemented (`a3c1d88`, new `ContractTypeBadge` using `COLORS.badge.primary` token) → FE develop `6fff946`, deployed live.

## Summary
2-agent (design + frontend) analysis of the contract-list card badges on `/operators/[slug]` — flagged by user as "AI slop / inconsistent". Root cause: 3 metadata badges per row built by 3 different systems (3 radii, 2 heights, 2 build methods) + a color-semantics collision (JOIN renders success-green next to a status badge). Converged fix: one canonical Chip geometry, neutral indigo for all contract types (icon+label differentiate), new scoped `ContractTypeBadge`. No code shipped yet — spec.

## Problem (confirmed via screenshot + code)
Each card's right-aligned badge cluster (`pages/operators/[slug].js:214-235`) mixes:
1. **Inactive** — inline `<span>` (`:217`): rect, `rounded` (4px), gray.
2. **Service category** ("Day Tours"/"Transportation") — `ServiceCategoryBadge` MUI Chip: rect, 6px, 28px, soft per-category fill + meaningful icon.
3. **Contract type** ("JOIN"/"CHARTER"/"PRIVATE") — inline `<span>` (`:224`): `rounded-full` pill, soft fill from `tourTypeSoft` token, generic `CategoryOutlinedIcon`.

→ 3 radii (4/6/full), 2 heights, MUI-Chip vs raw-span, and **JOIN green (`#10B981` = `COLORS.status.success`) reads as a status** beside the gray Inactive status badge. PRIVATE/CHARTER violet ALSO collides with DAY_TOUR category purple. Type badge shows raw enum `JOIN` + a meaningless grid icon.

## Debate trail
**Design:** unify geometry on the Chip pattern (28px/6px/13px); 2-tier hierarchy via fill (outlined=status, soft=identity); drop per-type colors → one indigo (type isn't ordinal, color falsely implies ranking), differentiate by icon (Groups/Lock/AirportShuttle); drop the generic icon; don't touch the 14-consumer `BadgeChip`.

**Frontend (feasibility + pushback):** verified `tourTypeSoft`+`getTypeColor` are single-consumer (operators card only) → safe to delete. Confirmed PRIVATE/CHARTER violet collides with DAY_TOUR purple too (not just JOIN-green). Confirmed AirportShuttle≠DirectionsBus (latter is the TRANSPORTATION category icon → would collide). Pushed back on infra: keep Inactive an inline span (className tweak, not a new variant prop); build `ContractTypeBadge` as a ~45-line twin of `ServiceCategoryBadge`, NOT a premature `<MetaBadge>` abstraction (only 2 callers). Agreed single-indigo over multi-hue (KISS; revisit only if scan-testing shows need). Caught: render `CONTRACT_TYPE_NAMES` friendly labels, not raw enum.

**Leader verification (corrects one frontend claim):** standalone `COLORS.badge.tourTypePrivate`/`tourTypeCharter` (`designSystem.js:46-47`) ARE consumed by `BadgeChip.js:69-73` + `ServiceCategoryBadge.js:48` — frontend's "optionally drop tourTypeCharter" would break BadgeChip. Only the `tourTypeSoft` nested block (`:49-54`) is operators-only and safe to delete.

## Decision (converged spec)
1. **Geometry**: all 3 badges → 28px height / 6px radius / 13px-500 / 16px icon (the `ServiceCategoryBadge` Chip look, made canonical).
2. **Hierarchy by fill, no new infra**: soft-fill = identity (service category + type); outlined gray = status (Inactive, stays inline span, className tweaked to match geometry).
3. **One indigo for all contract types** (`#EEF2FF` bg / `#4338CA` text / `#C7D2FE` border — unused by any status/category color). Differentiate JOIN/PRIVATE/CHARTER by icon + label only.
4. **Icons**: GroupsIcon (JOIN), LockIcon (PRIVATE), AirportShuttleIcon (CHARTER). Drop the generic `CategoryOutlinedIcon`.
5. **Labels**: `CONTRACT_TYPE_NAMES` (`constants/dayTripApi.js:49` — "Join Tour"/"Private Tour"/"Charter"), not raw enum.
6. **Build**: new `components/UI/ContractTypeBadge.js` (~45 lines, twin of `ServiceCategoryBadge`, own 3-entry config). Do NOT touch `BadgeChip.js`. No `<MetaBadge>` abstraction.

## Changes
- **New** `components/UI/ContractTypeBadge.js` — Chip, props `{type, size, showIcon, sx}`, `TYPE_CONFIG` keyed by `CONTRACT_TYPE`, one indigo, Groups/Lock/AirportShuttle icons, friendly labels, null-on-unknown.
- **Edit** `pages/operators/[slug].js` — delete `getTypeColor` + inline type span → `<ContractTypeBadge>`; tweak Inactive span to `rounded-md`/28px; drop unused `CategoryOutlinedIcon` import.
- **Edit** `helpers/designSystem.js` — delete only `tourTypeSoft` (`:49-54`); keep `tourTypePrivate`/`tourTypeCharter`.

## Consequences
Unlocks: one coherent badge row, no status-color collision, friendly type labels, meaningful per-type icons. Doesn't change: service-category badge (already fine), the 14 `BadgeChip` consumers (untouched). Single-indigo is a deliberate KISS call — per-type hues deferred unless usability shows scan failure.

## Verification
Lint + build clean; `/operators/silaphat` shows uniform badge geometry, indigo types w/ correct icon+label, no green JOIN, Inactive matching; spot-check one `BadgeChip` consumer unchanged.

## Related
- [[operator-detail-page-redesign-2026-06-16]] — the redesign that introduced `tourTypeSoft` + the inline type badge being fixed here.
- [[operator-detail-seo-aeo-geo-audit]] — same page, SEO pass (separate concern).
- Reuse targets: `components/UI/ServiceCategoryBadge.js` (pattern twin), `constants/dayTripApi.js` (`CONTRACT_TYPE`/`CONTRACT_TYPE_NAMES`), `helpers/designSystem.js` (tokens).
