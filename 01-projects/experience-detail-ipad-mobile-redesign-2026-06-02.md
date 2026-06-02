# Experience Detail Page — iPad & Mobile Redesign

**Status:** Implemented  
**Date:** 2026-06-02  
**Branch:** `260602-feat/experience-detail-redesign`  
**Revert tag:** `pre-tablet-mobile-redesign` (commit `d2d7220`)  
**URL:** `/activities/detail/[slug]`

---

## Summary

Three minimal CSS-class changes to correctly optimize the experience detail page for iPad (1024px landscape) and mobile (390px) without touching desktop (≥1280px) or any booking logic.

---

## Problem

The premium desktop redesign (`experience-detail-page-redesign-2026-06-02.md`) shipped a polished 2-column layout at `lg` (1024px). But 1024px is iPad Pro landscape — a tablet breakpoint, not desktop. This caused:

1. **380px sidebar at 1024px** = 37% of viewport width for booking panel. Too wide for tablet. Cramped content column.
2. **Airbnb 5-up photo grid at `lg:hidden`** = tablets got single static hero image, not the premium grid.
3. **No price in sticky bar** = users on mobile/tablet couldn't see cost without opening the booking modal.
4. **Duplicate booking widget** at 768–1023px = `PremiumBookingPanel` rendered inline in single-col AND `DayTripMobileBookingBar` fixed at bottom simultaneously.

---

## Team Debate

### Issue 1: iPad layout — 2-col sidebar or single-col?

| Approach | Pros | Cons |
|----------|------|------|
| Keep 2-col at 1024px (status quo) | Booking always visible | 37% sidebar too wide, content cramped, not tablet-native UX |
| Move 2-col to 1280px (xl) | Single-col on tablet, matches Airbnb/Klook/GYG pattern | Requires updating 3 classes |
| Custom 3-col at md | More flexibility | Over-engineering for 1 breakpoint tweak |

**Resolution:** Move 2-col breakpoint from `lg` (1024px) → `xl` (1280px). Tablets get single-column. Mobile bar covers booking on tablet. Desktop unchanged.

### Issue 2: Photo grid — static hero vs Airbnb grid on tablet?

| Approach | Pros | Cons |
|----------|------|------|
| Keep single hero on tablet | No change | Wastes premium grid on ~30% of traffic |
| Add swipe carousel (Swiper.js) | Best mobile UX | New dependency, ~3KB, new component |
| Show Airbnb grid at md+ (768px) | Reuses existing component, zero new code | Grid cells smaller on iPad portrait; acceptable |

**Resolution:** Change `lg:` → `md:` breakpoint on `AirbnbPhotoGrid`. Show premium 5-up grid at 768px+. Single hero only on phones < 768px. Zero new components.

### Issue 3: Sticky bar — add price or not?

| Approach | Pros | Cons |
|----------|------|------|
| Keep current (date + Book Now) | No change | Users don't know price before opening modal |
| Add "From THB X,XXX" to left side | Matches Airbnb/Klook UX, conversion signal | Need to derive min price from ratecards |

**Resolution:** Add price. `Math.min(...ratecards)` is 3 lines, same pattern as `PremiumBookingPanel.js`. No new API call.

---

## Changes Implemented

### 1 — Layout breakpoint `lg` → `xl`

**`DayTripDetailPage.js:147`**
```
grid-cols-1 lg:grid-cols-[1fr_380px]
→ grid-cols-1 xl:grid-cols-[1fr_380px]
```

**`DayTripDetailPage.js` right col div**
```
<div role="complementary" ...>
→ <div role="complementary" ... className="hidden xl:block">
```

**`DayTripMobileBookingBar.js:85`**
```
lg:hidden → xl:hidden
```

### 2 — Photo grid breakpoint `lg` → `md`

**`AirbnbPhotoGrid.js:36`**
```
hidden lg:grid → hidden md:grid
```

**`AirbnbPhotoGrid.js:105`**
```
lg:hidden → md:hidden
```

### 3 — Price in sticky bar

**`DayTripMobileBookingBar.js`** — added `fromPrice` derivation:
```js
const fromPrice = (() => {
  const rates = (contract?.ratecards || []).map(r => parseFloat(r.selling_rate)).filter(p => p > 0);
  return rates.length > 0 ? Math.min(...rates) : null;
})();
```
Left section now shows: `From THB X,XXX` (bold) + date/availability (caption).

---

## Breakpoint Map After Change

| Width | Layout | Photo | Booking |
|-------|--------|-------|---------|
| < 768px (phone) | single-col | Single hero (`FeaturedImageHeader`) | `xl:hidden` bar visible |
| 768–1023px (iPad portrait) | single-col | Airbnb 5-up grid ✓ | Bar visible with price ✓ |
| 1024–1279px (iPad landscape) | single-col | Airbnb 5-up grid ✓ | Bar visible with price ✓ |
| ≥ 1280px (desktop) | 2-col `[1fr_380px]` | Airbnb 5-up grid | `PremiumBookingPanel` sidebar |

---

## What Did NOT Change

- Desktop layout (xl+): identical to before
- `DayTripBookingWidget` — booking logic untouched
- `PremiumBookingPanel` — internals untouched
- Hash navigation (#reviews, #gallery) — untouched
- SSG/ISR page — untouched
- All other components — untouched

---

## Verification Checklist

- [ ] 1280px+: 2-col layout, sticky sidebar, mobile bar hidden
- [ ] 1024px (iPad landscape): single-col, bar visible with "From THB X"
- [ ] 768px (iPad portrait): single-col, Airbnb grid visible, bar with price
- [ ] 390px (iPhone): single hero, bar with price
- [ ] No duplicate booking widget at any breakpoint
- [ ] Booking modal opens from bar at 768px and 1024px
- [ ] `npm run build` clean

---

## Files Modified

| File | Change |
|------|--------|
| `components/activities/detail/DayTripDetailPage.js` | `lg:` → `xl:` grid, `hidden xl:block` on right col |
| `components/activities/detail/DayTripMobileBookingBar.js` | `lg:hidden` → `xl:hidden`, price + redesigned left section |
| `components/activities/detail/AirbnbPhotoGrid.js` | `lg:` → `md:` on both grid/hero divs |

**Total code changed: ~15 lines. Zero new components. Zero new dependencies.**

---

## Related

- [[experience-detail-page-redesign-2026-06-02]] — desktop premium redesign (prerequisite)
- [[experiences-2026-marketplace-redesign]] — browse page redesign
- [[smartenplus-2026-ux-direction]] — overall UX direction
