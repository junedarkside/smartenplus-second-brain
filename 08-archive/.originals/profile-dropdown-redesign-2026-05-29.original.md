# Profile Dropdown Redesign — 2026-05-29

## Summary
3-specialist review (UX + UI/Visual + Frontend) of the current ProfileButton. Full redesign spec decided: 11→6 items, 3-file split, MUI-preserve strategy, pill trigger, bottom sheet mobile, 296px visual spec.

## Status
**DECIDED 2026-05-29.** Ready for implementation. Branch: `260528-feat/header-redesign-2026`.

---

## Problem

Current ProfileButton (`components/auth/ProfileButton.js`) is a generic MUI Menu:
- **200px wide** — truncates labels like "Account Dashboard", "Family & Friends"
- **11 items, 4 dividers** — no traveler mental model; reads as SaaS admin panel
- **Guest state dead-end** — bare PersonOutlinedIcon navigates directly to /account/login, zero information scent
- **No identity confirmation** — auth header shows avatar only, no name/email; critical on shared devices
- **Guest path missing** — `/pages/guest-order/[orderId].js` exists but profile gives guests no path to it
- **Broken cart notice** — `sx` prop on `<span>` silently ignored; "N bookings will be saved" invisible on mobile
- **Visual** — MUI defaults, no design language, `boxShadow: 3` is generic Material elevation

---

## Decision

### Architecture: Keep MUI Menu Core
**Rationale:** Integration tests use `getByRole('menu')` / `getByRole('menuitem')` ARIA semantics. Swapping to Headless UI / Radix breaks those contracts. The `isLoggingOut` close-guard on MUI `onClose` is subtle behavior. Full visual control via `PaperProps` + `sx` overrides — zero test risk.

### Mobile: MUI Drawer (bottom sheet)
`anchor="bottom"` gives backdrop, focus trap, scroll lock for free. Fits Fitts's Law — trigger is top-right corner, interaction zone is bottom of screen; bottom sheet resolves the spatial mismatch.

---

## Item Architecture (11 → 6)

### Auth State
**Header (non-interactive):** Avatar + first name (`session.first_name`) + email

| Item | Route | Subtitle |
|---|---|---|
| My Bookings | `/bookings` | "View and manage your tickets" |
| My Orders | `/orders` | "Order history and receipts" |
| — divider — | | |
| Edit Profile | `/account/profile` | "Personal details and password" |
| Family & Friends | `/account/passenger/PassengersList` | "Saved traveler profiles" |
| — divider — | | |
| Help Center | `/help` | — |
| Logout | — | Red text + icon |

**Cut:** Account Dashboard (redundant), Rate & Reviews (move to booking detail page), Edit Password (fold into Edit Profile sub-section)

### Guest State
**Header:** Circle icon + "Guest Traveler" + "Access your bookings anytime"

| Item | Route | Subtitle |
|---|---|---|
| Find My Booking | `/bookings?guest=true` | "Look up with reference number" |
| Sign In | `/account/login` | "Access your saved trips" |
| Create Account | `/account/register` | "Save bookings and travel faster" |
| Help Center | `/help` | — |

---

## Visual Spec

### Dropdown Surface
| Property | Value |
|---|---|
| Width | 296px |
| Border-radius | 16px (`rounded-2xl`) |
| Background | `#FFFFFF` |
| Border | `1px solid #E5E7EB` |
| Shadow | `0 8px 24px rgba(0,0,0,0.10), 0 2px 8px rgba(0,0,0,0.06)` |
| Top offset | 12px margin from trigger |

### Typography
| Element | Size | Weight | Color |
|---|---|---|---|
| User name | 14px | 600 | `#111827` |
| Email | 12px | 400 | `#6B7280` |
| Item label | 14px | 500 | `#374151` |
| Item subtitle | 12px | 400 | `#9CA3AF` |
| Logout | 14px | 500 | `#EF4444` |

### Colors
- Row hover: `#F9FAFB` background only
- Row active: `#F3F4F6`
- Icons rest: `#9CA3AF` → hover row: `#4B5563`
- Icons: outline-only, no fills
- Dividers: `#F3F4F6`, 1px — **only 2 dividers** (after header, before logout)
- Logout: `#EF4444` at rest and hover

### Row Sizing
- Desktop: 48px height, `px-4 py-3`
- Mobile: 56px height (WCAG 2.2 touch target)

