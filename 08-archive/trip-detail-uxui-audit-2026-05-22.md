---
name: trip-detail-uxui-audit-2026-05-22
description: 3-specialist UX/UI audit of trip detail page. 32 issues found. Section/ContentCard abstraction absent from entire tree — root cause of all full-bleed mobile cards. All fixes implemented in branch 260522-fix/trip-detail-ux (3 commits).
metadata:
  type: project
  reviewed_by: trip-detail-uxui-auditor
  date: 2026-05-22
  page: http://localhost:3000/trips/hatyai/penang
  status: IMPLEMENTED
---

# Trip Detail Page UX/UI Audit — 2026-05-22

## Summary
32 issues: layout (12), visual/typography (10), conversion/a11y (10). Root cause: `Section`/`ContentCard` absent from trip detail tree. All fixes in `260522-fix/trip-detail-ux` (3 commits: `04b17f4`, `a31f12f`, `ac55eb3`).

## Context
SmartEnPlus trip detail page (`pages/trips/detail/[...slug].js`). ISR 300s. CSR hydration via `useCheckContractQuery`. Tree: TripDetailHero → SlideCalendar2 → TripDetail2[TripDetailsAttribute → TripDetailsImageAndMap → TripDetailContent → TripDetailBooking] → RelatedTripsSection → Reviews. Design standard: HOMEPAGE_SECTION token (`helpers/designSystem.js`) + `Section`/`ContentCard` (`components/common/`).

## Specialist A: Layout & Spacing (12 findings)

**Methodology:** Read `Section.js`, `ContentCard.js`, `designSystem.js:185–191`. Read full `[...slug].js`, trip detail components. Grep Section/ContentCard imports: zero across tree.

**LS1 — Section/ContentCard absent from trip detail tree** | P1 | Multiple

9+ sites hardcode layout. Root cause of LS2–LS12. Fix: ContentCard wrappers in TripDetail2.js; section padding in [..slug].js. **DONE.**

**LS2 — Page root missing max-w/layout tokens** | P2 | `[...slug].js:307`

`className='w-full'` — missing `flex flex-col max-w-[1200px] mx-auto`. Fix: `pb-16` added; structural gap at section level. **DONE (partial).**

**LS3 — Breadcrumb py-0 squish + px-4 vs px-3** | P2 | `[...slug].js:323`

`px-2 md:px-4 py-0` → zero vertical. Fix: `py-2 md:px-3`. **DONE.**

**LS4 — Calendar → Trip Details ungapped** | P2 | `[...slug].js:341`

`<section>` outside `gap-2` wrapper. Fix: `mt-2`. **DONE.**

**LS5 — Calendar full-bleed mobile** | P1 | `SlideCalendar2.js:985`

`md:mx-3 md:rounded-md` — no mobile margin. Fix: `mx-2 md:mx-3 xl:mx-0 rounded sm:rounded-md`. **DONE.**

**LS6 — Calendar section gap 4–6 vs standard 2** | P3 | `[...slug].js:332`

`gap-4 sm:gap-6` vs `gap-2`. Fix: Removed. **DONE.**

**LS7 — Trip Details gap-0 px-0 mobile** | P1 | `[...slug].js:341`

`gap-0 my-0 px-0 md:px-3`. Fix: `gap-2 mt-2 px-2 md:px-3`. **DONE.**

**LS8/9/10 — Three cards full-bleed all breakpoints** | P1 | `TripDetailsAttribute.js:41`, `TripDetailsImageAndMap.js:34`, `TripDetailContent.js:113`

Zero `mx-` everywhere. Fix: `<ContentCard>` at `TripDetail2.js`. **DONE.**

**LS11 — TripDetail2 gap-1 + timeline full-bleed** | P2 | `TripDetail2.js:134,152`

`gap-1` + outer `gap-0` = 4px total. Fix: `gap-2`; timeline in `<ContentCard>`. **DONE.**

**LS12 — RelatedTripsSection + Reviews px-0, gap-3, my-1.5** | P2 | `[...slug].js:361`, `RelatedTripsSection.js:171`

Non-4px-unit. Fix: Reviews: `gap-2 my-2 px-2 md:px-3`. RelatedTripsSection: deferred. **PARTIAL.**

## Specialist B: Visual Design & Typography (10 findings)

**Methodology:** Read `designSystem.js` (full). Grep `TYPOGRAPHY_SCALE` in trip detail → zero. Active in `components/order/`, `pages/bookings/`, `pages/blog/` — isolated, not systemic.

