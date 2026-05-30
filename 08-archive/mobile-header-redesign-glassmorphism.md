# Mobile Header Redesign — Glassmorphism Premium Travel

## Summary
Redesign SmartEnPlus mobile header from solid `bg-fb-blue` (#3b5998) bar to cinematic glassmorphism overlay that blends into homepage hero image.

## Context
Current mobile header is a solid Facebook-blue opaque bar. Premium travel platforms (Airbnb, Apple Travel) use translucent glassmorphism overlays that merge with hero imagery. Target: modern 2026 travel app aesthetic — immersive, premium, cinematic. Not yet implemented; this doc is the design spec + implementation plan.

## Current State (as of 2026-05-27)

**File:** `components/layout/main-header.js` lines 44–77

**Mobile AppBar (search inactive):**
- `position: relative` + MUI `Slide` animation (hide on scroll down)
- Background: `bg-fb-blue` — solid #3b5998
- Logo text: `font-bold text-lg text-white`
- Icons: CartButton + ProfileButton — `text-white/70 hover:text-white`, size 24×24

**Mobile AppBar (search active):**
- `position: fixed` + spacer div `h-[56px]`
- Background: `w-full bg-fb-blue` — still solid blue

**Hero integration:**
- Homepage (`pages/homepagev2.js`) hero renders BELOW relative header
- FeaturedImageHeader uses `md:-mt-[96px]` — overlap only on desktop, none on mobile
- Layout main: `md:pt-[96px]` padding on desktop only

**Existing glass CSS classes (`styles/globals.css` ~line 760):**
```css
.glass-header        { gradient rgba(0,0,0,0.50)→0.25; blur(8px);  transition 300ms }
.glass-header-scrolled { gradient rgba(0,0,0,0.75)→0.45; blur(16px) }
.glass-bg            { gradient rgba(0,0,0,0.28)→0.12; transition 200ms }
.glass-bg-scrolled   { gradient rgba(0,0,0,0.65)→0.40; transition 200ms }  ← desktop uses this
.hero-top-gradient   { gradient rgba(0,0,0,0.50)→0.20→transparent }
```
Desktop uses `.glass-bg-scrolled`. Mobile uses none — no glass at all.

## Target Design

### Visual Spec

| Property | Value |
|----------|-------|
| Background (at top) | `linear-gradient(to bottom, rgba(0,0,0,0.42), rgba(0,0,0,0.18))` |
| Background (scrolled) | `linear-gradient(to bottom, rgba(0,0,0,0.65), rgba(0,0,0,0.40))` |
| Backdrop filter | `blur(10px)` / `blur(16px)` scrolled |
| Height | 56px (MUI Toolbar default) |
| Position | `fixed` always |
| Text/logo color | `rgba(255,255,255,0.92)` |
| Icon color | `rgba(255,255,255,0.88)` — matches existing `text-white/70→text-white` hover |

### Layout
```
[ ☰ ]  [ ◆ SmartEnPlus ]           [ THB  🛒  👤 ]
  menu    logo                        currency cart profile
```
Currency selector added to mobile right side (currently missing from mobile layout).

### Currency Pill — Mobile Variant
Current desktop: `text-fb-blue bg-blue-200 text-xs px-2 py-1 rounded-md max-w-[40px]`
Target mobile: frosted glass pill — `text-white/90 text-xs font-semibold px-2 py-1 rounded-full border border-white/20 bg-white/10`

### Cart + Profile Icons
Keep: `text-white/70 hover:text-white` — already correct for glass aesthetic.

### Scroll Behavior
Reuse existing `useScrollTrigger` (already imported):
- `mobileTrigger === false` (at top) → `.glass-header-mobile`
- `mobileTrigger === true` (scrolled) → `.glass-header-mobile-scrolled`

### New CSS Classes Needed
```css
/* Add to globals.css alongside existing glass-* classes */
.glass-header-mobile {
  background: linear-gradient(to bottom, rgba(0,0,0,0.42), rgba(0,0,0,0.18));
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: background 300ms ease, backdrop-filter 300ms ease;
}
.glass-header-mobile-scrolled {
  background: linear-gradient(to bottom, rgba(0,0,0,0.65), rgba(0,0,0,0.40));
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  transition: background 300ms ease, backdrop-filter 300ms ease;
}
```

## Hero Integration Change

For glass to work visually, mobile header must be `position: fixed` and hero image must render BEHIND it.

**Recommended approach — always-fixed:**
1. Remove `Slide` animation's `position: relative` — switch to `position: fixed` always on mobile
2. Always render spacer `h-[56px]` on mobile (not just when `searchBarContent` exists)
3. Homepage hero: add `-mt-[56px]` negative margin on mobile hero wrapper so hero bleeds behind fixed header
4. Hero text content: add `pt-[56px]` padding inside hero so text not obscured

**Why always-fixed:** consistent behavior, no layout shift on Slide, simpler state logic. Non-homepage pages (routes, trips) get a fixed glass header over their content — cleaner than position:relative with scroll hide.

**Slide animation fate:** remove from normal mobile header. Keep only the scroll-triggered opacity/blur transition via class toggle.

## Files to Touch

| File | Change |
|------|--------|
| `components/layout/main-header.js` | Mobile AppBar: `bg-fb-blue` → `glass-header-mobile`/`glass-header-mobile-scrolled`, always fixed, always spacer, add CurrencySelector to mobile right |
| `styles/globals.css` | Add `.glass-header-mobile` + `.glass-header-mobile-scrolled` |
| `components/UI/CurrencySelector.js` | Add mobile glass pill variant via `variant="glass"` or `mobile` prop |
| `pages/homepagev2.js` or hero wrapper | Add `-mt-[56px]` on mobile hero so image extends behind fixed glass header |

## Constraints

- `useScrollTrigger` already imported in main-header.js — reuse, don't add new scroll listener
- Mobile breakpoint: `md` (768px) — `md:hidden` on mobile AppBar must stay
- Must not break search-active mode — fixed + spacer pattern already correct, only color changes
- MUI AppBar `elevation={0}` stays — no shadow
- CurrencySelector desktop pill (`text-fb-blue bg-blue-200`) must stay untouched for desktop; mobile gets glass variant only
- Do NOT change CartButton or ProfileButton internals
- Do NOT touch desktop header (already glass-bg-scrolled, working)

## What NOT to Do

- No solid-color backgrounds (`bg-fb-blue`, `bg-white`, `bg-black`)
- No box-shadow, no border on header bar
- No heavy opaque overlays (no rgba > 0.70 at top state)
- No extra nav items in mobile — menu icon handles nav
- No new scroll listeners — `useScrollTrigger` already handles it
- No MUI AppBar replacement — styling change only

## Verification

1. `npm run dev` → DevTools mobile emulation at 375px
2. Homepage: hero image visible through header (glass effect working)
3. Scroll down → header darkens, blur increases
4. Scroll to top → header lightens
5. Non-homepage pages (e.g. `/routes`) → glass header readable over page background
6. Tap cart/profile → modal/drawer opens correctly
7. Search active state → search bar renders, glass background maintained
8. Tap currency → selector opens correctly

## Related

- `main-header.js` mobile branch: lines 44–77
- Existing glass CSS: `styles/globals.css` ~line 760
- Desktop glass: `glass-bg-scrolled` on AppBar inner div (working)
- Desktop hero overlap: `md:-mt-[96px]` in `components/UI/FeaturedImageHeader.js`
- [[smartenplus-glassmorphism-header]] — earlier desktop glass plan (2026-05-25)
