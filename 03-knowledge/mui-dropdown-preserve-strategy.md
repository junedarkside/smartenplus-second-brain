# MUI Dropdown Preserve Strategy

## Summary
Keep MUI Menu core for ARIA test compatibility. Mobile: MUI Drawer as bottom sheet. Item reduction 11→6. 3-file split architecture.

## Context
`profile-dropdown-redesign.md`. 3-specialist review (UX + UI/Visual + Frontend). ProfileButton was generic MUI Menu, 11 items, no traveler mental model.

## Problem
- 200px width truncates labels like "Account Dashboard", "Family& Friends"
- 11 items, 4 dividers — reads as SaaS admin panel
- Guest state dead-end — no path to guest order lookup
- No identity confirmation on shared devices
- Integration tests use `getByRole('menu')` / `getByRole('menuitem')` ARIA semantics

## Decision

### Keep MUI Menu Core
**Rationale:** Swapping to Headless UI / Radix breaks ARIA test contracts. `isLoggingOut` close-guard on MUI `onClose` is subtle behavior. Full visual control via `PaperProps` + `sx` overrides.

```jsx
// ProfileButton.js — Desktop: renders MUI Menu
// ProfileBottomSheet.js — Mobile: renders MUI Drawer anchor="bottom"
// Both use <ProfileMenu> for content
```

### Mobile: MUI Drawer Bottom Sheet
- `anchor="bottom"` gives backdrop, focus trap, scroll lock for free
- `PaperProps: { borderRadius: '16px 16px 0 0' }`
- Drag handle: 32x4px `bg-gray-300`, centered, 8px top margin
- Max-height: `80dvh`, overflow-y auto
- Row height: 56px (WCAG 2.2 touch target)

### Item Architecture (11 → 6)

**Auth State:**
| Item | Route |
|------|-------|
| My Bookings | `/bookings` |
| My Orders | `/orders` |
| Edit Profile | `/account/profile` |
| Family & Friends | `/account/passenger/PassengersList` |
| Help Center | `/help` |
| Logout | — (red text + icon) |

**Guest State:**
| Item | Route |
|------|-------|
| Find My Booking | `/bookings?guest=true` |
| Sign In | `/account/login` |
| Create Account | `/account/register` |
| Help Center | `/help` |

**Cut:** Account Dashboard, Rate & Reviews, Edit Password (fold into Edit Profile)

### Visual Spec
- Width: 296px
- Border-radius: 16px (`rounded-2xl`)
- Shadow: `0 8px 24px rgba(0,0,0,0.10), 0 2px 8px rgba(0,0,0,0.06)`
- Top offset: 12px margin from trigger
- Dividers: only 2 (after header, before logout)

### File Structure
```
components/auth/
  ProfileButton.js        # ~120L — orchestrator, state + logout
  ProfileMenu.js          # ~130L — content, guest/auth variants
  ProfileBottomSheet.js   # ~80L  — MUI Drawer wrapper
  ProfileImage.js         # MODIFY — pill trigger, fix stringToColor
```

## Details

### MUI sx Key Override
```jsx
'& .MuiPaper-root': {
  width: '296px',
  borderRadius: '16px',
  border: '1px solid #E5E7EB',
  boxShadow: '0 8px 24px rgba(0,0,0,0.10), 0 2px 8px rgba(0,0,0,0.06)',
  mt: '12px',
}
```

### stringToColor Fix
Constrain output to `hsl(H, 55%, 45%)` — brightness floor prevents near-black or oversaturated avatars.

### ProfileImage Trigger Redesign
- Desktop: `h-10 px-3 rounded-full border border-gray-200 bg-white hover:bg-gray-50`
- Left: 32px avatar
- Right: first name (14px/500) + "My Account" (11px/400 gray400)
- Far right: 16px chevron, rotates 180deg when open
- Mobile (`< md`): avatar-only 44x44px tap target

## Tradeoffs
- 3-file split keeps each file under 200L/component limit
- Guest state loses "Help Center" divider aesthetic — acceptable
- Logout red text+icon signal enough — no background change needed

## Consequences
- Integration tests pass with `getByRole('menu')` queries
- Guest users have path to booking lookup
- Identity confirmation via avatar + name + email in header

## Related
- [[mui-tailwind-css-specificity]] — MUI sx vs Tailwind specificity
- [[header-redesign-2026-team-review]] — header context