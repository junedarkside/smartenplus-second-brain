# Mobile Search Bar UX — Competitor Research 2026

## Summary
Competitive analysis of mobile sticky search bars for ferry/transport booking. SmartEnPlus current bar has zero visual hierarchy; this research defines the redesign direction to beat competitors.

## Context
Trip results page `/trips/hatyai/koh-lipe` shows a flat mobile bar:
```
Hatyai → Koh Lipe
20 Jun · One Way · 👥 1 Passenger · [⭕ search circle]
```
Problems: all gray same-weight text, "One Way" wastes space, search icon is low-contrast gray circle, passenger button has no background — fails WCAG 44px touch target.

## Competitor Patterns

| Competitor | Sticky type | Key mobile win |
|---|---|---|
| Google Flights | Hide-on-scroll-down, reveal-on-scroll-up | Bold route dominant, colored search CTA |
| Airbnb | Always-visible compact | Pill chips per param, brand CTA always visible |
| VRBO | Visible + chip filters | Progressive disclosure, removable chips |
| Booking.com | Static (no scroll behavior) | Full fields upfront, high friction to edit |
| 12Go / Lomprayah | Minimal bar | Route dominant, but no visual hierarchy |

## Winning Patterns

### Visual Hierarchy
1. **Route** (origin → destination) — bold, dark, largest
2. **Date** — chip/badge, secondary
3. **Passenger count** — chip/badge, tappable
4. **Search CTA** — 40px+ filled brand-color circle, always right-aligned

### What to cut
- "One Way" label — implicit, wastes 7 chars on mobile
- Dot separators between chips — chips themselves provide separation
- Gray circle search icon — replace with brand-blue filled circle

### Touch Target Rules
- Min 44×44px per WCAG AA (see [[wcag-touch-target-enforcement]], [[touch-target-44px-enforcement]])
- Chips: `min-h-[28px]` with `px-2` gives sufficient target if stacked
- Search icon: `w-10 h-10` (40px) + `p-1` wrapper = 44px effective touch area

### Chip Pattern (Airbnb/VRBO standard)
```
[20 Jun]  [👥 1]  [🔍 brand-blue 40px]
```
- Chip style: `rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600`
- Passenger chip: tappable → opens Passenger modal
- Date chip: tappable → opens SearchDialog
- Search icon: `bg-fb-blue text-white rounded-full`

### Conversion Psychology
- Signal editability — background + hover state on each chip
- Make CTA impossible to miss — brand color, not gray
- Hide on scroll-down (current SmartEnPlus `StickySearchBar` already does opacity fade; keep)
- Reduce friction — tap chip = instant modal, no page reload

## Implementation Scope (2026-06-15)
Branch: `feat/mobile-search-bar-redesign`

Files changed:
- `components/search/SearchDialogTrigger.js` — add `variant="icon-branded"` (40px filled blue circle)
- `components/search/HeaderSearchSummary.js` — stacked branch: route row + chips row + branded CTA
- `components/search/StickySearchBar.js` — single-row: route+date, passenger pill (blue tint), branded CTA, drop "One Way" badge

No Redux/routing/modal changes — pure visual layer.

## Tradeoffs
- Removing "One Way" label: acceptable — round trip shows "Round Trip (Outbound/Return)" which IS informative; one-way is default/implicit
- Chip row may wrap on very small phones (320px) — use `flex-wrap` with `gap-1.5`
- Brand-blue on white: passes WCAG AA (4.5:1 ratio for #3b5998 on white)

## Related
- [[smartenplus-2026-ux-direction]] — Strategic UX direction (compact, calm, operational)
- [[wcag-touch-target-enforcement]] — 44px touch target rules
- [[touch-target-44px-enforcement]] — Implementation patterns
- [[design-systems]] — Token reference
- [[icon-button-size-decision]] — Icon sizing decisions
