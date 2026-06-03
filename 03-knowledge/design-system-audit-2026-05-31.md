# Design System Audit — 2026-05-31

## Brand Color
**`#3b5998`** — Facebook blue, correct brand color.

Was `#1E40AF` in earlier edits. Reverted to `#3b5998`.

## Single Source of Truth
`helpers/designSystem.js` — all design tokens defined here.

## Key Tokens

### Colors
```js
COLORS.brand.primary // '#3b5998'
COLORS.brand.primaryDark  // '#2d4373'
COLORS.brand.secondary    // '#2563eb'
COLORS.badge.primary.color // '#1E40AF' (badge text, not main brand)
COLORS.status.success     // '#10B981'
COLORS.status.warning // '#F59E0B'
COLORS.status.error       // '#EF4444'
COLORS.status.info        // '#3B82F6'
```

### Tailwind Config
```js
'fb-blue': '#3b5998'           // same as COLORS.brand.primary
'brand.primary': '#3b5998'
'brand.primary-dark': '#2d4373'
```

### MUI Theme
```js
// theme.js
palette.primary.main: '#3b5998'
```

## Files Updated (15 total)

### Brand Color Fixes (8 files)
| File | Change |
|------|--------|
| `components/UI/ScrollTop.js` | `backgroundColor: '#3b5998'` |
| `components/payment/QRPaymentForm.js` | COLORS.brand.primary |
| `components/bookings/PdfViewImproved.js` | COLORS.brand.primary |
| `components/auth/LogoutProgressModal.js` | COLORS.brand.primary |
| `components/activities/shared/PricingDisplay.js` | COLORS.brand.primary |
| `components/UI/CarouselArrowButtons.js` | COLORS.badge.primary.color |
| `components/UI/ServiceCategoryBadge.js` | COLORS.badge.primary.color |
| `components/UI/PassengerCountBadge.js` | COLORS.badge.primary.color |
| `components/auth/ProfileMenu.js` | COLORS.badge.primary.color |

### Button Component Fixes (4 files)
| File | Change |
|------|--------|
| `components/auth/common/SubmitButton.js` | `getButtonClasses('primary')` |
| `components/checkout/Coupon.js` | `getButtonClasses('primary')` |
| `components/forms/FormCard.js` | `getButtonClasses('primary')` |
| `components/auth/common/SocialSignIn.js` | `CARD_CONFIG.border`, `rounded-md` |

### Spacing/Border Fixes (3 files)
| File | Change |
|------|--------|
| `lib/homepage/components/DiscoverySection.js` | `rounded-xl` → `rounded-md` |
| `lib/homepage/components/TravelThailandBetterSection.js` | `rounded-xl` → `rounded-md` |
| `lib/homepage/components/AirportTransferSection.js` | `gap-4` → `gap-1 md:gap-2 lg:gap-3` |

## Design System Utilities

```js
import { COLORS, getButtonClasses, getCardClasses, getInputClasses, BUTTON_CONFIG, CARD_CONFIG } from '../helpers/designSystem'
```

- `getButtonClasses('primary')` → `bg-fb-blue text-white font-bold px-6 py-3 rounded-md` + hover
- `getButtonClasses('secondary')` → `bg-white text-gray-800 border border-gray-300 px-6 py-3 rounded-md` + hover
- `getCardClasses(hover)` → `p-4 rounded-md border border-gray-200 bg-white` + hover shadow
- `getInputClasses(hasError, isDisabled)` → `w-full px-4 py-3 text-base border border-gray-200 rounded-lg` + focus/error states

## Audit Findings (before fix)
- 16 high severity hardcoded brand/badge colors
- 21 medium severity hardcoded status colors
- 0 components used `getButtonClasses()` before audit
- Only `UnifiedCard` used `getCardClasses()`
- 3 homepage sections used `rounded-xl` on non-image-card elements