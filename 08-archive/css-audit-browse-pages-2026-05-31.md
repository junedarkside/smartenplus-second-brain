# CSS Audit — Browse Pages Consistency (Destinations/Locations/Trips/Activities)

## Summary
**COMPLETED 2026-05-31.** Post-blog consistency update (commit 315cc2e), 4 browse pages audited + fixed against homepage, trip detail, blog reference patterns. 13 commits on branch `260528-feat/header-redesign-2026`.

## What Was Fixed
- Card border-radius: `rounded-xl` (12px) on all browse cards
- Card padding: `p-4` (16px) on LocationCard, DayTripCard
- Grid gaps: `gap-4 md:gap-6` (16-24px) on all browse grids
- Section padding: `py-6 px-4 xl:px-0` on trips, locations, destinations
- Card bg: `bg-white` on trips cards (vs transparent page)
- LocationCard station items: `rounded-md` (per design system)
- Back/share overlay: added to `/trips` matching `/locations` pattern
- Removed redundant inner `mx-` margins (section `px-4` sufficient)
- Removed grid `p-2` padding (cards self-pad with `p-4`)
- designSystem.js: documented `rounded-xl` vs `rounded-md` token usage

## Pages Audited
- `/destinations` — LocationCard component
- `/locations` — LocationGridComponent
- `/trips` — Trips browse page
- `/activities?category=DAY_TOUR` — DayTripList/DayTripCard

## Reference Canonical Patterns
| Element | Value |
|---------|-------|
| Card border-radius (image cards) | `rounded-xl` (12px) — `BORDER_RADIUS.imageCard` |
| Card border-radius (editorial cards) | `rounded-md` (6px) — `BORDER_RADIUS.container` |
| Card padding | `p-4` (16px) |
| Grid gap | `gap-4 md:gap-6` (16px → 24px) |
| Section padding | `py-6 px-4 xl:px-0` (24px vertical) |
| Card margins | `mx-2 md:mx-3 xl:mx-0` |

## Inconsistencies Found

### HIGH Priority

**1. Card Border-Radius — 4 different values across pages**
| Page | Current | Expected |
|------|---------|----------|
| Homepage PopularRoutes | `rounded-xl` (12px) ✓ | 12px |
| Activities browse | `rounded-md` (6px) | 12px |
| Trips browse | `rounded` (4px) | 12px |
| Locations browse | `rounded-xl` (12px) ✓ | 12px |
| Destinations | `rounded-none sm:rounded-md` (0→6px) | 12px |

**2. Card Padding — too small on destinations/activities**
| Component | Current | Expected |
|-----------|---------|----------|
| LocationCard | `p-2 sm:p-6` (8px→24px) | `p-4` (16px) |
| DayTripCard | `sx={{ px: 2, pt: 2, pb: 2 }}` (8px) | `p-3` min |
| TripsCard | `p-4` (16px) ✓ | `p-4` |

**3. Grid Gaps — too tight on browse pages**
| Page | Current | Reference |
|------|---------|-----------|
| Destinations | `gap-2 sm:gap-3` (8→12px) | `gap-4 md:gap-6` |
| Locations | `gap-2` (8px) | `gap-4 md:gap-6` |
| Activities | `spacing={1}` (4px MUI) | `gap-4 md:gap-6` |
| Trips | `gap-2` (8px) | `gap-4 md:gap-6` |

### MEDIUM Priority

**4. Section top padding — detail page 0px**
- `/activities/detail/`: `pt-0` vs homepage `py-6` (24px)
- Detail pages use inline div instead of `<Section>` component

**5. Card background — destinations glassmorphism**
- LocationCard: `bg-white/80 backdrop-blur-sm` vs blog `bg-white`

**6. Button border-radius**
- LocationCard Book button: `rounded-lg` (8px) vs design system `rounded-md` (6px)

### LOW Priority

**7. Image heights** — Homepage 200px vs Activities browse 180px
**8. Mobile border-radius 0px** — LocationCard `rounded-none` on mobile

## Files to Fix

| File | Changes |
|------|---------|
| `components/destinations/LocationCard.js` | `p-4`, `rounded-xl`, `bg-white`, book button `rounded-md` |
| `components/locations/LocationGridComponent.js` | `gap-4 md:gap-6` |
| `components/UI/DayTripList.js` or DayTripCard | `spacing={2}`, padding increase to `p-3`+ |
| `pages/trips/index.js` | `rounded-xl`, `gap-4 md:gap-6` |
| `pages/activities/detail/[...slug].js` | `py-6` section wrapper |
| `helpers/designSystem.js` | Document `rounded-xl` vs `rounded-md` usage rule |

## Design Token Debate

designSystem.js has two valid border-radius tokens:
- `BORDER_RADIUS.container`: `6px` (rounded-md) — text-heavy cards
- `BORDER_RADIUS.imageCard`: `12px` (rounded-xl) — image-forward browse cards

**Decision:** Browse grid cards (destinations/locations/trips/activities) = image-forward → use `rounded-xl` (12px). Blog editorial cards = text-heavy → `rounded-md` (6px). Update designSystem.js to document this.

## Related
[[blog-seo-performance]] — blog consistency commit 315cc2e
[[design-systems]] — token-based design system
[[section-contentcard-wrapper-pattern]] — Section component usage
[[carousel-design-standard]] — card styling rules
