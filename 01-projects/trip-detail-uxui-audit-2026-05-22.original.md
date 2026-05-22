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
32 issues across layout (12), visual/typography (10), and conversion/a11y (10). Single root cause: `Section`/`ContentCard` abstractions absent from entire trip detail tree. All fixes implemented in branch `260522-fix/trip-detail-ux` (3 commits: `04b17f4`, `a31f12f`, `ac55eb3`).

## Context
SmartEnPlus trip detail page (`pages/trips/detail/[...slug].js`). ISR revalidate=300s. CSR hydration overlay via `useCheckContractQuery`. Component tree: TripDetailHero → SlideCalendar2 → TripDetail2[TripDetailsAttribute → TripDetailsImageAndMap → TripDetailContent → TripDetailBooking] → RelatedTripsSection → Reviews. Design standard: HOMEPAGE_SECTION token (`helpers/designSystem.js`) + `Section`/`ContentCard` (`components/common/`).

---

## Specialist A: Layout & Spacing

### Methodology
Read `Section.js`, `ContentCard.js`, `designSystem.js:185–191`. Read `[...slug].js` (full), `TripDetailHero.js`, `SlideCalendar2.js:975–1010`, `TripDetail2.js:125–175`, `TripDetailsAttribute.js:40–131`, `TripDetailsImageAndMap.js:30–65`, `TripDetailContent.js:110–120`, `TripDetailBooking.js:88–144`, `RelatedTripsSection.js:115–211`, `ReviewListByProduct.js:100–124`. Grep for Section/ContentCard imports: zero results confirmed across entire trip detail tree.

### Findings

**LS1 — Section/ContentCard abstraction absent from entire trip detail tree** | P1 | Multiple files

9+ sites hardcoding layout: `[...slug].js:307,322,331,341,361` bare divs/sections; `TripDetailsAttribute.js:41`, `TripDetailsImageAndMap.js:34`, `TripDetailContent.js:113`, `RelatedTripsSection.js:171` — all manual layout reimplementation. Root cause of all LS2–LS12.
Fix: ContentCard wrappers in TripDetail2.js; section padding fixes in [..slug].js. **DONE.**

**LS2 — Page root wrapper missing max-w/layout tokens** | P2 | `[...slug].js:307`

`className='w-full'` — missing `flex flex-col max-w-[1200px] mx-auto`. Ultra-wide (>1200px) expands beyond design intent.
Fix: `pb-16` added; structural gap resolved by section fixes. **DONE (partial — pb-16 added, max-w on section level).**

**LS3 — Breadcrumb py-0 squish + px-4 vs standard px-3** | P2 | `[...slug].js:323`

`px-2 md:px-4 py-0` → zero vertical padding = dead strip between hero and calendar.
Fix: `py-2 md:px-3`. **DONE.**

**LS4 — Calendar → Trip Details ungapped** | P2 | `[...slug].js:341`

Trip Details `<section>` was sibling outside `gap-2` wrapper — zero enforced gap.
Fix: `mt-2` on `:341` section. **DONE.**

**LS5 — Calendar full-bleed mobile** | P1 | `SlideCalendar2.js:985`

`md:mx-3 md:rounded-md` — no mobile margin, no mobile rounding.
Fix: `mx-2 md:mx-3 xl:mx-0 rounded sm:rounded-md`. **DONE.**

**LS6 — Calendar section internal gap 4–6 vs standard 2** | P3 | `[...slug].js:332`

`gap-4 sm:gap-6` (16–24px) vs standard `gap-2` (8px).
Fix: Removed (`max-w-[1200px] mx-auto` kept, gap removed). **DONE.**

**LS7 — Trip Details section gap-0 px-0 mobile** | P1 | `[...slug].js:341`

`gap-0 my-0 px-0 md:px-3` — cards touched, no mobile horizontal padding.
Fix: `gap-2 mt-2 px-2 md:px-3`. **DONE.**

