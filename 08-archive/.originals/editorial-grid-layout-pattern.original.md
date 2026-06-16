# Editorial Grid Layout Pattern

## Summary
Asymmetric 2fr 1fr CSS grid for featured destination cards. Desktop uses CSS grid with row-span. Mobile/tablet uses CardCarouselContainer. Border radius token: `rounded-xl` (12px) as `imageCard`.

## Context
`destinations-redesign-review.md` (2026-05-29). 3-agent review + scrutiny pass. Destinations section redesign from uniform grid to editorial layout.

## Problem
- All7 cards identical size/weight — no visual hierarchy
- `(N trips)` supply count not emotionally useful
- "Explore More..." occupies full grid cell — wastes space
- Uniform grid feels like sitemap

## Decision

### Asymmetric Desktop Grid (`lg+`)
```
grid-template-columns: 2fr 1fr
gap-3

FeaturedCard (items[0]):      row-span-2, min-h-[320px]
SupportingCard[1] (items[1]): col-start-2 row-start-1, min-h-[152px]
SupportingCard[2] (items[2]): col-start-2 row-start-2, min-h-[152px]
Sub-row div:                   col-span-2 grid grid-cols-2 gap-3
  SupportingCard[3] (items[3]): min-h-[180px]
  SupportingCard[4] (items[4]): min-h-[180px]
```

### Mobile Carousel
Reuse `CardCarouselContainer` via `DestinationsCarousel.js` wrapper:
- `desktopMode="carousel"`, `carouselBreakpoint="lg"`
- Do NOT wrap in `lg:hidden` div — `CardCarouselContainer` handles breakpoint internally
- `renderCard={(item) => <SupportingCard item={item} />}`
- Slide wrapper: `min-w-[220px] sm:min-w-[280px] h-[200px]`

### Border Radius: `rounded-xl` (12px)
Token added to `BORDER_RADIUS_CLASSES` as `imageCard: 'rounded-xl'`.

**Rationale:** `rounded-2xl` (16px) rejected. Codebase already has drift: `DiscoverySection.js` uses `rounded-xl`. Current LocationGridComponent cards use bare `rounded` (4px), not `rounded-md` (6px). Token addition fills a gap.

### Skip ContentCard
For photo-led editorial sections, ContentCard constraints are wrong:
- `bg-white` irrelevant (photography fills cards)
- `overflow-hidden` should clip individual card images, not section wrapper
- `flex-col` blocks asymmetric CSS grid

Use `Section` + local grid div directly. Same pattern as `PopularRoutesSection`.

## Details

### FeaturedCard Structure
```jsx
<article className="rounded-xl overflow-hidden relative group">
  <Image fill object-cover priority sizes="(max-width: 768px) 100vw, 66vw" />
  <div className="absolute inset-0 bg-black/25 transition-opacity duration-200 group-hover:bg-black/10" />
  <div className="absolute bottom-0 left-0 right-0 p-4">
    <span className="inline-block mb-2 px-2 py-0.5 text-xs font-medium bg-white/20 text-white rounded">
      {copy?.tag}
    </span>
    <h3 className="text-xl font-bold text-white"> {capitalizedLocation}</h3>
  </div>
  <Link aria-label={`View trips to ${capitalizedLocation}, ${routeCount} routes available`} />
</article>
```

### destinationCopy.js
```js
const DESTINATION_COPY = {
  'bangkok':    { tag: 'Bus & Train Hub',    context: "..." },
  'phuket':     { tag: 'Island Gateway',     context: '...' },
  'koh-samui':  { tag: 'Gulf Island',        context: '...' },
  'chiang-mai': { tag: 'Northern Capital',   context: '...' },
  // ...
};
```

### GTM Events
```js
// destination_click — on card click
{ destination_name, destination_slug, destination_position, is_featured, route_count }

// destinations_see_all_click — on "See all" link
{ category: 'destinations_section', section_title }
```

## Tradeoffs
- `carouselBreakpoint="lg"` (1024px) chosen over `md` (768px) — asymmetric grid too cramped at tablet size
- ISR: featured card (`index === 0`) may go stale — acceptable, negotiate `featured: boolean` with backend
- WCAG contrast: `bg-black/25` white text may fail 4.5:1 on light images — test and increase to `bg-black/35` if needed

## Consequences
- Visual hierarchy now explicit — featured card dominates
- Mobile carousel preserves horizontal scroll UX
- Editorial copy via `destinationCopy.js` — quarterly review cadence, not code

## Related
- [[design-systems]] — token-based design system
- [[section-contentcard-wrapper-pattern]] — when to skip ContentCard
- [[carousel-design-standard]] — Embla carousel usage
