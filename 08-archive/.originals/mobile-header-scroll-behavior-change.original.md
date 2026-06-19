# Mobile Header Scroll Behavior Change

## Summary
Mobile header changed from dynamic (scroll-with-content + Slide hide/show animation) to permanently fixed (no scroll behavior). Removed spacer `<Toolbar />` in layout.js. Two separate DOM structures for mobile/desktop diverged from original unified row.

## Context
Original header (`main-header.js` at git HEAD before redesign) had dynamic mobile behavior. Current header (post-redesign) is permanently fixed. This affects content layout, scroll UX, and maintenance.

## What Changed

| Aspect | Original | Current |
|--------|----------|---------|
| `position` | relative (MUI default) | `fixed` |
| Slide animation | Yes — hides on scroll down | No |
| Header structure | Single unified row, CSS-adaptive (`md:hidden`, `md:bg-white`) | Two separate rows (mobile `<div>` + desktop `<div>`) |
| Spacer in layout.js | `<Toolbar />` between header and main | No spacer |
| Logo text | `text-lg md:text-2xl text-white md:text-gray-600` | `text-lg text-white` (mobile) |
| Scroll behavior | Scrolls with content, hides via Slide | Permanently fixed, always visible |

## Issues

1. **Fixed header without spacer breaks content layout** — Original had `<Toolbar />` creating top spacer equal to header height. Removed. Content scrolls under fixed header on mobile.

2. **Scroll-hide behavior removed** — Users who relied on header hiding on scroll down (to see more content) now have permanently visible header consuming viewport space.

3. **Desktop/mobile code paths diverged** — Original: single row adapting via CSS. Current: two completely separate DOM structures. Increases maintenance burden, potential for inconsistencies.

4. **Missing spacer compensation** — `position="fixed"` on mobile + no spacer in layout.js = first content element partially obscured by header on page load.

## Related
- [[hero-section-comprehensive-audit]] — Contains mobile header analysis section
- [[mobile-header-redesign-glassmorphism]] — Glassmorphism redesign spec (SUPERSEDED)
- [[smartenplus-header-ux-v1]] — Desktop 2-row header implementation v1
- [[header-redesign-2026-spec]] — Current header redesign spec
- [[hero-88px-gap-root-cause]] — 88px gap related to header positioning
- [[nextjs-fixed-header-per-route]] — Fixed vs sticky per-page pattern