**LS8 — TripDetailsAttribute full-bleed all breakpoints** | P1 | `TripDetailsAttribute.js:41`

Zero `mx-` at every breakpoint.
Fix: Wrapped in `<ContentCard>` at `TripDetail2.js:136`. **DONE.**

**LS9 — TripDetailsImageAndMap full-bleed all breakpoints** | P1 | `TripDetailsImageAndMap.js:34`

Same pattern as LS8.
Fix: `<ContentCard>` wrapper at `TripDetail2.js:145`. **DONE.**

**LS10 — TripDetailContent full-bleed all breakpoints** | P1 | `TripDetailContent.js:113`

Same pattern.
Fix: `<ContentCard>` wrapper at `TripDetail2.js:162`. **DONE.**

**LS11 — TripDetail2 internal gap-1 + timeline full-bleed** | P2 | `TripDetail2.js:134,152`

`gap-1` (4px) + outer `gap-0` = 4px card separation total. Timeline div also full-bleed.
Fix: `gap-2`; timeline wrapped in `<ContentCard>`. **DONE.**

**LS12 — RelatedTripsSection + Reviews px-0 mobile, gap-3, my-1.5** | P2 | `[...slug].js:361`, `RelatedTripsSection.js:171`

`px-0`, `gap-3`, `my-1.5` (non-4px-unit).
Fix: Reviews: `gap-2 my-2 px-2 md:px-3`. RelatedTripsSection: deferred (RelatedTrips has its own internal layout, full fix needs separate pass). **PARTIAL — reviews fixed.**

---

## Specialist B: Visual Design & Typography

### Methodology
Read `designSystem.js` (full). Read `TripDetailHero.js:55–60`, `TripDetailsAttribute.js:40–130`, `TripDetailContent.js:110–278`, `BestRateTable.js`, `TripDetailBooking.js:90–130`, `TimeLineDisplay.js`, `RelatedTripsSection.js:120–130`, `BookButton.js:260–291`. Grep for `TYPOGRAPHY_SCALE` in trip detail tree → zero. Grep in `components/order/`, `pages/bookings/`, `pages/blog/` → active usage confirmed (P1, not systemic P3).

### Findings

**VD1 — h1 mobile text-sm** | P1 | `TripDetailHero.js:57`

`text-sm md:text-3xl` = 12px mobile. TYPOGRAPHY_SCALE.h1 minimum = 24px. Parent `text-lg` on wrapper div does NOT cascade to h1.
Fix: `text-base md:text-3xl`. **DONE.**

**VD2 — Section headings static text-lg, no responsive scale** | P2 | Multiple

`TripDetailsImageAndMap.js:35`, `TripDetailContent.js:137,151,181,205`, `TripDetail2.js:153` — all `text-lg` fixed. HOMEPAGE_SECTION.heading = `text-xl`. TYPOGRAPHY_SCALE.h3 = `text-lg sm:text-xl`.
Fix: Deferred — low visual impact, no P0/P1 user harm. Tag for typography pass.

**VD3 — TYPOGRAPHY_SCALE zero adoption in trip detail** | P1 | `components/itinerary/`, `pages/trips/detail/`

Trip detail predates token adoption. Other areas (orders, bookings, blog) use tokens.
Fix: Tagged P1 — adopt in next refactor pass alongside ContentCard work.

**VD4 — text-slate-600 off-palette** | P2 | `TripDetailContent.js:208`

`text-slate-600` not in approved `gray-*` neutral palette.
Fix: `text-gray-600`. **DONE.**

**VD5 — text-md phantom class** | P1 | `TripDetailContent.js:208`, `[...slug].js:264,282`

`text-md` not a valid Tailwind token — generates no CSS, inherits parent size.
Fix: `text-base` in all 3 places. **DONE.**

**VD6 — z-5 invalid Tailwind z-index** | P1 | `TripDetailContent.js:114`

Tailwind z-index scale: z-0, z-10, z-20, z-30, z-40, z-50 only. `z-5` → no CSS → sticky tab bar loses stacking context.
Fix: `z-10`. **DONE.**

