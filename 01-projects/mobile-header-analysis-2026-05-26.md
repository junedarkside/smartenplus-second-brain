# Mobile Header Analysis — Original vs Current

## Original Mobile Header (git HEAD)

**File:** `components/layout/main-header.js` at git HEAD

- **AppBar:** No `position` prop (defaults to `relative` in MUI)
- **Slide wrapper:** `<Slide appear={false} direction="down" in={!trigger}>` — header hides on scroll down, appears on scroll up
- **Structure:** Single toolbar row with `className='w-full bg-fb-blue md:bg-white'`
- **Mobile row contents:**
  - MenuIcon (only on mobile)
  - SmartEnPlus logo text (`text-lg md:text-2xl text-white md:text-gray-600`)
  - CartButton + ProfileButton
- **Nav links:** `hidden md:flex` — desktop only via CSS display toggle
- **Scroll behavior:** Header scrolls with page content (relative positioning), hides via Slide animation

**File:** `components/layout/layout.js` at git HEAD

- Had `<Toolbar />` between `<DynamicMainHeader />` and `<main>` — this created a content spacer

## Current Mobile Header

**File:** `components/layout/main-header.js` (current)

- **AppBar:** `position="fixed"` with `sx={{ top: 0, zIndex: 1100 }}` — fixed on ALL screens
- **Slide wrapper:** NONE
- **Mobile row:** Separate `<div className='w-full bg-fb-blue md:hidden'>` with its own Toolbar
- **Mobile row contents:**
  - MenuIcon
  - SmartEnPlus logo (`text-lg text-white`)
  - CartButton + ProfileButton
- **Desktop row:** Separate `<div className='hidden md:block glass-bg/glass-bg-scrolled'>`
- **Scroll behavior:** Header is always fixed/stationary, does not scroll with content

**File:** `components/layout/layout.js` (current)

- No `<Toolbar />` between header and main — no spacer added

## What Changed for Mobile

| Aspect | Original | Current |
|--------|----------|---------|
| position | relative (default) | fixed |
| Slide animation | Yes — hides on scroll down | No |
| Header structure | Single unified row | Two separate rows (mobile/desktop) |
| Spacer in layout.js | `<Toolbar />` present | No spacer |
| Background | Solid blue on mobile | Solid blue on mobile (unchanged) |
| Logo text | `text-lg md:text-2xl text-white md:text-gray-600` | `text-lg text-white` (white only) |

## Is Mobile Behavior Preserved?

**NO — mobile behavior has fundamentally changed.**

| Behavior | Original | Current | Preserved? |
|----------|----------|---------|------------|
| Header scrolls with content | Yes (relative) | No (fixed) | NO |
| Header hides on scroll down | Yes (Slide) | No | NO |
| Header visible at top of page | Yes | Yes (but always visible, not just on scroll up) | PARTIAL |
| Fixed/stationary header | No | Yes | NEW |
| Logo + actions in one row | Yes | Yes | YES |

The original mobile header was **dynamic** — it scrolled with page content and used a Slide animation to hide/show based on scroll direction. The current mobile header is **permanently fixed** at the top of the viewport with no scroll-related behavior.

## Issues Found

1. **Fixed header without spacer breaks content layout** — Original had `<Toolbar />` in `layout.js` to create a top spacer equal to header height. This was removed. Content now scrolls under the fixed header on mobile.

2. **Scroll-hide behavior removed** — Users who relied on the header hiding on scroll down (to see more content) now have a permanently visible header consuming viewport space.

3. **Desktop/mobile code paths diverged significantly** — The original had a single row that adapted via CSS (`md:hidden`, `md:bg-white`). Now there are two completely separate DOM structures. This increases maintenance burden and could cause inconsistencies.

4. **Missing spacer compensation** — With `position="fixed"` on mobile but no spacer in `layout.js`, the first content element will be partially obscured by the header on page load/navigation.

## Hero Section (homepagev2.js)

Both original and current use the same `FeaturedImageHeader` with defaults:
- `customMinHeight` prop not passed — defaults to `min-h-[200px] sm:min-h-[250px] md:min-h-[460px]`
- No `customMinHeight="min-h-[500px] md:min-h-[460px]"` found in either version

The hero section height is unchanged between original and current.
