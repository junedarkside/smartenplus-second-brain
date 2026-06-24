# Design System Audit — Activity Detail Page (2026-06-19)

## Summary

Full design token compliance audit of `/activities/detail/[slug]` page and all components it renders. Scoped audit: 18 components checked. Found 42 violations across 6 categories. Previous audit (2026-06-13) was project-wide; this targets activity detail specifically and tracks new violations introduced after that audit.

---

## Scope

Page root: `components/activities/detail/DayTripDetailPage.js`

Components audited:
- `DayTripDetailPage.js` · `AirbnbPhotoGrid.js` · `DayTripHero.js`
- `DayTripDetailHeader.js` · `ExperienceTitleArea.js` · `ExperienceHighlights.js`
- `WhyTravelersLove.js` · `IncludedExcluded.js` · `MeetingPointCard.js`
- `ExperienceFAQ.js` · `PremiumBookingPanel.js` · `DayTripMobileBookingBar.js`
- `RelatedExperiences.js` · `DayTripCard.js` · `RatingDisplay.js`
- `PricingDisplay.js` · `PricingTypeBadge.js` · `PromotionalBadge.js`
- `FeaturedImageHeader.js` · `BookedCounter.js` · `ShareButton.js`

---

## Token Reference (source: `helpers/designSystem.js`)

| Token | Value |
|-------|-------|
| `COLORS.brand.primary` | `#3b5998` |
| `COLORS.brand.primaryDark` | `#2d4373` |
| `COLORS.brand.secondary` | `#2563eb` |
| `COLORS.status.success` | `#10B981` |
| `COLORS.status.warning` | `#F59E0B` |
| `COLORS.status.error` | `#EF4444` |
| `COLORS.status.info` | `#3B82F6` |
| `COLORS.neutral.gray400` | `#9CA3AF` |
| `COLORS.neutral.gray500` | `#6B7280` |
| `COLORS.neutral.gray50` | `#F9FAFB` |
| `BORDER_RADIUS.container` | `6px` |
| `BORDER_RADIUS.badge` | `4px` |
| `BORDER_RADIUS.input` | `8px` |
| `BORDER_RADIUS.imageCard` | `12px` |
| `ELEVATION_TOKENS.sm` | `0 1px 2px rgba(0,0,0,0.05)` |
| `ELEVATION_TOKENS.md` | `0 4px 16px rgba(0,0,0,0.12)` |
| `ELEVATION_TOKENS.lg` | `0 8px 24px rgba(0,0,0,0.10), 0 2px 8px rgba(0,0,0,0.06)` |

---

## Violations by Component

### DayTripDetailPage.js
- `[VIOLATION]` hardcoded `borderRadius: '8px !important'` → use `BORDER_RADIUS.input`
- `[VIOLATION]` hardcoded `'rounded-md'` Tailwind in skeleton → acceptable but inconsistent with sx-based radius in rest of file
- `[OK]` uses `COLORS.neutral.gray200` for border

### AirbnbPhotoGrid.js
- `[VIOLATION]` `h-[480px]` + `rounded-xl` — `rounded-xl` is 12px correct but Tailwind class, not token
- `[VIOLATION]` `bg-black/40 hover:bg-black/50` — opacity not from `OPACITY` scale
- `[VIOLATION]` `boxShadow: 2` (MUI numeric shorthand) — should be `ELEVATION_TOKENS.sm` string
- `[VIOLATION]` `fontSize: '0.75rem'` — should be `TYPOGRAPHY_SCALE.caption` (text-xs)
- `[OK]` no hardcoded hex colors

### DayTripHero.js
- `[VIOLATION]` error fallback gradient `from-blue-400 to-blue-600` — hardcoded Tailwind colors, should use `COLORS.brand.primary`/`secondary`
- `[VIOLATION]` `bg-white/80`, `rounded-full`, `shadow-md` on back button — opacity not from scale; `rounded-full` has no token
- `[VIOLATION]` `bg-white bg-opacity-20 hover:bg-opacity-30` — 20%/30% not in `OPACITY` scale
- `[OK]` error/loading state logic correct; `bgDefault` fallback wired

### DayTripDetailHeader.js
- `[VIOLATION]` `color: '#666'` × 3 (lines 176, 189, 202) — should be `COLORS.neutral.gray500` (`#6B7280`)
- `[OK]` badge colors use `COLORS.badge.*` correctly

