# Breadcrumb Deduplication Plan

**Date:** 2026-05-20 | **Loose End:** #6 | **Branch:** `260520-refactor/breadcrumb-dedup` off `develop`

## Target Pattern

```jsx
<div className="max-w-[1200px] mx-auto w-full px-2 md:px-3 mb-6">
  <DynamicStandardBreadcrumb lastBreadcrumb="..." />
</div>
```

StandardBreadcrumb has `py-2` built-in. Wrapper: max-width, centering, padding, bottom margin.

## GROUP A — Already correct, NO CHANGE (8 files)

`pages/bookings/index.js`, `pages/orders/index.js`, `pages/account/dashboard.js`, `pages/account/profile.js`, `pages/account/editPassword.js`, `pages/rate-review/index.js`, `pages/account/passenger/PassengersList.js`, `pages/rate-review/[reviewSlug].js`

## GROUP B — Flatten section > div wrapper (10 files) — Commit 1

**From:**
```jsx
<section className='w-full flex flex-col justify-center gap-2 max-w-[1200px] mx-auto my-2'>
  <div className='px-4 flex justify-start item-start'>
    <DynamicStandardBreadcrumb />
  </div>
</section>
```
**To:** target pattern.

Files: `pages/destinations/index.js` ~98, `pages/destinations/[slug].js`, `pages/trips/index.js` ~524, `pages/locations/index.js` ~136, `pages/locations/[slug].js`, `pages/airport-transfer/index.js` ~149, `pages/airport-transfer/[slug].js`, `pages/operators/index.js` ~59, `pages/operators/[slug].js`, `pages/forum/index.js` ~169

## GROUP C — Fix padding-only divs (4 files) — Commit 2

**From:** `<div className='px-2 md:px-4'><DynamicStandardBreadcrumb /></div>`
**To:** target pattern (`md:px-4` → `md:px-3`).

Files: `pages/help/[...slug].js` (3 instances ~152, 211, 240), `pages/ref/article/[slug].js` ~137, `pages/help/index.js` ~69, `components/blog/BlogPostDisplay.js` ~212

## GROUP D — Fix section with py-0 (2 files) — Commit 3

**From:** `<section className='w-full max-w-[1200px] mx-auto px-2 md:px-4 py-0'>`
**To:** div, `md:px-3`, add `mb-6`, drop `py-0`.

Files: `components/trips/FilterTripsPage.js` ~204, `components/trips/TripDetailSchedule.js` ~34 (keep `<nav aria-label="breadcrumb">` inside)

## GROUP E — SKIP

`components/layout/AccountLayout.js` (parent controls), `components/daytrips/detail/DayTripDetailHeader.js` (inside MUI Box), `pages/forum/[...slug].js` (MUI Stack), blog pages (`breadcrumbData` prop)

## Execution Order

1. GROUP B — `refactor: standardize breadcrumb wrapper — flatten section/div patterns`
2. GROUP C — `refactor: standardize breadcrumb wrapper — fix padding-only patterns`
3. GROUP D — `refactor: standardize breadcrumb wrapper — fix section/py-0 patterns`

## Verification
- `npm run dev` → check `/destinations`, `/trips`, `/help`, `/locations`, `/airport-transfer`
- Consistent left padding + bottom margin on all pages
- No layout shift
- TripDetailSchedule: `<nav aria-label="breadcrumb">` in DOM