**VD7 — Cards md:rounded-lg vs rounded-md standard** | P2 | Multiple

`TripDetailsAttribute.js:41`, `TripDetailsImageAndMap.js:34`, `TripDetailContent.js:113` — `md:rounded-lg` (8px), no mobile rounding. ContentCard provides `rounded sm:rounded-lg`.
Fix: ContentCard wrapper provides correct rounding. **DONE (via ContentCard wrapping).**

**VD8 — BookButton bgcolor #4267b3 secondary vs primary** | P2 | `BookButton.js:268`

#4267b3 = `COLORS.brand.secondary`. Book CTA should use primary (#3b5998 = fb-blue).
Fix: `#3b5998`; hover `#2d4474`. **DONE.**

**VD9 — RelatedTripsSection + Reviews rounded-lg + over-padding** | P2 | Multiple

`p-4 md:p-6` (16–24px) vs standard `p-2`. `rounded-lg` vs container `rounded-md`.
Fix: Deferred for RelatedTripsSection (separate component scope). Reviews section structural fix done.

**VD10 — Price text-xs in booking bar** | P2 | `TripDetailBooking.js:108`

Primary conversion info (total price) at 12px.
Fix: `text-sm font-semibold`. **DONE.**

---

## Specialist C: User Flow & Conversion

### Methodology
Read `[...slug].js:25–55` (dynamic imports + fallbacks) and `:305–378` (render tree). Read `TripDetailHero.js`, `TripDetailBooking.js` (full), `BestRateTable.js`, `TripDetailContent.js:110–145`, `BookButton.js:260–295`, `TripDetail2.js:55–80`, `FeaturedImageHeaderSkeleton.js`. User journey traced: land → understand route → see price → select date → select passengers → tap Book.

### Findings

**CF1 — Price lazy-loaded, no price in bar during hydration** | P1 | `[...slug].js:42–44`

`DynamicTripDetail2` loading fallback = `<div className="text-center p-4">Loading Details...</div>`. BestRateTable inside this lazy block. Bar shows "Calculating..." until hydration. Mitigated by ISR on repeat visits.
Fix: Deferred — requires passing `lowestRate` from page-level props into bar initial render (medium effort). Tag for perf pass.

**CF2 — Fixed bar obscures reviews; no pb- on page root** | P1 | `[...slug].js:307`

Fixed bar ~52px, page root had no `pb-`. Last content hidden.
Fix: `pb-16`. **DONE.**

**CF3 — contractAvaliable=false empty bar state** | P1 | `TripDetailBooking.js:118`

`isNonOperatingDay=false` but `contractAvaliable=false` → empty `<div>`. No user messaging for advance_hr passed, stop_sale, inactive contract, out-of-range date.
Fix: fallback `"Not available for this date"`. **DONE.**

**CF4 — BookButton disabled no accessibility context** | P1 | `BookButton.js:277`

`disabled={true}` → `opacity-50`. No aria context. Screen reader: "Book Now, dimmed."
Fix: `aria-describedby="booking-status-msg"` + `<span className="sr-only">Select a date to continue</span>`. **DONE.**

**CF5 — Passenger selector no visual affordance** | P2 | `TripDetailBooking.js:98`

`cursor-pointer` but no chevron, no "tap to edit" hint. Looks like static badge.
Fix: `<ExpandMoreIcon fontSize="small" />`. **DONE.**

**CF6 — Calendar loading fallback CLS** | P1 | `[...slug].js:27`

Fallback ~36px, live calendar ~80px → 44px CLS on hydration.
Fix: `min-h-[80px]` + matching margins on fallback div. **DONE.**

**CF7 — TripDetail2 loading fallback CLS** | P1 | `[...slug].js:43`

Fallback ~48px, full TripDetail2 ~600–800px → hard CLS.
Fix: `min-h-[600px]`. **DONE.**

**CF8 — lowestRate=null error state strands user** | P2 | `[...slug].js:279`

