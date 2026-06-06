---
name: mui-menu-paper-overflow-guard
description: When MUI Menu content height > viewport, cap Paper + MenuList with maxHeight calc(100vh - N) and explicit overflow to prevent content from clipping past the bottom edge of the menu.
type: knowledge-atom
date: 2026-06-06
parent: website-audit-full-2026-06-06
---

# MUI Menu Paper Overflow Guard

## Summary
MUI Menu Paper has no implicit max-height. When anchored content + menu content > available viewport, the Paper visually "breaks" — rounded corner background ends mid-content while rows continue to render. Fix: explicit `MenuListProps` + `PaperProps` with `maxHeight: calc(100vh - N)` and `overflowY/overflow` constraints.

## Context
`website-audit-full-2026-06-06` r3-leader-synthesis. F2 (44×44 touch targets) raised `ProfileImage` desktop pill height 36→44px. This 8px re-anchored the MUI Menu 8px lower in the viewport. The Menu content (~820px tall after ProfileMenu's 3 expandables closed) exceeded available space (~650px on 1280×720). Paper's `border-radius: 16px` background ended mid-content → looked "broken" at the bottom.

## Problem
- Default MUI `Menu` Paper has no `maxHeight` constraint
- Tall content + edge anchor position = Paper bottom extends past viewport
- `border-radius: 16px` reveals the cutoff: background fades but rows keep rendering
- Mobile Bottom Sheet (`ProfileBottomSheet.js`) already has `maxHeight: '80dvh'` set — same pattern needed on desktop Menu

## Pattern
**Bad** — default Menu, no maxHeight, breaks on tall content near viewport edge:
```jsx
<Menu anchorEl={anchorEl} open={open} onClose={handleClose} sx={MENU_SX}>
  <ProfileMenu {...props} />
</Menu>
```

**Good** — explicit Paper + MenuList maxHeight with overflow constraints:
```jsx
<Menu
  anchorEl={anchorEl}
  open={open}
  onClose={handleClose}
  disableScrollLock
  MenuListProps={{
    sx: {
      padding: 0,
      maxHeight: 'calc(100vh - 120px)',
      overflowY: 'auto',
    },
  }}
  PaperProps={{
    sx: {
      maxHeight: 'calc(100vh - 120px)',
      overflow: 'hidden',  // Paper clips; MenuList scrolls inside
    },
  }}
  sx={MENU_SX}
>
  <ProfileMenu {...props} />
</Menu>
```

## Details

### Why both PaperProps AND MenuListProps
- `PaperProps.maxHeight` + `overflow: hidden` — caps the visible Paper so the rounded border + shadow + background stay inside the viewport
- `MenuListProps.maxHeight` + `overflowY: auto` — the inner `<ul>` scrolls when content exceeds the Paper height
- Without PaperProps: rounded background fades mid-row, looks broken
- Without MenuListProps: Paper scrolls as a unit, including its own rounded corners

### Why `calc(100vh - 120px)` not `calc(100vh - 8px)`
- 120px = anchor offset (12px `mt`) + 88px header height + breathing room
- Anchor at bottom of header, so available space = viewport - header height
- Use 80-120px depending on header height (single-row 80px → 80-100; 2-row 96px → 100-120)

### Why `disableScrollLock`
- Default MUI Menu locks body scroll on open
- `disableScrollLock` lets the page scroll behind the menu, matching Bottom Sheet feel
- Acceptable because Menu is short-lived and click-outside dismisses

## Trigger Conditions
Add this pattern whenever:
1. Menu content height can grow (expandable rows, dynamic lists, long user data)
2. Trigger button position can change (F2 height bump is a real-world example)
3. Menu anchored near viewport edge (header dropdowns, action menus in headers)

## Real-World Triggers (F2 post-mortem)
- Touch target height increase on anchor button (re-anchors menu lower)
- Adding 1-2 menu items to existing menu
- New viewport size (small laptop 1280×720, projector 1024×768)
- Localized text expansion (German +30% vs English)

## Tradeoffs
- **Pro:** Prevents content clipping regardless of anchor position
- **Pro:** Matches Bottom Sheet pattern (`ProfileBottomSheet.js:14-17`) — visual consistency
- **Pro:** No JS — pure CSS solution via sx
- **Con:** `overflowY: auto` shows scrollbar only when needed (mostly invisible)
- **Con:** Adds 2 props to every Menu — minor

## Verification
Test on smallest target viewport (1280×720 or 1024×768). Open menu, verify:
- Rounded border + shadow + background all stay inside viewport
- Inner content scrolls if total height > Paper height
- Trigger button position change (e.g., F2 36→44) does not break layout

## Related
- [[mui-dropdown-preserve-strategy]] — MUI Menu core for ARIA test compat
- [[expandable-menu-row-mui-collapse]] — companion pattern for tall content
- [[profile-dropdown-redesign-2026-05-29]] — original Bottom Sheet pattern
