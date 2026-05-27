# Header Redesign 2026 — Design Spec

## Summary
Full replacement of dark glassmorphism header with solid warm-white premium navigation system. "Modern OS for traveling across Thailand." Implementation-ready spec for frontend team.

## Context
Current header (as of 2026-05-27 revert): dark glass overlay (`glass-bg-scrolled`, `glass-header`), white text, 2-row desktop layout. This was designed for cinematic hero photography. The 2026 direction pivots toward operational clarity — Google Flights / Linear / Notion UX philosophy, not tourism aesthetics.

## Decision
Solid `#FFFFFF` single-row header across all breakpoints. No glassmorphism. No blur.

Reference: [[smartenplus-glassmorphism-header]] (deprecated approach), [[mobile-header-redesign-glassmorphism]] (superseded by this spec)

## Design Spec

### Desktop (≥768px)
- Height: 80px
- Background: `#FFFFFF`
- Border: `1px solid rgba(0,0,0,0.06)`
- Shadow: `0 2px 12px rgba(0,0,0,0.03)`
- Layout: `[Logo] | [Nav: Routes · Journeys · Experiences · Guides] | [Currency · Cart · Account]`
- Nav text: inactive `text-gray-500`, active `text-gray-900 border-b-2 border-gray-900`

### Mobile (<768px)
- Height: 56px
- Same solid white surface
- Layout: `[Hamburger] [Logo] | [Currency · Cart · Account]`
- Icons: `text-gray-700`

### StickySearchBar (scroll state on search results)
- White surface, dark text — replaces dark glass
- Route text: `text-gray-900`, badge: `bg-gray-100 border-gray-300 text-gray-600`

### CSS Classes to Add
```css
.solid-header {
  background: #FFFFFF;
  border-bottom: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 2px 12px rgba(0,0,0,0.03);
}
.solid-header-elevated {
  background: #FFFFFF;
  border-bottom: 1px solid rgba(0,0,0,0.08);
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}
```

## Files to Change (5)
| File | Change |
|------|--------|
| `styles/globals.css` | Add `.solid-header`, `.solid-header-elevated` |
| `components/layout/main-header.js` | Single-row 80px, solid bg, dark text, center nav |
| `components/search/StickySearchBar.js` | White surface, dark text/icons |
| `components/layout/layout.js` | `md:pt-[80px]` (was 96px) |
| `pages/homepagev2.js` | Remove `-mt-[56px]` hero bleed |

Also update: `components/search/HeaderSearchSummary.js` — `text-white` → `text-gray-900/500`

## Tradeoffs
- Loses dramatic hero overlap effect (intentional — not a tourism site)
- Gains: WCAG contrast, operational clarity, matches SaaS product UX direction
- Glass classes stay in CSS — hero-top-gradient still uses them

## Implementation Notes
- Design doc also committed to project root: `HEADER_REDESIGN_2026.md`
- Implementation plan was written + validated this session (2026-05-28)
- Reverted accidental implementation — implement intentionally next session

## Related
[[smartenplus-glassmorphism-header]] · [[mobile-header-redesign-glassmorphism]] · [[nav-header-redesign-2026-05-24]]