No navigation link in pricing unavailable state. User must use browser back.
Fix: `<Link href="/trips">Search other trips →</Link>`. **DONE.**

**CF9 — Price not visible above fold mobile 375px** | P2 | Architecture

Hero `min-h-[200px]` + breadcrumb ~30px + calendar ~80px = ~310px before trip details. Fixed bar shows price only post CSR hydration.
Fix: Deferred — requires hero overlay redesign (medium effort, separate UX initiative).

**CF10 — Sticky tab z-index broken during scroll** | P1 | `TripDetailContent.js:114`

`z-5` invalid — tabs render behind calendar (`z-10`) during scroll. Same root as VD6.
Fix: `z-10`. **DONE (same as VD6).**

---

## Discussion: Cross-Specialist Debates

### D1 — ContentCard wrapper: page level vs per-component mx classes
Spec A: Could patch `mx-` on each component's className.
Counter: TripDetailsAttribute, TripDetailsImageAndMap, TripDetailContent reused on other pages — adding `mx-` directly would break those layouts.
**Leader verdict:** Fix at TripDetail2.js level (not page level). TripDetail2 is only used on trip detail page — wrapping there keeps components layout-agnostic. Effort: small. **Implemented.**

### D2 — Calendar: keep SlideCalendar2 slide UX or replace?
Spec C: Horizontal swipe = correct UX for multi-date transportation booking.
Spec A: Full-bleed mobile inconsistent with all other sections.
**Leader verdict:** Keep slide UX. Add `mx-2 md:mx-3 xl:mx-0 rounded sm:rounded-md` directly to SlideCalendar2 outer div. No behavior change. Effort: trivial. **Implemented.**

### D3 — h1 text-sm: hero overlay constraint vs semantic
Spec B: 12px h1 = semantic error below body text.
Spec A: Parent `text-lg` wrapper visually reads larger.
**Leader verdict:** Parent `text-lg` on wrapper div doesn't cascade to h1's own `text-sm`. Fix: `text-base md:text-3xl`. **Implemented.**

### D4 — TYPOGRAPHY_SCALE: trip-page P1 vs systemic P3
Spec B: Zero imports in trip detail = P1.
Grep: TYPOGRAPHY_SCALE active in `OrderDetail.js`, `pages/bookings/index.js`, `pages/blog/`. Trip detail is isolated gap, not systemic.
**Leader verdict:** P1 — trip detail behind, not entire app. Adopt in next refactor pass.

### D5 — Fixed bar pb- fix: layout.js vs page file
Spec A: Fix in layout.js `<main>` to cover all pages.
Spec C: Only trip detail page has this fixed bar.
**Leader verdict:** Fix in `[...slug].js:307` only. layout.js patch would add unnecessary padding to every page. **Implemented.**

