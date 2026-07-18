# Hero Overlay — Back + Share Buttons

## Summary
Hero image with floating action buttons (back + share) that sit above the image without trapping clicks on the image itself.

## Context
Locations (#252) + Destinations (#251) redesigns both need a back button + share popover floating over a full-bleed hero image. Naive `absolute top-2 right-2` works but blocks hero CTA clicks.

## Problem
Putting `position: absolute` buttons directly on a hero eats pointer events — clicks on the image (e.g. for a video play CTA, or accidental taps) hit the buttons instead.

## Decision — Two-layer overlay pattern

```jsx
<div className="relative">                              {/* hero container */}
  <div className="absolute top-2 left-0 right-0 w-full z-40 pointer-events-none">
    <div className="max-w-[1200px] mx-auto flex flex-row justify-between items-center px-3 pointer-events-auto">
      <button aria-label="Go back" className="w-11 h-11 ..." onClick={() => router.back()}>
        <ArrowBackIosNewOutlinedIcon />
      </button>
      <ShareButton />                                    {/* dynamic-imported, ssr:false */}
    </div>
  </div>
  <FeaturedImageHeader title="..." imgUrl={bgDefault}>
    {/* hero content */}
  </FeaturedImageHeader>
</div>
```

Key moves:
- **Outer overlay row: `pointer-events-none`** — clicks pass through to hero.
- **Inner content row: `pointer-events-auto`** — buttons receive clicks.
- **`z-40`** — above image but below modals/dropdowns (z-50).
- **`max-w-[1200px] mx-auto`** — caps width to design-token container even on ultra-wide screens.
- **`w-11 h-11` (44px)** — meets touch-target token. Don't shrink to 36px for these.
- **`bg-white/80 backdrop-blur-md`** — readable on any hero photo without obscuring too much.
- **`ShareButton` dynamically imported, `ssr: false`** — popover uses `window`/`document`, breaks SSR.

## Tradeoffs
- One extra DOM node per overlay. Negligible.
- `router.back()` skips to previous route — bad on SEO entry (deep link from Google). Acceptable for now; flag for audit.

## Consequences
- Reusable as `<HeroOverlayActions back share />` component when 3rd page adopts. Keep fork until then.
- Standardises the 44px white-blur floating button language across the site.

## Related
- [[destinations-page-redesign]] — first use
- [[locations-page-redesign]] — second use (#252)
- `pages/destinations/index.js` · `pages/locations/index.js` · `components/UI/ShareButton.js`