**VD1 — h1 mobile text-sm** | P1 | `TripDetailHero.js:57`

`text-sm md:text-3xl` = 12px mobile. Parent `text-lg` does NOT cascade. Fix: `text-base md:text-3xl`. **DONE.**

**VD2 — Section headings static text-lg** | P2 | Multiple

Fixed `text-lg` everywhere. HOMEPAGE_SECTION.heading = `text-xl`. Fix: Deferred (typography pass).

**VD3 — TYPOGRAPHY_SCALE zero adoption in trip detail** | P1 | `components/itinerary/`, `pages/trips/detail/`

Predates token adoption. Fix: P1 — adopt next refactor pass.

**VD4 — text-slate-600 off-palette** | P2 | `TripDetailContent.js:208`

Not in `gray-*` palette. Fix: `text-gray-600`. **DONE.**

**VD5 — text-md phantom class** | P1 | `TripDetailContent.js:208`, `[...slug].js:264,282`

Invalid Tailwind. Fix: `text-base` x3. **DONE.**

**VD6 — z-5 invalid z-index** | P1 | `TripDetailContent.js:114`

Tailwind scale: z-0, z-10, z-20... `z-5` → no CSS. Fix: `z-10`. **DONE.**

**VD7 — Cards md:rounded-lg vs rounded-md standard** | P2 | Multiple

`md:rounded-lg`, no mobile rounding. ContentCard provides standard rounding. Fix: ContentCard wrapper. **DONE.**

**VD8 — BookButton bgcolor secondary vs primary** | P2 | `BookButton.js:268`

#4267b3 = `COLORS.brand.secondary`. Book CTA should use primary (#3b5998). Fix: `#3b5998`; hover `#2d4474`. **DONE.**

**VD9 — RelatedTripsSection + Reviews over-padding** | P2 | Multiple

`p-4 md:p-6` vs standard `p-2`. Fix: Deferred for RelatedTripsSection. Reviews done.

**VD10 — Price text-xs in booking bar** | P2 | `TripDetailBooking.js:108`

Conversion info at 12px. Fix: `text-sm font-semibold`. **DONE.**

## Specialist C: User Flow & Conversion (10 findings)

**Methodology:** Read full `[...slug].js`, `TripDetailHero.js`, `TripDetailBooking.js`, `BestRateTable.js`, `TripDetailContent.js`, `BookButton.js`. Journey: land → route → price → date → passengers → Book.

**CF1 — Price lazy-loaded, no price in bar during hydration** | P1 | `[...slug].js:42-44`

Fallback = `<div>Loading Details...</div>`. BestRateTable inside lazy block. ISR mitigates repeat visits. Fix: Deferred — needs `lowestRate` prop threading.

**CF2 — Fixed bar obscures reviews; no pb-** | P1 | `[...slug].js:307`

Bar ~52px, no `pb-`. Fix: `pb-16`. **DONE.**

**CF3 — contractAvaliable=false empty state** | P1 | `TripDetailBooking.js:118`

Empty `<div>`. No messaging. Fix: fallback `"Not available for this date"`. **DONE.**

**CF4 — BookButton disabled no aria** | P1 | `BookButton.js:277`

`disabled={true}` → `opacity-50`. No aria. SR: "Book Now, dimmed." Fix: `aria-describedby="booking-status-msg"` + sr-only text. **DONE.**

**CF5 — Passenger selector no affordance** | P2 | `TripDetailBooking.js:98`

`cursor-pointer` but no chevron. Fix: `<ExpandMoreIcon fontSize="small" />`. **DONE.**

**CF6 — Calendar fallback CLS** | P1 | `[...slug].js:27`

Fallback ~36px → live ~80px = 44px CLS. Fix: `min-h-[80px]` + matching margins. **DONE.**

**CF7 — TripDetail2 fallback CLS** | P1 | `[...slug].js:43`

Fallback ~48px → live ~600–800px = hard CLS. Fix: `min-h-[600px]`. **DONE.**

**CF8 — lowestRate=null strands user** | P2 | `[...slug].js:279`

No nav link. Fix: `<Link href="/trips">Search other trips →</Link>`. **DONE.**

**CF9 — Price not visible above fold mobile 375px** | P2 | Architecture

Hero `min-h-[200px]` + breadcrumb ~30px + calendar ~80px = ~310px before trip details. Fix: Deferred — hero overlay redesign.

**CF10 — Sticky tab z-index broken** | P1 | `TripDetailContent.js:114`