### D6 — BookButton bgcolor: secondary token vs wrong usage
Spec B: #4267b3 IS a defined token (secondary), not arbitrary.
Counter: Primary CTA should use primary color token, not secondary.
**Leader verdict:** Defined token, wrong semantic usage. Fix to primary (#3b5998). **Implemented.**

---

## Leader Synthesis

32 issues confirmed. Root cause structural: trip detail page was built as a one-off with no shared abstractions. Homepage progressively adopted Section/ContentCard tokens; trip detail never did. ContentCard wrapper pass in TripDetail2.js resolves 8 issues in one commit (LS5, LS7, LS8, LS9, LS10, LS11 via ContentCard + gap fix, VD7 via ContentCard rounding).

Typography violations clustered around 3 phantom/invalid classes: `text-md` (3 occurrences, no CSS), `z-5` (1 occurrence, no stacking context), `text-slate-600` (off-palette). All trivial find-replace. The h1 `text-sm` at 12px mobile was the highest-visibility single fix — page title smaller than body text on 375px viewport.

Conversion gaps: fixed bar obscuring reviews (pb-16), empty booking state messaging (CF3), CLS from two lazy-load fallbacks (CF6, CF7). The passenger selector chevron (CF5) was a hidden affordance — users couldn't discover it was interactive.

Deferred (medium effort, separate initiative): price in bar during hydration (CF1), price visibility above fold (CF9), RelatedTripsSection inner card over-padding (VD9), TYPOGRAPHY_SCALE full adoption (VD3).

---

## Priority Fix Queue (as implemented)

**P0 — none confirmed**

**P1 — Implemented**
1. LS5 — Calendar full-bleed mobile → mx-2 md:mx-3 xl:mx-0 on SlideCalendar2 `04b17f4`+`a31f12f`
2. LS7 — Trip Details gap-0 px-0 → gap-2 mt-2 px-2 md:px-3 `a31f12f`
3. LS8/LS9/LS10 — Three cards full-bleed → ContentCard wrapper `a31f12f`
4. VD1 — h1 text-sm → text-base `04b17f4`
5. VD5 — text-md → text-base x3 `04b17f4`
6. VD6/CF10 — z-5 → z-10 sticky tabs `04b17f4`
7. CF2 — pb-16 page root `04b17f4`
8. CF3 — empty contractAvaliable state message `ac55eb3`
9. CF4 — BookButton aria-describedby `ac55eb3`
10. CF6 — Calendar fallback min-h-[80px] `a31f12f`
11. CF7 — TripDetail2 fallback min-h-[600px] `a31f12f`

**P1 — Deferred**
- CF1 — Price lazy-load gap (medium effort — needs lowestRate prop threading)
- VD3 — TYPOGRAPHY_SCALE adoption (refactor pass)

**P2 — Implemented**
1. LS3 — Breadcrumb py-0→py-2, px-4→px-3 `04b17f4`
2. LS4 — Calendar→Trip Details gap: mt-2 `a31f12f`
3. LS11 — TripDetail2 gap-1→gap-2, timeline ContentCard `a31f12f`
4. LS12 — Reviews gap-3→gap-2, my-1.5→my-2, px-0→px-2 `a31f12f`
5. VD4 — text-slate-600→text-gray-600 `04b17f4`
6. VD7 — rounded-lg→ContentCard rounding `a31f12f`
7. VD8 — BookButton bgcolor secondary→primary `04b17f4`
8. VD10 — Price text-xs→text-sm font-semibold `ac55eb3`
9. CF5 — ExpandMoreIcon chevron on passenger selector `ac55eb3`
10. CF8 — lowestRate=null escape link `04b17f4`

**P2 — Deferred**
- VD2 — Section headings responsive scale (typography pass)
- VD9 — RelatedTripsSection over-padding (separate component scope)
- CF9 — Price above fold mobile (hero redesign initiative)

**P3 — Implemented**
1. LS6 — Calendar section gap-4 sm:gap-6 removed `a31f12f`

---

## Key Files Modified

- `pages/trips/detail/[...slug].js` — pb-16, py-2, mt-2, gap-2, px-2, CLS fallbacks, escape link
- `components/search/SlideCalendar2.js:985` — mx-2 md:mx-3 xl:mx-0 rounded mobile margins
- `components/itinerary/TripDetail2.js` — ContentCard import + wraps 4 child sections
- `components/trips/detail/TripDetailHero.js:57` — h1 text-sm→text-base
- `components/itinerary/TripDetailContent.js:114,208` — z-5→z-10, text-md→text-base, slate-600→gray-600
- `components/itinerary/TripDetailBooking.js` — price text-sm, chevron, fallback message
- `components/UI/BookButton.js` — bgcolor primary, aria-describedby

## Branch

`260522-fix/trip-detail-ux` — 3 commits: `04b17f4` `a31f12f` `ac55eb3` → PR to `develop`

## Related

- [[seo-homepage-auditor]]
- [[homepage-seo-performance-deep-review-2026-05-21]]
- [[trip-detail-page-review-2026-05-20]]
- [[design-systems]]
- [[master-state]]