### ExperienceHighlights.js
- `[VIOLATION]` `mt: '2px'` inline — below spacing scale minimum (xs = 4px)
- `[VIOLATION]` `fontSize: '0.9rem'` — not in `TYPOGRAPHY_SCALE`; use body (14→16px)
- `[OK]` `COLORS.status.success` used correctly for checkmark icon

### WhyTravelersLove.js
- `[VIOLATION]` `'rounded-xl bg-gray-50'` — `bg-gray-50` should reference `COLORS.neutral.gray50`
- `[VIOLATION]` `fontSize: '0.85rem'` — should be `TYPOGRAPHY_SCALE.small`
- `[OK]` `COLORS.brand.primary`, `COLORS.status.warning` used correctly

### IncludedExcluded.js
- `[VIOLATION]` `border border-gray-200` × 2 — not referencing `COLORS.neutral.gray200` via token
- `[VIOLATION]` `bg-gray-50` — should use `COLORS.neutral.gray50`
- `[OK]` `COLORS.status.success`, `COLORS.neutral.gray700` used correctly

### MeetingPointCard.js
- `[VIOLATION]` `color: '#1D4ED8'` — not in design system; closest is `COLORS.brand.secondary` (`#2563eb`) or `COLORS.status.info` (`#3B82F6`)
- `[VIOLATION]` `border border-gray-200 rounded-xl` — Tailwind not token-referenced
- `[VIOLATION]` `bg-blue-50` — no equivalent token; closest `COLORS.neutral.gray50` or `COLORS.badge.primary.bg` (`#DBEAFE`)

### ExperienceFAQ.js
- `[VIOLATION]` `borderRadius: '8px !important'` — use `BORDER_RADIUS.input`
- `[OK]` `COLORS.neutral.gray200` used correctly

### PremiumBookingPanel.js
- `[VIOLATION]` `boxShadow: '0 2px 20px rgba(0,0,0,0.12)'` — use `ELEVATION_TOKENS.md`
- `[VIOLATION]` `borderRadius: '16px'` — no 16px token; closest `BORDER_RADIUS.imageCard` (12px)
- `[VIOLATION]` `fontSize: '0.7rem'` — below `TYPOGRAPHY_SCALE.caption` (12px min); use `caption`
- `[OK]` `COLORS.neutral.gray200` used correctly

### DayTripMobileBookingBar.js
- `[VIOLATION]` `bg-red-50`, `text-red-600` — no token; should derive from `COLORS.status.error`
- `[VIOLATION]` `text-gray-500` × 3 — Tailwind, not referencing `COLORS.neutral.gray500`
- `[VIOLATION]` `borderRadius: '6px'` inline — use `BORDER_RADIUS.button`
- `[VIOLATION]` `padding: '10px 20px'`, `fontSize: '0.9rem'` — off-scale values
- `[OK]` `COLORS.brand.secondary`, `COLORS.brand.secondaryDark` used correctly for CTA button

### RatingDisplay.js
- `[VIOLATION]` `#FFA000` (star amber) — should be `COLORS.status.warning` (`#F59E0B`)

### PromotionalBadge.js
- `[VIOLATION]` `rgba(16, 185, 129, 0.95)` — should be `COLORS.status.success` + opacity
- `[VIOLATION]` `rgba(245, 158, 11, 0.95)` × 2 — should be `COLORS.status.warning` + opacity
- `[VIOLATION]` `rgba(24, 119, 242, 0.95)` — custom; closest `COLORS.brand.secondary` + opacity
- `[VIOLATION]` `boxShadow: '0 2px 8px rgba(0,0,0,0.15)'` — use `ELEVATION_TOKENS.sm`

### BookedCounter.js
- `[VIOLATION]` `bg-blue-100` Tailwind — should use `COLORS.badge.primary.bg` (`#DBEAFE`)
- `[VIOLATION]` `text-fb-blue` legacy custom class — should use `COLORS.badge.primary.color` (`#1E40AF`)

### FeaturedImageHeader.js
- `[VIOLATION]` default `dominantColor = 'rgb(156, 163, 175)'` hardcoded — should be `COLORS.neutral.gray400` as CSS rgb()

### ShareButton.js
- `[VIOLATION]` `color: copied ? 'green' : 'inherit'` — should use `COLORS.status.success`
- `[VIOLATION]` `shadow-lg`, `text-gray-800`, `text-gray-500` — Tailwind not token-referenced