### MUI sx Key Override
```js
'& .MuiPaper-root': {
  width: '296px',
  borderRadius: '16px',
  border: '1px solid #E5E7EB',
  boxShadow: '0 8px 24px rgba(0,0,0,0.10), 0 2px 8px rgba(0,0,0,0.06)',
  mt: '12px',
}
```

---

## ProfileImage Trigger Redesign

Replace bare Avatar + grey badge with **pill button**:

- Desktop: `h-10 px-3 rounded-full border border-gray-200 bg-white hover:bg-gray-50`
- Left: 32px avatar (brightness-normalized initials)
- Right of avatar: first name (14px/500) + "My Account" (11px/400 gray400)
- Far right: 16px chevron gray400, rotates 180deg when open
- Mobile (`< md`): avatar-only 44×44px tap target, no text/chevron

**Fix `stringToColor`:** constrain output to `hsl(H, 55%, 45%)` — brightness floor prevents near-black or oversaturated avatars.

---

## File Structure (3-file split)

```
components/auth/
  ProfileButton.js        # ~120L — orchestrator, state + logout (MODIFY)
  ProfileMenu.js          # ~130L — content, guest/auth variants (NEW)
  ProfileBottomSheet.js   # ~80L  — MUI Drawer wrapper (NEW)
  ProfileImage.js         # MODIFY — pill trigger, fix stringToColor
```

### ProfileButton.js
- All existing state preserved: `anchorEl`, `isLoggingOut`, `logoutError`, `isNavigating`
- Add: `isMobile = useMediaQuery(theme.breakpoints.down('md'))`
- Renders desktop MUI Menu OR mobile Drawer, both using `<ProfileMenu>`
- **Logout 4-step flow: unchanged**

### ProfileMenu.js props
```js
{ session, status, isLoggingOut, logoutError, logoutHandler, navigateTo, onClose }
```

### ProfileBottomSheet.js
MUI `Drawer anchor="bottom"`, `PaperProps: { borderRadius: '16px 16px 0 0' }`, drag handle, 80dvh max-height.

---

## Mobile Bottom Sheet Spec
- `borderRadius: '16px 16px 0 0'` (top corners only)
- Drag handle: 32×4px, `bg-gray-300`, centered, 8px top margin
- Backdrop: `rgba(0,0,0,0.35)`, 150ms fade
- Max-height: `80dvh`, overflow-y auto
- Row height: 56px

---

## Debate Summary

**UX Specialist:**
- Cut 5 items (Dashboard, Rate&Reviews, Edit Password as top-level, and restructure)
- Guest dead-end is a conversion failure — guest order lookup path exists but unreachable
- Bottom sheet wins on Fitts's Law and OTA convention (Booking.com, Grab, Airbnb all use it)
- Identity confirmation missing from auth header — critical on shared/family devices

**UI/Visual Specialist:**
- 200px clips labels; 296px minimum
- grey.300 badge creates competing affordances with fb-blue ring
- `stringToColor` needs brightness floor — arbitrary hex produces jarring avatars
- Only 2 dividers — current 4 carry equal weight, making sections feel arbitrary
- Logout red text+icon is the signal; no background change needed

**Frontend Engineer:**
- Keep MUI Menu — tests use ARIA semantics that Radix/Headless UI would break
- MUI Drawer for bottom sheet — backdrop + focus trap for free, reuses existing MUI stack
- 3-file split stays under 200L/component limit
- Migration risk low — only `main-header.js` consumes ProfileButton, no API change
- Some integration tests assert on `console.log` strings that don't exist in current code — already broken, need updating regardless

**Consensus reached:** All 3 agree on item reduction, MUI-preserve, 3-file split, bottom sheet, 296px spec.

---

## Implementation Notes
- `navigateTo` + logout logic: pass as props to ProfileMenu (no state duplication)
- RTK Query hooks (`useCheckCartIdQuery`, `useDeleteCartMutation`) stay in ProfileButton
- `useSession` stays in ProfileButton
- Language & Currency selector: deferred — can be added as optional footer row later
- `Rate & Reviews` UX: recommend moving link to booking detail page (`/bookings/[id]`)

---

## Related
- `ProfileButton.js` — `components/auth/ProfileButton.js` (current implementation)
- [[header-redesign-2026-implementation]] — parent branch context
- [[smartenplus-2026-ux-direction]] — strategic UX direction ("operational" over "cinematic")
- [[mui-tailwind-css-specificity]] — MUI sx vs Tailwind specificity rules
