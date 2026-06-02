# Activities Sort/Filter UX Pattern

## Summary
State-driven emphasis for peer-action buttons — hierarchy via content/context, not default styling.

## Problem
Initial Filter button design used brand color (`contained`) while Sort used outline. This created false
hierarchy where Sort appeared secondary. Travel UX research (Klook, Booking.com, GetYourGuide) shows
both are equal-frequency controls on listing pages. Users filter frequently and sort occasionally,
but sort access must be equally visible.

## Decision
Both outlined by default. Active state (user has applied filters or changed sort) carries the visual
signal: badge count for filters, active sort label for sort. No solid fill CTA color.

## Pattern

| State | Filter button | Sort button |
|---|---|---|
| Default (no selections) | `[ Filter ]` outlined gray | `[ Sort ]` outlined gray |
| Filters applied | `[ Filter (3) ]` outlined brand + badge | `[ Sort ]` outlined gray unchanged |
| Sort changed from default | `[ Filter ]` unchanged | `[ Price ↑ ]` outlined brand |
| Both active | `[ Filter (3) ]` brand | `[ Price ↑ ]` brand |

Active = user has made a choice. Emphasis shifts to communicating what choice was made.

## Implementation

**Files:** `constants/sortOptions.js`, `components/activities/browse/FilterDayTripsPage.js`

**SORT_SHORT_LABEL mapping:**
```js
export const SORT_SHORT_LABEL = {
  '': 'Sort',              // default
  '-booked_count': 'Popular',
  '-average_rating': 'Top Rated',
  'min_rate': 'Price ↑',
  '-min_rate': 'Price ↓',
};
```

**Active state sx pattern:**
```js
// Filter button
borderColor: activeFilterCount > 0 ? COLORS.brand.primary : COLORS.neutral.gray300,
color: activeFilterCount > 0 ? COLORS.brand.primary : 'text.primary',

// Sort button
borderColor: filters.sort ? COLORS.brand.primary : COLORS.neutral.gray300,
color: filters.sort ? COLORS.brand.primary : 'text.primary',
```

**Desktop:** `SortBar` unchanged — count + sort dropdown above results, optional active sort chip.

**Mobile:** Sticky bottom bar has two buttons:
- Filter button opens `<Drawer>` with `<ExperienceSidebar>`
- Sort button opens lightweight `<Drawer>` with `<RadioGroup>` over `SORT_OPTIONS`, closes on selection

## Benchmark

| App | Pattern |
|---|---|
| Klook | Both outlined, active sort + filter state highlighted |
| Booking.com | Both outlined, state-driven color shift on active |
| GetYourGuide | Combined filter entry, both controls outlined |
| Viator | Separate sort modal, both outlined default |

All modern travel platforms avoid double-solid-CTA pattern. State = best signal.

## Tradeoffs

| Approach | Rating | Tradeoff |
|---|---|---|
| Both solid (old) | 5/10 | Too much visual weight, competes with booking CTA |
| Filter solid, Sort outline (initial) | 7.5/10 | Creates false hierarchy, users perceive Sort as utility |
| Both outlined, state-driven (chosen) | 9/10 | Cleaner, modern, scales to other filter types, content is signal |

## Consequences

- Reduces visual noise on sticky bar
- Emphasizes real state (filters applied/sort chosen) not semantic importance
- Extends well if new filter controls added later (all outlined, active state visible)
- Must always provide active sort label in button (e.g., not just icon)

## Related

- [[experiences-2026-marketplace-redesign]] — sort/filter UX part of broader activities redesign
- [[design-systems]] — button styling consistency across platform
- [[nextjs-fixed-header-per-route]] — sticky bar positioning pattern
