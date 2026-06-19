# Design System Phase 1 Migration

## Summary
Replaced hardcoded hex colors with `COLORS` token imports from `helpers/designSystem.js` across 16 component files. Exact-value-only replacement — no visual changes.

## Context
Audit (2026-06-13) found 290 hardcoded hex colors in components/pages. Phase 1 targets: components only (pages handled separately). Only replace hex values that exactly match an existing token.

## Token Mappings Used

| Token | Hex | Usage |
|-------|-----|-------|
| `COLORS.brand.primary` | `#3b5998` | ScrollTop, brand accents |
| `COLORS.status.error` | `#EF4444` | Danger text, logout, urgency |
| `COLORS.status.warning` | `#F59E0B` | Amber icons, star rating, QR timer |
| `COLORS.status.success` | `#10B981` | Checkmark icons, ATTRACTION_TICKET |
| `COLORS.status.info` | `#3B82F6` | Checkbox checked, ACCOMMODATION icon |
| `COLORS.neutral.gray50` | `#F9FAFB` | Hover backgrounds, ProfileImage |
| `COLORS.neutral.gray100` | `#F3F4F6` | Active backgrounds, avatar placeholder |
| `COLORS.neutral.gray200` | `#E5E7EB` | Borders, empty star, menu outline |
| `COLORS.neutral.gray300` | `#D1D5DB` | Bottom sheet handle |
| `COLORS.neutral.gray400` | `#9CA3AF` | Disabled icons, secondary text, chevrons |
| `COLORS.neutral.gray500` | `#6B7280` | Subtitle text, icon color, avatar text |
| `COLORS.neutral.gray700` | `#374151` | Label text, menu row text |
| `COLORS.neutral.gray800` | `#1F2937` | OTHER category text |
| `COLORS.neutral.gray900` | `#111827` | Primary text, headings |
| `COLORS.badge.primary.color` | `#1E40AF` | Focus ring, nav avatar |
| `COLORS.badge.tourTypePrivate` | `#7C3AED` | DAY_TOUR icon color |
| `Z_INDEX.scrollTop` | `500` | ScrollTop z-index |

## Files Changed (16)

| File | Key Replacements |
|------|-----------------|
| `components/auth/ProfileMenu.js` | 23 colors — gray50-900, error, gray400 |
| `components/UI/ServiceCategoryBadge.js` | 6 colors — tourTypePrivate, success, warning, info, gray500, gray800 |
| `components/UI/ScrollTop.js` | brand.primary, Z_INDEX.scrollTop |
| `components/UI/CarouselArrowButtons.js` | gray400 (2x) |
| `components/UI/DynamicCheckboxItem.js` | info, gray700, gray900 (2x) |
| `components/auth/ProfileBottomSheet.js` | gray300 |
| `components/activities/detail/DayTripDetailPage.js` | gray200 |
| `components/activities/shared/KeyFeatures.js` | success |
| `components/activities/shared/UrgencyMessage.js` | error, warning |
| `components/auth/ProfileButton.js` | gray200, gray400 |
| `components/auth/ProfileImage.js` | gray50, gray100, gray200, gray400, gray500, gray700 |
| `components/blog/BookmarkButton.js` | badge.primary.color |
| `components/payment/QRPaymentForm.js` | gray200, warning |
| `components/review/BookingReviewList.js` | gray200 |
| `components/review/ReviewFirstPage.js` | gray400 |
| `components/UI/ProfileHeader.js` | gray500 (4x) |

## Files Skipped (20)

Three categories of skips:

1. **No exact token match** — Material Design colors (`#4CAF50`, `#FF9800`), Tailwind semantic (`#FEF2F2`, `#F0FDF4`), amber stars (`#FFA000`), brand variants (`#1877f2`, `#368ed6`)
2. **Already tokenized** — BadgeChip.js, PassengerCountBadge.js, SortBar.js
3. **Excluded** — pdfStyles.js (PDF rendering may not support JS imports)

## Decision Rules

- Only exact hex match replaced (case-insensitive)
- `#fff` / white left alone — universal, no token
- rgba() values not replaced — token system is hex-only
- SVG fills in icon components (`suv-icon.js`) left alone — `#263238` not in tokens
- Added `import { COLORS }` only when file had replacements

## Gotcha: QRPaymentForm Margin Fix

Commit `c55f6a1` fixed `md:m-2` -> `my-2` on QRPaymentForm. Token changes only touched SVG stroke colors in `CountdownRing` — no layout impact. Confirmed via `git diff`.

## Related
- [[design-systems]] — Token architecture
- [[design-system-audit]] — Full audit, migration roadmap
- [[design-token-caption-tailwind-gotcha]] — Tailwind strings vs MUI sx
- [[designsystem-shadow-border-tokens]] — Shadow/border tokens