### PricingDisplay.js · PricingTypeBadge.js · RelatedExperiences.js · DayTripCard.js · ExperienceTitleArea.js
- `[OK]` All fully compliant with design tokens

---

## Violation Summary

| Category | Count | Severity |
|----------|-------|----------|
| Hardcoded hex/rgb colors | 8 | High |
| Off-scale font sizes (`0.7rem`, `0.85rem`, `0.9rem`) | 6 | Medium |
| Border radius inline (not using `BORDER_RADIUS.*`) | 7 | Medium |
| Box shadow not using `ELEVATION_TOKENS` | 4 | Medium |
| Tailwind color classes not token-referenced | 9 | Low |
| Off-scale opacity/spacing | 5 | Low |
| **Total** | **39** | — |

---

## Priority Fix List

### P0 — Wrong color (no token exists at all)
1. `MeetingPointCard.js` `#1D4ED8` → `COLORS.brand.secondary` or `COLORS.status.info`
2. `RatingDisplay.js` `#FFA000` → `COLORS.status.warning`
3. `DayTripDetailHeader.js` `#666` × 3 → `COLORS.neutral.gray500`
4. `ShareButton.js` `'green'` → `COLORS.status.success`

### P1 — Shadow/radius inline values
5. `PremiumBookingPanel.js` custom `boxShadow` → `ELEVATION_TOKENS.md`
6. `PromotionalBadge.js` custom `boxShadow` → `ELEVATION_TOKENS.sm`
7. `PremiumBookingPanel.js` `borderRadius: 16px` → decide: extend `BORDER_RADIUS` or use 12px
8. `ExperienceFAQ.js` + `DayTripDetailPage.js` `borderRadius: '8px !important'` → `BORDER_RADIUS.input`

### P2 — Font size off-scale
9. `PremiumBookingPanel.js` `0.7rem` → `caption` (12px)
10. `DayTripMobileBookingBar.js` `0.9rem` → `body` (14–16px)
11. `WhyTravelersLove.js` `0.85rem` → `small`
12. `ExperienceHighlights.js` `0.9rem` → `body`

### P3 — Tailwind Tailwind color classes (low-risk, high-volume)
13. `BookedCounter.js` → swap Tailwind for token values
14. `DayTripHero.js` error gradient → `COLORS.brand.*`
15. `IncludedExcluded.js`, `MeetingPointCard.js` `bg-gray-50`, `border-gray-200` → reference tokens

---

## Missing Tokens (system gap, not component bug)

| Gap | Impact | Recommendation |
|-----|--------|----------------|
| No circular radius token (`rounded-full`) | Used in 4 components | Add `BORDER_RADIUS.circle: '50%'` or `'9999px'` |
| `OPACITY` scale not mapped to Tailwind bg-opacity | 6 components use `bg-white/20` etc. | Add Tailwind `backgroundOpacity` mapping in config |
| No `0.7rem` / `0.85rem` / `0.9rem` in `TYPOGRAPHY_SCALE` | Components invent sizes | Enforce: `caption` (12px) is minimum; ban sub-caption sizes |
| No error-state tinted background token | `DayTripMobileBookingBar` uses `bg-red-50` | Add `COLORS.status.errorLight` or `COLORS.badge.error.bg` |

---

## New Violations vs 2026-06-13 Audit

2026-06-13 audit was project-wide. These violations are specific to activity detail page and include regressions from post-audit work:

- `AirbnbPhotoGrid.js` — new file (added post-audit), never audited
- `PromotionalBadge.js` rgba violations — existed pre-audit, not in P0/P1 list previously
- `BookedCounter.js` legacy `text-fb-blue` — existed pre-audit
- `PremiumBookingPanel.js` `16px` radius — no token for it (system gap)

---

## Related

- [[design-system-audit]] — project-wide audit, migration roadmap
- [[design-system-phase1-migration]] — token completion tasks
- [[design-systems]] — token inventory
- `helpers/designSystem.js` — source of truth

## Atomized Notes (Extracted 2026-06-24)

- [[design-system-missing-tokens-gaps]] — 4 system-level token gaps (no circular radius, OPACITY unmapped, no sub-caption sizes, no error-tinted bg) that force invented values. Track as token-layer todo, not per-component.
