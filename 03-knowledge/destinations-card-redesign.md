# Destinations Card Redesign — Text Below Image

## Summary
Redesigned "Thailand's Top Destinations" homepage section from asymmetric overlay-text cards to equal 5-col card grid with location name + tag below the image.

## Context
Session #146 shipped Travel Guide section as equal 3-col card grid with text below image. Session #147 extended same pattern to Destinations section. Both sections now share the same visual language.

## Problem
Previous design: full-bleed image with white text overlay. Issues:
- Low contrast on bright/washed-out images
- Asymmetric FeaturedCard/SupportingCard layout created implicit hierarchy not meaningful to users
- Overlay text hard to read; no secondary info visible

## Decision
**Equal 5-col grid, text below image** — drop FeaturedCard/SupportingCard asymmetry entirely.

## Details

### Files changed
| File | Change |
|------|--------|
| `lib/homepage/components/DestinationsEditorialGrid.js` | Replaced FeaturedCard + SupportingCard + asymmetric grid → single `DestinationCard` × 5-col equal grid |
| `lib/homepage/components/DestinationsCarousel.js` | Rewrote `DestinationSlideCard` — removed overlay pattern, text below image |
| `lib/homepage/components/LocationsSkeletonLoader.js` | Updated desktop skeleton to match 5-col equal grid |

### Card structure
```
article (rounded-xl, bg-white, shadow-[0_4px_16px])
  Link (block, group, wraps full card)
    div (relative, aspect-[4/3], overflow-hidden)   ← image container
      Image (fill, object-cover, hover:scale-105)
    div (p-3, flex-col, gap-1)                      ← text block
      span.font-semibold.text-gray-900              ← location name (itemProp="name")
      span.text-xs.text-gray-500                    ← badge text
```

### Badge text strategy
`badgeText` resolved in `processedItems` useMemo:
1. `DESTINATION_COPY[slug]?.tag` — editorial label for 13 known locations (e.g. "Island Gateway")
2. Fallback: `"${route_count} routes"` for unknown slugs
3. Null if no route_count → renders nothing

`DESTINATION_COPY` at `lib/homepage/data/destinationCopy.js` — 13 entries. Review quarterly.

### Grid layout
- Desktop `lg+`: `grid-cols-5 gap-4` (was `[grid-template-columns:2fr_1fr]`)
- Mobile `<lg`: Embla swipe carousel via `CardCarouselContainer`, unchanged

### Image
- `aspect-[4/3]` — slightly taller than 16:9, suits portrait-heavy destination photography
- `priority` only on index 0 (Bangkok, highest route_count — API returns ordered by `-route_count`)
- `hover:scale-105 transition-transform duration-300` — subtle zoom on hover

## Tradeoffs
| Kept | Dropped |
|------|---------|
| `role="list"` + `role="listitem"` | Dark gradient overlay div |
| `itemScope/itemType schema.org/TouristDestination` | FeaturedCard + SupportingCard components |
| GTM `destination_click` tracking | Asymmetric `2fr/1fr` editorial grid |
| `isFeatured: index === 0` in processedItems | `absolute inset-0` link pattern |
| Router prefetch on hover | White overlay text |

## Consequences
- Text always legible regardless of image brightness
- Simpler component tree — one card component instead of three
- Skeleton loader matches new layout — no layout shift
- Extensible: `badgeText` slot can show rating, price range, or other data later

## Related
- [[TravelThailandBetterSection]] — Travel Guide section (same pattern, shipped session #146)
- [[destinations-section-homepage]] — parent `LocationsSection.js`
- `lib/homepage/data/destinationCopy.js` — editorial copy source
