# Nav/Header Redesign

## Summary
Minimal white nav redesign for SmartEnPlus. Desktop: white bg, border-b, tab-style active links. Mobile: brand blue bg unchanged. Full a11y baseline added.

## Context
Previous header: two-tone (blue mobile / gray-50 desktop), pipe-separated nav links, no active state, no keyboard accessibility, profile icon clipped on Mac mini.

## Changes (commit 082a154, 2026-05-19)

Files: `components/layout/main-header.js`, `components/layout/layout.js`, `components/auth/ProfileImage.js`

### Desktop
- `bg-white` replaces `bg-gray-50`. `border-b border-gray-200` separator.
- `<nav aria-label="Primary navigation">` replaces div with pipe spans
- Active link: `text-brand-primary border-b-2 border-brand-primary` (tab indicator)
- Hover: `hover:text-gray-900 hover:border-gray-300`
- Focus: `focus-visible:ring-2 focus-visible:ring-brand-primary focus-visible:ring-inset`
- `aria-current="page"` on active link
- Skip-to-content `<a href="#main-content">` (sr-only, visible on focus)
- `max-w-7xl` replaces hardcoded `max-w-[1200px]`

### Mobile
- Brand blue `bg-fb-blue` preserved
- Consistent icon color: `text-white md:text-gray-600` on hamburger + logo text (matches CartButton + ProfileButton)
- Drawer: `IconButton` replaces bare div for close button (keyboard accessible)
- Drawer active item: left border + `primaryLight` bg + `aria-current="page"`

## Decisions

### MUI AppBar color="inherit" required
MUI AppBar defaults to `color="primary"` which injects `bgcolor: '#3f51b5'` overriding ALL Tailwind bg classes on the inner div. Adding `color="inherit"` makes the AppBar transparent to parent CSS.
**Rule:** When using Tailwind bg classes inside AppBar, always set `color="inherit"` on AppBar.

### justify-end not justify-between for right icon cluster
Using `justify-between` on the right-side flex cluster spreads items across the full remaining width after logo (can be 900px+), creating huge gaps and pushing rightmost icon off-screen.
**Rule:** Right-side toolbar icon clusters should use `justify-end` + `gap-*`. The outer Toolbar `justify-between` handles logo↔cluster separation.

### ProfileImage Box size must contain badge overflow
`ProfileImage` chevron badge positioned `bottom:-2, right:-2` — overflows the container Box. MUI AppBar applies `overflow:hidden` which clips it. Fixed by expanding Box from `width:40, height:40` to `width:44, height:44`.
**Rule:** Absolutely positioned badge children that use negative offsets need their parent container sized to contain them, especially inside `overflow:hidden` ancestors.

### Consistent mobile/desktop icon color pattern
CartButton, ProfileButton, hamburger, logo text all use `text-white md:text-gray-600`. This two-state color class handles the bg switch (blue mobile → white desktop) in one place.
**Rule:** All header icons/text on bg-switching header use `text-white md:text-gray-600`.

## A11y Baseline for Nav

Minimum required for a production nav:
- `<nav aria-label="Primary navigation">` — nav landmark
- `aria-current="page"` — current page signal
- `focus-visible:ring` — visible keyboard focus
- Skip-to-content link (`sr-only focus:not-sr-only`) + `id="main-content"` on `<main>`
- Close buttons as `<IconButton>` not bare `<div>`

## Related
- [[design-systems]]
- [[architecture]]
- [[admin-dashboard-component-patterns]]
