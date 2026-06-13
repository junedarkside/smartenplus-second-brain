# Carousel Design Standard

## Summary
Embla-carousel-react items-per-screen breakpoints, gap values, card widths, focus ring handling for SmartEnPlus frontend.

## Context
Popular Routes carousel investigation 2026-05-28. `gridCols={4}` hardcoded → overflow. Cards `flex-none` with fixed px widths → unpredictable items-per-screen. Blue focus ring from browser `box-shadow`, not `outline`.

## Breakpoints

Design system: `xs(0) → sm(640) → md(768) → lg(1024) → xl(1280) → 2xl(1536)`

## Items Per Screen

| Viewport | Width | Items | Peek | Card Width |
|----------|-------|-------|------|------------|
| Mobile <640px | 320-414px | **1** | 25-30% | `w-[80vw]` |
| sm 640px+ | 640px | **2** | 20% | `w-[45vw]` |
| md 768px+ | 768px | **2-3** | 20% | `w-[40vw]` |
| lg 1024px+ | 1024px | **3** | 15% | `w-[30vw]` |
| xl 1280px+ | 1280px+ | **4** | 10% | `w-[25vw]` |

Peek = partial next card visible → signals scrollability.

## Gap Values

Design system spacing:
- Mobile: `gap-3` (12px) — `mr-2 sm:mr-3 last:mr-0`
- Tablet+: `gap-4` (16px) — `mr-3 lg:mr-4 last:mr-0`

## Card Width Strategy

vw-based widths, NOT fixed px. Fixed px breaks viewport adaptation.

```
w-[80vw] sm:w-[45vw] md:w-[40vw] lg:w-[30vw] xl:w-[25vw] max-w-[320px]
```

`max-w-[320px]` caps width on large screens.

Update `sizes` on Next/Image to match:
```
sizes="(max-width: 639px) 80vw, (max-width: 767px) 45vw, (max-width: 1023px) 40vw, 30vw"
```

## Embla Carousel Implementation

### DOM Structure
```
div.relative
  div.overflow-hidden (ref={emblaRef}) ← overflow:hidden + embla ref SAME element
    div.flex (embla scroll container)
      div.flex-none.snap-start (each slide)
  div.absolute.inset-0 (arrows — OUTSIDE viewport, above it)
```

### Embla Config
```js
const [emblaRef, emblaApi] = useEmblaCarousel({
  align: 'start',
  containScroll: 'trimSnaps', // or 'keepSnaps'
  loop: true, // recommended for UX
});
```

### Slide Wrapper
```jsx
<div className="flex-none snap-start mr-3 last:mr-0">
  {renderCard(item, index)}
</div>
```

### Key Rules
- `overflow:hidden` + `ref` MUST be same element
- Buttons MUST be outside `overflow-hidden` — otherwise clipped
- `inset-0` on button wrapper for full-width coverage
- `pointer-events-none` outer, `pointer-events-auto` inner for button targets
- `flex-none` on slides prevents shrinking
- Gap via `mr-N` on slides, NOT `gap-*` on flex container (embla transforms conflict)

## Focus Ring Handling

Browser `focus-visible` uses `box-shadow`, NOT `outline`.

```jsx
<a style={{ outline: 'none', boxShadow: 'none' }}>
```

Inline style required — Tailwind insufficient against browser defaults.

## Mobile Snap (MOB-4)

All Embla carousels in `lib/homepage/components/*Carousel.js` need `align: 'start'` option (already documented above) + container-level `overflow-x: auto` + `scroll-snap-type: x mandatory` for native mobile swipe fallback. Without these, mobile users lose scroll affordance on iOS Safari.

## Related

- [[design-systems]]
- [[popular-routes-carousel-fix-2026-05-28]]
- [[website-audit-full-2026-06-06-overview]] MC3 / MOB-4