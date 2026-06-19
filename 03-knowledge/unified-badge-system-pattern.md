# Unified Badge System Pattern

## Summary
When a card row shows multiple metadata badges, they must share ONE geometry and differentiate semantic axes by fill + icon — NOT by clashing hue. Mixing build methods (MUI Chip vs raw span), radii, and ad-hoc per-value colors reads as "AI slop / inconsistent".

## Context
Operator contract-card on `/operators/[slug]` (audit + fix #124, [[operator-card-badge-consistency]]). One row had 3 badges from 3 systems: Inactive (raw span, 4px rect, gray), ServiceCategory (MUI Chip, 6px, soft per-category fill), ContractType (raw span, full pill, `tourTypeSoft` token). 3 radii, 2 heights, 2 build methods.

## Problem — two failure modes
1. **Geometry drift**: different radius/height/build per badge in the same cluster. Fix: one canonical primitive (here: the MUI `Chip` render — 28px / 6px / 13px / 16px icon / `marginLeft:4px`). New badge = a thin twin component with its own config map, NOT a fork of the JSX and NOT a premature generic `<MetaBadge>` (only 2 callers → twin is fine; extract a shared primitive only at the 3rd caller).
2. **Color-semantics collision**: contract type was color-coded (JOIN green `#10B981` = `COLORS.status.success`; PRIVATE/CHARTER violet = DAY_TOUR category hue). Green made a *type* read as a *status* sitting next to the gray Inactive *status* badge. 

## Decision / rules
- **Differentiate semantic axes by FILL + ICON, not hue.** Status = outlined/gray; identity (category, type) = soft-fill. Within an axis that isn't ordinal (contract type: JOIN/PRIVATE/CHARTER), use ONE color + distinct icons + friendly labels — color-coding a non-ordinal set falsely implies ranking.
- **A badge's color must not borrow another axis's reserved hue** — type color must avoid `status.success` green and the category palette (sky/violet). Use a token meant for it: `COLORS.badge.primary` (defined "for important booking behavior (contract type)").
- **Icon must be meaningful, not filler.** Generic `CategoryOutlinedIcon` on every type badge said nothing — replaced with Groups (JOIN) / Lock (PRIVATE) / AirportShuttle (CHARTER). Avoid icons already owned by another badge (DirectionsBus = TRANSPORTATION category → don't reuse for CHARTER).
- **Labels from the constants map**, not raw enums: `CONTRACT_TYPE_NAMES` ("Join Tour"), not `JOIN`.
- **Colors from design tokens, never hardcoded hex in the component.** (Caught mid-impl: had inlined `#EEF2FF` → switched to `COLORS.badge.primary`.)

## Implementation
`components/UI/ContractTypeBadge.js` — twin of `components/UI/ServiceCategoryBadge.js`, 3-entry `TYPE_CONFIG` keyed by `CONTRACT_TYPE`, single `COLORS.badge.primary`, null-on-unknown. Did NOT touch shared `BadgeChip.js` (14 consumers). Deleted dead `tourTypeSoft` token (kept `tourTypePrivate/Charter` — used by BadgeChip).

## Related
- [[operator-card-badge-consistency]] — full audit/spec
- [[design-token-caption-tailwind-gotcha]] — token-layer separation (Tailwind vs MUI vs JS hex)
- [[design-systems]]
