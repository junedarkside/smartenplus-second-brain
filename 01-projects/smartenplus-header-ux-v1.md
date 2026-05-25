# SmartEnPlus Desktop Header UX/UI — Implementation v1

## Status: COMPLETED 2026-05-25

---

# Executive Summary

Desktop header restructured into 2-row layout for desktop. Mobile behavior identical to pre-change — single row with hamburger menu. Help Center added to profile dropdown.

---

# Final Desktop Header Wireframe

```
#################################################################

 [ SmartEnPlus ]

                                  THB   🛒   👤

---------------------------------------------------------------

 Explore Thailand   Routes   Experiences   Journeys   Guides

#################################################################
```

---

# Row 1 — Utility Layer (all screen sizes)

Purpose: branding, operational utilities, booking state, account access

```
[ SmartEnPlus ]                        THB   🛒   👤
```

**Components:**
- Logo + brand name → links to `/`
- THB button → standalone CurrencySelectorMenu (hidden on mobile `hidden md:flex`)
- 🛒 → CartButton
- 👤 → ProfileButton

**Mobile:** blue background (`bg-fb-blue`), white logo text
**Desktop:** white background, gray logo text

---

# Row 2 — Exploration Layer (desktop only)

Purpose: ecosystem navigation, travel discovery, movement exploration

```
Explore Thailand   Routes   Experiences   Journeys   Guides
```

Hidden on mobile (`hidden md:block`). Nav items use `hidden md:flex`.

**Submenus deferred** — caused tech debt in prior attempt. When re-activated:
- Backend NavigationItem data fully populated
- Frontend NavDropdown stable
- Separate implementation ticket

---

# Profile Dropdown — v1 Additions

**Added this version:**
- Help Center → `/help` (page exists, uses `HelpOutlineOutlinedIcon`)

**Deferred:**
- Saved Trips → needs `/saved-trips` page
- Language → next version

---

# Bugs Caught During Implementation

1. **`hidden md:flex` dropped from nav** — accidentally removed during restructure. Restored.
2. **`bg-fb-blue md:bg-white` wrapper removed** — accidentally removed during restructure. Restored around Row 1 Toolbar.
3. **Row 2 showed on mobile** — Divider + Toolbar visible even with `hidden md:flex` on nav. Fixed by wrapping Divider + Row 2 in `hidden md:block` div.

---

# Verification

1. `npm run dev` — dev server on localhost:3000
2. Desktop viewport — header shows 2-row layout
3. THB button standalone, not inside profile dropdown
4. Profile dropdown — Help Center visible when logged in
5. Mobile — hamburger menu, single row only (no Divider visible)
6. navConfig fallback renders correctly

---

# Implementation Files

| File | Change |
|------|--------|
| `components/layout/main-header.js` | 2-row layout (Row 1 + Divider + Row 2 wrapped in `hidden md:block`) |
| `components/auth/ProfileButton.js` | Help Center menu item added |

---

# Related Docs

- [[nav-config-research]] — prior nav UX research
- [[navigation-api]] — backend NavigationSection API
- [[smartenplus-header-ux-v1]] — original research doc (superseded by this)