`z-5` → tabs behind calendar (`z-10`). Same root as VD6. Fix: `z-10`. **DONE.**

## Cross-Specialist Debates

**D1 — ContentCard: page level vs per-component**
Verdict: TripDetail2.js level — only used on trip detail. Components stay layout-agnostic. **Implemented.**

**D2 — Calendar: keep slide UX?**
Verdict: Keep. Add `mx-2 md:mx-3 xl:mx-0 rounded sm:rounded-md`. **Implemented.**

**D3 — h1 text-sm: overlay vs semantic**
Verdict: `text-base md:text-3xl`. **Implemented.**

**D4 — TYPOGRAPHY_SCALE: trip-page P1 vs systemic P3**
Verdict: P1 — trip detail behind. Adopt next pass.

**D5 — Fixed bar pb-: layout.js vs page**
Verdict: `[...slug].js:307` only. **Implemented.**

**D6 — BookButton bgcolor: secondary token wrong semantic**
Verdict: Fix to primary (#3b5998). **Implemented.**

## Priority Fix Queue

**P1 — Implemented**
1. LS5 — Calendar full-bleed → `mx-2 md:mx-3 xl:mx-0` `04b17f4`+`a31f12f`
2. LS7 — gap-0 px-0 → `gap-2 mt-2 px-2 md:px-3` `a31f12f`
3. LS8/9/10 — 3 cards full-bleed → ContentCard `a31f12f`
4. VD1 — h1 text-sm → `text-base` `04b17f4`
5. VD5 — text-md → `text-base` x3 `04b17f4`
6. VD6/CF10 — z-5 → `z-10` `04b17f4`
7. CF2 — pb-16 page root `04b17f4`
8. CF3 — empty contractAvaliable message `ac55eb3`
9. CF4 — BookButton aria-describedby `ac55eb3`
10. CF6 — Calendar fallback `min-h-[80px]` `a31f12f`
11. CF7 — TripDetail2 fallback `min-h-[600px]` `a31f12f`

**P1 — Deferred**
- CF1 — Price lazy-load (needs lowestRate prop threading)
- VD3 — TYPOGRAPHY_SCALE adoption

**P2 — Implemented**
1. LS3 — Breadcrumb py-0→`py-2`, px-4→`px-3` `04b17f4`
2. LS4 — Calendar→Details gap: `mt-2` `a31f12f`
3. LS11 — gap-1→`gap-2`, timeline ContentCard `a31f12f`
4. LS12 — Reviews gap-3→`gap-2`, my-1.5→`my-2`, px-0→`px-2` `a31f12f`
5. VD4 — slate-600→`text-gray-600` `04b17f4`
6. VD7 — rounded-lg→ContentCard rounding `a31f12f`
7. VD8 — BookButton secondary→primary `04b17f4`
8. VD10 — Price text-xs→`text-sm font-semibold` `ac55eb3`
9. CF5 — ExpandMoreIcon chevron `ac55eb3`
10. CF8 — lowestRate=null escape link `04b17f4`

**P2 — Deferred**
- VD2 — Section headings responsive (typography pass)
- VD9 — RelatedTripsSection over-padding (separate scope)
- CF9 — Price above fold mobile (hero redesign)

**P3 — Implemented**
1. LS6 — Calendar gap-4 sm:gap-6 removed `a31f12f`

## Key Files Modified

- `pages/trips/detail/[...slug].js` — pb-16, py-2, mt-2, gap-2, px-2, CLS fallbacks, escape link
- `components/search/SlideCalendar2.js:985` — mx-2 md:mx-3 xl:mx-0 rounded mobile margins
- `components/itinerary/TripDetail2.js` — ContentCard import + wraps 4 sections
- `components/trips/detail/TripDetailHero.js:57` — h1 text-sm→text-base
- `components/itinerary/TripDetailContent.js:114,208` — z-5→z-10, text-md→text-base, slate-600→gray-600
- `components/itinerary/TripDetailBooking.js` — price text-sm, chevron, fallback message
- `components/UI/BookButton.js` — bgcolor primary, aria-describedby

## Branch

`260522-fix/trip-detail-ux` — 3 commits: `04b17f4` `a31f12f` `ac55eb3` → PR to `develop`

## Related

[[seo-homepage-specialist-team]] · [[homepage-seo-performance-deep-review-2026-05-21]] · [[trip-detail-page-review-2026-05-20]] · [[design-systems]] · [[master-state]]
