# Premium Glassmorphism Header — Design Report

**Status:** Finalized 2026-05-25
**Team:** glass-auditor + hero-reviewer + scroll-specialist

---

## Design Decision: Option A — Unified Glass

Both Row 1 (logo+utilities) and Row 2 (nav) share identical glassmorphism treatment. Single dark gradient layer, no divider needed. Header feels like "one integrated navigation system."

---

## Gap Analysis: Current vs. Glassmorphism

| Element | Current (header-ux-v1) | Glassmorphism Target |
|---------|----------------------|---------------------|
| Background | `bg-fb-blue md:bg-white` solid | Dark gradient `from-black/60 to-black/30` + `backdrop-blur-md` |
| Border | `border-b border-gray-200` | `border-b border-white/10` (subtle) |
| Row 1 text | `text-white md:text-gray-600` | `text-white` always |
| Row 2 nav text | `text-gray-600 border-gray-300` | `text-white/80 hover:text-white border-transparent` |
| Hero visibility | Solid — hero blocked | Hero visible through glass |
| Scroll behavior | Slide (hide/show) | Sticky + blur/opacity shift |

---

## Technical Implementation

### 1. CSS Changes (main-header.js)

Replace white bg wrapper with glass, remove Divider (unified glass):
```jsx
// NEW — unified glass, NO divider
<div className='hidden md:block w-full bg-gradient-to-b from-black/60 to-black/30 backdrop-blur-md border-b border-white/10'>
  <Toolbar>Row 1</Toolbar>
  <Toolbar>Row 2</Toolbar>  {/* both in same glass container */}
</div>
```

Mobile stays: `bg-fb-blue` (brand blue, solid)

### 2. Typography Overhaul

Row 1: `text-white` (logo + utility icons)
Row 2 nav links:
- Default: `text-white/80`
- Hover: `text-white`
- Active: `text-white border-white`

### 3. Hero Section Changes

`FeaturedImageHeader.js` line 136: reduce `opacity-20` → `opacity-10`
`SearchCover.js`: same treatment

### 4. Scroll Behavior — New Pattern (Not Slide)

Remove Slide. Use `position: sticky` on AppBar + threshold-based `isScrolled` state via `useScrollTrigger`. CSS transitions handle blur/opacity interpolation.

---

## Files to Modify

| File | Change |
|------|--------|
| `components/layout/main-header.js` | Glassmorphism bg, white typography, sticky wrapper |
| `components/UI/FeaturedImageHeader.js` | Reduce hero overlay opacity |
| `components/UI/SearchCover.js` | Reduce hero overlay opacity |

## Implementation Priority

**Phase 1 (core):** Glass bg + white typography + hero overlay reduction
**Phase 2 (scroll):** Sticky + blur transition
**Phase 3 (polish):** Height compression (optional)

---

## Technical Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Dropdown z-index stacking | Medium | Test early, add `isolation: isolate` if needed |
| backdrop-filter performance jank | Low | CSS transitions + `will-change` only on change |
| Slide → sticky migration breaks other pages | Medium | Keep Slide for non-hero pages, sticky only for homepage |

---

## Verification

- [ ] Desktop: header floats over hero, hero visible through glass
- [ ] Desktop: both rows unified glass, no divider
- [ ] Desktop: nav text white, readable on dark glass
- [ ] Desktop: scroll → sticky + blur intensifies
- [ ] Mobile: solid blue header, hamburger menu works
- [ ] Dropdowns: stack correctly above glass
- [ ] Lint passes

---

## Out of Scope (v2)

- Mobile glassmorphism
- Submenu dropdowns
- Language selector
- Height compression on scroll

---

---

## Implementation Reality — 2026-05-25

### What was built vs planned

| Aspect | Planned | Actual |
|--------|---------|--------|
| Header position | `sticky` everywhere | `fixed` on homepage, `sticky` on all other routes |
| Hero height | unchanged | `min-h-screen` on homepage (`customMinHeight` prop) |
| Hero overlay | reduce `opacity-10` | replaced flat opacity div with `.hero-top-gradient` CSS class (gradient top-to-transparent) |
| Back/share controls | unchanged | hidden via `isCinematic` prop — `FeaturedImageHeader` suppresses controls when true |
| Hero image container | `max-w-[1200px]` always | `inset-0` (full-bleed) when `isCinematic`, constrained otherwise |
| Icon colors | planned `text-white` | `text-white/70 hover:text-white` matching nav inactive state |
| Image sizes | `80vw` cap at >768px | `100vw` always — correct for full-viewport cinematic |
| Double-glass bug | not in plan | fixed: `AppBar` had `glass-header` class + inner div had `glass-bg` → double opacity stack. Removed class from AppBar, set `MuiAppBar-root { background-color: transparent }` |

### Key CSS added (`styles/globals.css`)

```css
.hero-top-gradient {
  background: linear-gradient(to bottom, rgba(0,0,0,0.50) 0%, rgba(0,0,0,0.20) 35%, transparent 65%);
  pointer-events: none;
}

/* glass-bg lightened — single layer now */
.glass-bg {
  background: linear-gradient(to bottom, rgba(0,0,0,0.28), rgba(0,0,0,0.12));
}
.glass-bg-scrolled {
  background: linear-gradient(to bottom, rgba(0,0,0,0.65), rgba(0,0,0,0.40));
}
```

### Key prop added to `FeaturedImageHeader`

`isCinematic` (bool, default undefined/falsy):
- `true` → full-bleed `inset-0` image container, no back/share controls, no `lg:rounded-b-lg`
- falsy → original constrained behavior (trip detail pages unaffected)

### Layout offset pattern (`layout.js`)

```jsx
<main className={`...${isHomepage ? '' : ' pt-[88px]'}`}>
```
Homepage needs no offset (hero fills viewport). All other pages need `pt-[88px]` to clear fixed header.

See [[nextjs-fixed-header-per-route]] for reusable atomic pattern.

### Admin help text (`smartenplus-backend/pages_info/admin.py`)

`HeroBannerAdmin` now has fieldsets with upload spec warning:
- Minimum 1920×1080px · Ideal 2560×1440px · WebP preferred · Max 10MB · Landscape only

No migration needed (admin UI only).

---

## Related Docs

- [[smartenplus-header-ux-v1]] — prior header-ux-v1 (white bg, 2-row layout) — superseded by this
- [[nav-config-research]] — prior nav UX research
- [[hero-banner-cms]] — hero management
- [[nextjs-fixed-header-per-route]] — atomic pattern: fixed header on homepage, sticky elsewhere