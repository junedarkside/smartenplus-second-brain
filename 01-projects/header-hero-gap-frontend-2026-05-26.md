# Header-Hero Gap — Frontend Analysis

## Layout Structure

```
layout.js
└── <AppBar position={fixed|sticky} zIndex=1100>  ← MainHeader
└── <main id="main-content" pt-[88px?|gap-2>     ← when isHomepage: no pt-[88px], else pt-[88px]
    └── FeaturedImageHeader ("/") or FeaturedImageHeader ("/destinations")
        └── <header class="relative min-h-[200px]...">  ← Featured HERO CONTAINER
            └── <div class="absolute inset-0|max-w..."> ← Absolutely positioned IMAGE wrapper
                └── <Image fill objectFit="cover" />
            └── <div class="absolute top-1/2...">       ← children passed by page (HERO CONTENT)
```

## CSS Positioning Breakdown

### MainHeader (`main-header.js`)
| Property | Homepage | Non-Homepage |
|----------|----------|--------------|
| `position` | `fixed` | `sticky` |
| `zIndex` | `1100` | `1100` |
| `top` | `0` (implicit) | `0` (implicit) |
| Effect | Removed from document flow, overlays content | Removed from document flow? NO! `sticky` still takes space via `top: 0` |

### Main Element (`layout.js` line 230)
| Property | Homepage | Non-Homepage |
|----------|----------|--------------|
| Class | `mx-auto w-full flex-grow no-scrollbar` | `mx-auto w-full flex-grow no-scrollbar pt-[88px]` |
| `pt-[88px]` | NO | YES |
| Effect | Content starts below header via hero `pt-[88px]` | Content pushed down 88px by padding-top |

### FeaturedImageHeader (`FeaturedImageHeader.js`)
| Property | Value |
|----------|-------|
| Container `<header>` | `relative min-h-[200px] sm:min-h-[250px] md:min-h-[460px]` |
| Inner image wrapper | `absolute inset-0` (cinematic) OR `max-w-[1200px] mx-auto w-full min-h-[...]` (non-cinematic) |
| Image | `fill` + `objectFit: cover` — fills parent absolutely |
| Gradient overlay | `absolute top-0 left-0 w-full h-full hero-top-gradient` |
| Back button | `absolute top-0 left-0 right-0 z-30` |
| **Children (hero content)** | **Rendered AFTER image wrapper div** — sibling position, NOT nested inside absolute |

### Hero Content Positioning (from pages)

**Homepage (`homepagev2.js` line 392):**
```jsx
<div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full z-20 pt-[88px]">
```
- `pt-[88px]` = 88px padding-top pushes hero CONTENT (search box) below the FIXED header height

**Destinations (`destinations/index.js` line 83):**
```jsx
<div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full z-20">
```
- NO `pt-[88px]` — but `transform -translate-y-1/2` centers vertically in available space

## The Gap — Technical Explanation

**The gap is 88px and it lives ABOVE the hero image, NOT inside it.**

The root mechanism:

1. `MainHeader` on non-homepage uses `position="sticky"` with `top: 0`
2. `sticky` is NOT `fixed` — it REMOVES the header from document flow AND then pins it at `top: 0`. The key difference: **sticky creates a block that Reserve space in the document flow before it sticks.**
3. `layout.js` line 230 applies `pt-[88px]` (88px padding-top) to the `<main>` element on non-homepage pages
4. The `<main>` element's padding creates space ABOVE the hero container
5. But `FeaturedImageHeader` uses `position: relative` on its `<header>` container — it is INSIDE the main element and subject to main's padding

**Visual stack on non-homepage:**
```
Viewport
└── [sticky header pinned at top — 0px from top of viewport, zIndex 1100]
└── [Gap — white space — 88px from pt-[88px] on <main>]
└── [Hero image starts at 88px — 88px from top of viewport]
```

**Visual stack on homepage:**
```
Viewport
└── [fixed header overlaid at top — 0px from top, zIndex 1100]
└── [Hero image starts at 0px from top of viewport — NO gap]
    └── [Hero content has pt-[88px] → search box pushed below header]
```

## Root Cause

**Double-offset created by `sticky` + `pt-[88px]` on non-homepage:**

| Element | Homepage | Non-Homepage |
|---------|----------|--------------|
| Header position | `fixed` (overlays, no scroll-space) | `sticky` (takes scroll-space via `top: 0`) |
| Main padding-top | `gap-2` only (tiny) | `pt-[88px]` pushes all content down 88px |
| Hero image start | `0px` from viewport top | `88px` from viewport top |

On homepage: `fixed` header doesn't reserve document space → hero starts at `0px`
On non-homepage: `sticky` header reserves document space via `top: 0` sticky positioning → then `pt-[88px]` on `<main>` ADDS ANOTHER 88px → double 88px gap

**Why `sticky` reserves space:** `position: sticky` with `top: 0` does two things:
1. Keeps the element in normal document flow (it reserve space)
2. When scrolled past, pins at `top: 0`

Combined with `pt-[88px]` on `<main>`, you get 88px (sticky space) + 88px (padding) = 176px equivalent offset, but visually the sticky header covers 88px of it, leaving **88px white gap between header bottom and hero top.**

## Fix Options

### Option 1: Remove `pt-[88px]` from `<main>` on non-homepage
**Change `layout.js` line 230:**
```jsx
// Current:
className={`mx-auto w-full flex-grow no-scrollbar${isHomepage ? '' : ' pt-[88px]'}`}

// Proposed:
className={`mx-auto w-full flex-grow no-scrollbar ${isHomepage ? '' : 'pt-[calc(88px+8px)]'}`}
// or just remove entirely and let hero handle its own offset
```
**Tradeoffs:**
- `pt-[88px]` was likely added to prevent content from hiding UNDER the sticky header when scrolling
- Removing it means content starts immediately after sticky header without buffer
- Hero section would need its own `pt-[88px]` if the padding is meaningful for other content

### Option 2: Add `pt-[88px]` to hero content div on non-homepage pages
Keep `pt-[88px]` on `<main>` but compensate on hero pages themselves (invert the offset).

**Tradeoffs:**
- Requires changing every non-homepage page that uses `FeaturedImageHeader`
- Fragile — new pages will forget to add it
- Asymmetric: homepage hero content has `pt-[88px]`, non-homepage hero content doesn't (88px difference)

### Option 3: Make non-homepage header `position="fixed"` like homepage
**Change `main-header.js` line 40:**
```jsx
position={isHomepage ? 'fixed' : 'fixed'}  // Always fixed
```
This would align behavior but might break UX (sticky header intention was to keep nav visible when scrolling down長い pages).

**Tradeoffs:**
- Users lose sticky nav on non-homepage pages
- Would need to test all non-homepage pages
- Best fix if sticky behavior isn't needed on destination/help/blog pages

### Option 4: Adjust hero container margin instead of main padding
Instead of `pt-[88px]` on main, add `mt-[88px]` to hero or adjust the flex gap.

**Tradeoffs:**
- Changes layout structure
- Might affect other components inside `<main>`

### Recommended Fix
**Option 1 (remove `pt-[88px]` from main)** is the cleanest because:
- The 88px offset on `<main>` was a hack — hero should self-handle its spacing from sticky header
- Hero content (the SearchBox) already has `pt-[88px]` on homepage to clear the fixed header
- On non-homepage, if hero content needs clearance from sticky header, add `pt-[88px]` to the hero content div itself (not the main container)
- This makes the spacing intentional and component-local rather than global
