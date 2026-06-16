---
name: r1-ux
description: Specialist A — UX/Conversion Designer. Heart/save UX analysis with industry comparison + 4 recs.
metadata:
  type: specialist-r1
  role: ux-conversion-designer
  page: favorite-heart
  smartenplus_route: /activities
  date: 2026-06-08
  parent: favorite-heart-analysis-2026-06-08
---

## UX Analysis

### Current State
Heart sits top-right (`top:8 right:8`) inside `DayTripCard.js:122-133`, wrapped in MUI `<IconButton size="medium">` with 80% white bg. Unauthenticated taps route through `useAuthRedirect` to signin. Save state optimistic, no spinner, no toast, no count, no label. No "Saved tours" surface in `ProfileMenu.js` (My Activity only has Bookings/Orders/Reviews).

### Industry Comparison

| Aspect | SmartEnPlus | Klook | Booking.com | Airbnb |
|--------|-------------|-------|-------------|--------|
| Position | top-right (`top:8 right:8`) | top-right | top-right (with count) | top-left |
| Tap target | 40px (MUI default) | ~36-40px | ~32-36px | 40px |
| Empty state | outline heart, no label | outline heart, no label | outline heart + "Saved" tooltip | outline heart, no label |
| Filled state | red `#E11D48` | red | navy/dark + count | red/pink (`#FF385C`) |
| Save feedback | none (optimistic flip) | brief animation | toast "Saved" | scale pulse + toast |
| Discovery of saved | none in nav | account → wishlist | account → saved | nav tab "Wishlists" |

### Recommendations (top 4)

1. **Add save feedback animation** — scale pulse (1.0→1.3→1.0, 200ms) on heart fill. Klook/Booking do this. 30 min CSS. — effort: S — impact: med
2. **Surface "Saved tours" in nav** — add to `ProfileMenu.js:130-141` under My Activity (next to Bookings/Orders/Reviews). Even with "Coming soon" label, user sees the heart goes somewhere. — effort: S — impact: high (reduces "save into void" confusion)
3. **Bump tap target to 44px** — switch `size="medium"` to `size="large"` or explicit `sx={{ p: 1.25 }}` (~44px). Aligns with WCAG 2.5.5 + matches social-icon batch (40×40 wrappers were added recently per `9472df5` commit). — effort: S — impact: med (mobile thumb zone)
4. **Logged-out tooltip** — show "Sign in to save" `title` attribute on the heart when no session. `BookmarkButton.js:107-118` already redirects, but tell user before tap. — effort: S — impact: low (clarity)

### UX Risks

- **Save-into-void:** heart persists data but `ProfileMenu.js` has zero wishlist entry. User clicks save → expects to find it → cannot. Highest churn risk.
- **Optimistic flip on card click collision:** `DayTripCard.js:124` uses `e.stopPropagation()` on wrapper Box, but heart itself is inside IconButton. If stopPropagation fails (event bubbling edge case), tap could trigger card navigation mid-save. Verify by clicking heart quickly during a list scroll.
- **Guest friction:** no "Sign in" hint before tap. Users waste a click + page nav to discover auth requirement. Fixable via `title` attr or visual badge.
- **No undo path:** removing a heart has no confirmation, no toast, no undo. If a user accidentally removes (e.g., double-tap during scroll), the data is gone. Toast with "Undo" 5s would match Booking.com pattern.

### Out of Scope (confirmed with user)
- Wishlist page (separate ticket)
- Heart count display
- A/B test setup
