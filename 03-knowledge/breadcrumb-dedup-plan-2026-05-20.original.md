# Breadcrumb Deduplication Plan

**Date:** 2026-05-20  
**Loose End:** #6  
**Branch:** new branch `260520-refactor/breadcrumb-dedup` off `develop`

---

## Target Pattern

```jsx
<div className="max-w-[1200px] mx-auto w-full px-2 md:px-3 mb-6">
  <DynamicStandardBreadcrumb lastBreadcrumb="..." />
</div>
```

StandardBreadcrumb already has `py-2` built-in. Wrapper only needs max-width, centering, padding, bottom margin.

---

## GROUP A — Already correct, NO CHANGE (8 files)

- `pages/bookings/index.js`
- `pages/orders/index.js`
- `pages/account/dashboard.js`
- `pages/account/profile.js`
- `pages/account/editPassword.js`
- `pages/rate-review/index.js`
- `pages/account/passenger/PassengersList.js`
- `pages/rate-review/[reviewSlug].js`

---

## GROUP B — Flatten section > div wrapper (10 files) — Commit 1

**Current pattern:**
```jsx
<section className='w-full flex flex-col justify-center gap-2 max-w-[1200px] mx-auto my-2'>
  <div className='px-4 flex justify-start item-start'>
    <DynamicStandardBreadcrumb />
  </div>
</section>
```

**Replace with target pattern.**

Files:
1. `pages/destinations/index.js` ~line 98
2. `pages/destinations/[slug].js`
3. `pages/trips/index.js` ~line 524
4. `pages/locations/index.js` ~line 136
5. `pages/locations/[slug].js`
6. `pages/airport-transfer/index.js` ~line 149
7. `pages/airport-transfer/[slug].js`
8. `pages/operators/index.js` ~line 59
9. `pages/operators/[slug].js`
10. `pages/forum/index.js` ~line 169 (uses `<nav>` inside section — replace whole block)

---

## GROUP C — Fix padding-only divs (4 files) — Commit 2

**Current pattern:**
```jsx
<div className='px-2 md:px-4'>   {/* or px-3 md:px-4 */}
  <DynamicStandardBreadcrumb ... />
</div>
```

**Replace with target pattern.** Note: `md:px-4` → `md:px-3`.

Files:
1. `pages/help/[...slug].js` — 3 instances (~lines 152, 211, 240) — fix all 3
2. `pages/ref/article/[slug].js` ~line 137
3. `pages/help/index.js` ~line 69 (missing mx-auto + max-w)
4. `components/blog/BlogPostDisplay.js` ~line 212

---

## GROUP D — Fix section with py-0 (2 files) — Commit 3

**Current pattern:**
```jsx
<section className='w-full max-w-[1200px] mx-auto px-2 md:px-4 py-0'>
  <DynamicStandardBreadcrumb ... />
</section>
```

**Replace** (div not section, md:px-3, add mb-6, drop py-0):

Files:
1. `components/trips/FilterTripsPage.js` ~line 204
2. `components/trips/TripDetailSchedule.js` ~line 34 — has semantic `<nav>` inside, keep it:
```jsx
<div className="max-w-[1200px] mx-auto w-full px-2 md:px-3 mb-6">
  <nav aria-label="breadcrumb">
    <DynamicStandardBreadcrumb ... />
  </nav>
</div>
```

---

## GROUP E — SKIP (context-dependent, do not change)

- `components/layout/AccountLayout.js` — parent controls spacing
- `components/daytrips/detail/DayTripDetailHeader.js` — inside MUI `<Box className="mb-8">`
- `pages/forum/[...slug].js` — inside MUI Stack, complex layout
- All blog pages (`pages/blog/index.js` etc.) — breadcrumb passed as `breadcrumbData` prop to `BlogPageWrapper`

---

## Execution Order

1. GROUP B — 10 files, commit: `refactor: standardize breadcrumb wrapper — flatten section/div patterns`
2. GROUP C — 4 files, commit: `refactor: standardize breadcrumb wrapper — fix padding-only patterns`
3. GROUP D — 2 files, commit: `refactor: standardize breadcrumb wrapper — fix section/py-0 patterns`

## Verification

- `npm run dev` → check `/destinations`, `/trips`, `/help`, `/locations`, `/airport-transfer`
- Breadcrumb: consistent left padding + bottom margin on all pages
- No layout shift vs before
- TripDetailSchedule: `<nav aria-label="breadcrumb">` still present in DOM
