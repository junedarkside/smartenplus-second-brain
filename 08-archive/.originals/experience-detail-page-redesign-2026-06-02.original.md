# Experience Detail Page — Premium Redesign 2026

**Status:** Planned (not implemented)
**Date:** 2026-06-02
**URL:** `/activities/detail/[slug]`
**Reference image:** ChatGPT mockup, Airbnb Experiences benchmark

---

## Problem

Current detail page reads like a logistics document. Trust signals weak. Reviews buried at bottom. Booking widget feels like a form. Timeline dominates page. Users must scroll far before deciding to book.

**Conversion goal:** User understands within 5 seconds — what it is, why it's worth booking, why to trust it, how much it costs, how to reserve.

---

## Design Decisions

| Decision | Resolution | Reason |
|----------|-----------|--------|
| Photo approach | Airbnb 5-up grid (1 large + 4 thumbs) | Immediately communicates experience value |
| Hero vs gallery | Merge into one AirbnbPhotoGrid component | Current: hero + separate gallery = fragmented UX |
| Section order | Visuals → Title → Trust → Highlights → Why Love → Description → Reviews → Itinerary → Logistics → FAQ | Conversion-first, trust before logistics |
| Reviews position | Before itinerary | Social proof converts better than timeline detail |
| Timeline | Collapsed by default (MUI Accordion) | De-emphasize logistics, available on demand |
| Inclusions/Exclusions | 2-col side-by-side, no accordion | Easy comparison, always visible |
| Meeting point | Human-readable card | No raw enum string (HOTEL_PICKUP) |
| Booking panel | Premium wrapper around existing DayTripBookingWidget | Zero risk to booking logic |
| StickySidebar location | **Move to page level (DayTripDetailPage right column)** | DayTripBookingWidget.js:374 wraps itself in StickySidebar — PremiumBookingPanel wrapping it = double sticky = breaks. Fix: remove StickySidebar from widget, add to page right column. |
| Trust badges source | **Dynamic from `contract.extra` (not static strings)** | DayTripCard.js:49 reads `extra?.filter(e => e.type === 'FEATURE')`. Static badges would show "Hotel Pickup" for tours that don't offer it. |
| Highlights HTML parse | **`<li>` extract, fallback to HTMLContentRenderer** | `tour_highlights` is free-form TextField — operators use `<p>`, `<ul>`, or prose. `<li>` parse is best-effort only; if 0 items found, fall back to existing HTML blob render. |
| Related experiences | Client-side fetch via useGetContractsQuery | Same hook as FilterDayTripsPage, no new API |
| API | Zero new endpoints | All data from existing /product-detail/{slug}/ |
| Redux | Zero new state | Reuse existing dayTrip slice + cart slice |

---

## Layout

```
max-w-[1280px], lg:grid-cols-[1fr_380px]

ABOVE GRID (full-bleed):
  AirbnbPhotoGrid  ← 5-up photo grid desktop, single hero mobile

LEFT COLUMN (70%):
  ExperienceTitleArea     ← h1 + rating + trust badges + breadcrumbs
  ExperienceHighlights    ← icon cards (parsed from tour_highlights HTML)
  WhyTravelersLove        ← 5 selling-point cards
  AboutThisExperience     ← description (no accordion, inline ~15 lines)
  ReviewListByProduct     ← MOVED UP (was last)
  TimelineDisplay         ← collapsed MUI Accordion wrapper (inline)
  IncludedExcluded        ← 2-col layout, no accordion
  MeetingPointCard        ← human-readable, no raw enum
  ExperienceFAQ           ← sourced from existing fields
  RelatedExperiences      ← 3-4 DayTripCards, client-side fetch

RIGHT COLUMN (30%, sticky):
  PremiumBookingPanel     ← wraps DayTripBookingWidget
```

---

## New Components (all in `components/activities/detail/`)

### AirbnbPhotoGrid.js
- Props: `{ images, featuredImage, tourName, onOpenGallery }`
- Desktop: `hidden lg:grid grid-cols-[2fr_1fr] h-[480px] rounded-xl overflow-hidden`
- Right side: `grid-rows-2 grid-cols-2` (4 thumbs)
- Mobile: renders `FeaturedImageHeader` (existing, zero new code)
- Images: `contract.featured_image` + `contract.image[]`, max 5
- `priority={true}` on main image (LCP)
- "Show all photos" button → calls `onOpenGallery` (existing Gallery lightbox)
- Graceful: 1 image = single hero, no crash

### ExperienceTitleArea.js
- Props: `{ contract }`
- Fields: `translated_name||name`, `average_rating`, `review_count`, `service_category`, `difficulty_level`, `extra[]`
- Reuses: `StandardBreadcrumb` (dynamic), `AverageRating` with `title={false}`
- Trust badges **dynamic from `contract.extra`** — same pattern as `DayTripCard.js:49-55`:
  ```js
  const features = contract.extra?.filter(e => e.type === 'FEATURE') || [];
  const freeCancellation = features.some(f => f.item.toLowerCase().includes('cancellation'));
  const hotelPickup = features.some(f => f.item.toLowerCase().includes('pickup'));
  const instantConfirmation = features.some(f => f.item.toLowerCase().includes('instant'));
  ```
- Only render badges that exist in data. `CheckCircleIcon` in `COLORS.status.success`
- "Top Rated" badge: only if `average_rating >= 4.5 && review_count >= 10`
- Rating row: `href="#reviews"` (preserves existing hash scroll)

### ExperienceHighlights.js
- Props: `{ html }` — caller: `contract.translated_highlights || contract.tour_highlights`
- Parse `<li>` text via `html-react-parser` (already installed), max 6 items
- **`tour_highlights` is a free-form TextField** — operators may use `<p>`, `<ul><li>`, or prose. `<li>` parse is best-effort only.
- Grid: `grid grid-cols-1 sm:grid-cols-2 gap-3`
- Each card: `CheckCircleIcon` green + text (reuse `KeyFeatures.js` icon pattern)
- **Fallback (most tours will hit this):** if `extractLiItems(html).length === 0` → render `HTMLContentRenderer html={html}` unchanged

### WhyTravelersLove.js
- Props: `{ contract }`
- 5 cards, filter null values:
  - Duration: `tour_duration_days` + `AccessTimeIcon`
  - Capacity: `max_participants` + `PeopleIcon`
  - Transport: `transport_composit[0]` + vehicle icon
  - Meeting: `MEETING_POINT_TYPE_LABELS[meeting_point_type]` + `LocationOnIcon`
  - Rating: `average_rating` + `StarIcon`
- Grid: `grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3`
- Card: `flex flex-col items-center text-center p-3 rounded-xl bg-gray-50`

### IncludedExcluded.js
- Props: `{ inclusions, exclusions }` — caller passes translated fallback
- `grid grid-cols-1 sm:grid-cols-2 gap-6`
- Inclusions: `CheckCircleIcon` green + `HTMLContentRenderer`
- Exclusions: `CancelIcon` gray + `HTMLContentRenderer`
- Card: `border border-gray-200 rounded-md p-6`
- Returns `null` if both empty

### MeetingPointCard.js
- Props: `{ meetingPointType, meetingPointDetails }`
- Uses `MEETING_POINT_TYPE_LABELS[meetingPointType]` — existing constant, no raw enum
- `LocationOnIcon` in `bg-blue-50` circle
- Returns `null` if `meetingPointType` null

### ExperienceFAQ.js
- Props: `{ whatToBring, ageRestriction, meetingPointType, difficulty }`
- MUI `Accordion` (same pattern as `DayTripContent.js`)
- Items (filter null source):
  - "What should I bring?" → `whatToBring` HTML
  - "Are there age restrictions?" → `ageRestriction`
  - "How difficult is this?" → map `difficulty_level` → friendly string
  - 2 static: "Can I cancel?", "Is this suitable for beginners?"
- All collapsed by default

### PremiumBookingPanel.js
- Props: `{ contract, selectedDate, onDateChange }`
- **Wrapper pattern** — wraps existing `DayTripBookingWidget`, zero risk to booking logic
- Outer `Card`: `boxShadow: '0 2px 20px rgba(0,0,0,0.12)'`, `borderRadius: '16px'`, `border: '1.5px solid #e5e7eb'`
- Header: "From THB X,XXX" via `PricingDisplay` + star rating
- Body: `DayTripBookingWidget` with `sx={{ boxShadow: 'none', border: 'none' }}`
- Footer trust row: `CheckCircleIcon` green + "Free Cancellation" / "Instant Confirmation" / "No Hidden Fees"
- "From" price: `Math.min(...ratecards.map(r => parseFloat(r.selling_rate)).filter(p => p > 0))` — same as `DayTripCard.js`
- **⚠️ StickySidebar must be removed from `DayTripBookingWidget.js:374`** before this wrapper is used. `DayTripDetailPage.js` right column wraps with `<StickySidebar>` instead. Double StickySidebar = sticky positioning breaks (see `CLAUDE.md` StickySidebar constraint).

### RelatedExperiences.js
- Props: `{ serviceCategory, currentSlug }`
- Client-only (dynamic import, `ssr: false`)
- Hook: `useGetContractsQuery({ serviceCategory, pageSize: 5 })` — same as `FilterDayTripsPage.js`
- **No `exclude_slug` API param.** Client-side: `results.filter(c => c.slug !== currentSlug).slice(0, 4)`. Request 5, remove current if present, show at most 4. If current not in first 5 (possible for new/low-ranked tours), all 4 slots show other contracts — acceptable.
- Grid: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4`
- Renders existing `DayTripCard` (no changes)
- Loading: skeleton pattern from `DayTripList.js`
- Returns `null` if no results

---

## Files Modified

### `DayTripDetailPage.js` — major rewrite
- `max-w-[1200px]` → `max-w-[1280px]`
- `md:grid-cols-[8fr_4fr]` → `lg:grid-cols-[1fr_380px]`
- Mount `AirbnbPhotoGrid` above two-column grid (full-bleed)
- New section order (see layout above)
- `AboutThisExperience` inline (heading + `HTMLContentRenderer`, ~15 lines)
- Timeline inline wrapper: MUI `Accordion defaultExpanded={false}` wrapping `TimelineDisplay`
- **Right column**: `<StickySidebar><DynamicPremiumBookingPanel .../></StickySidebar>` — StickySidebar moved here from `DayTripBookingWidget`
- **Keep (high risk if dropped) — hash navigation system has 4 moving parts:**
  1. `reviewsRef = useRef(null)` — on `ReviewListByProduct` container with `id="reviews"`. `id` must travel to new position (before itinerary). ExperienceTitleArea's `href="#reviews"` breaks if id absent.
  2. `galleryRef = useRef(null)` — on `AirbnbPhotoGrid` container.
  3. `useEffect` on `router.asPath` + `router.events.on('routeChangeComplete')` — calls `scrollIntoView` with 100ms delay for `#reviews` and `#gallery`.
  4. Client-side review fetch `useEffect` — fetches `/product-detail/{slug}/` after SSG hydration. `reviews` lives in `useState(initialContract?.reviews || [])`, NOT read from `contract` directly. Drop this and reviews are blank on first ISR-cached load.
- Keep: `DayTripMobileBookingBar`
- Keep: `DynamicDayTripBookingWidget` import (used inside PremiumBookingPanel)

### `DayTripBookingWidget.js` — minor modification
- **Remove `StickySidebar` wrapper** from `return` statement (line 374)
- Change `return (<StickySidebar><Card...>` → `return (<Card...>`
- Import `StickySidebar` removed from this file
- Booking logic, state, props — unchanged

### Files NOT modified
- `pages/activities/detail/[...slug].js` — SSG/ISR untouched
- `DayTripDetailSEO.js` — SEO unchanged
- `DayTripContent.js` — kept, not imported in page
- `DayTripHighlights.js` — kept, not imported in page
- `DayTripDetailHeader.js` — **retired, not deleted.** Step 7 rewrite removes its import and replaces with `ExperienceTitleArea.js`. File itself not edited — swap happens entirely in `DayTripDetailPage.js`. Do not import both: DayTripDetailHeader renders breadcrumbs, h1, rating, duration, operator logo, and all badge chips — same territory as ExperienceTitleArea.

---

## Reuse Map

| Existing | Used By |
|----------|---------|
| `AverageRating` | `ExperienceTitleArea`, `PremiumBookingPanel` |
| `ReviewListByProduct` | Page (unchanged, moved up) |
| `TimelineDisplay` | Page (wrapped, unchanged) |
| `DayTripBookingWidget` | `PremiumBookingPanel` (wrapped) |
| `DayTripCard` | `RelatedExperiences` |
| `HTMLContentRenderer` | `ExperienceHighlights`, `IncludedExcluded`, `MeetingPointCard`, `ExperienceFAQ` |
| `PricingDisplay` | `PremiumBookingPanel` |
| `FeaturedImageHeader` | `AirbnbPhotoGrid` (mobile) |
| `StandardBreadcrumb` | `ExperienceTitleArea` |
| `COLORS`, `TYPOGRAPHY_SCALE`, `BORDER_RADIUS` from `designSystem.js` | All new components |
| `MEETING_POINT_TYPE_LABELS` (existing constant) | `WhyTravelersLove`, `MeetingPointCard` |
| `useGetContractsQuery` from `dayTripsApi` | `RelatedExperiences` |

---

## API Data Available (no new endpoints needed)

All from `GET /product-detail/{slug}/`:
- `name` / `translated_name`, `slug`
- `average_rating` / `rating`, `review_count`, `reviews[]`
- `featured_image`, `image[]`
- `tour_highlights` / `translated_highlights` (HTML)
- `description` / `translated_description` (HTML)
- `inclusions` / `translated_inclusions` (HTML)
- `exclusions` / `translated_exclusions` (HTML)
- `what_to_bring` / `translated_what_to_bring` (HTML)
- `age_restriction` (string)
- `ratecards[]` with `selling_rate`, `rate_card_type`, `rate_date`
- `timeline.timeline_place[]`
- `meeting_point_type`, `meeting_point_details` / `translated_meeting_point_details`
- `operator.operator_name`, `operator.operator_logo`
- `tour_duration_days`, `max_participants`, `transport_composit[]`
- `service_category`, `difficulty_level`
- `extra[]` — `{ type: 'FEATURE', item: string }` — source for trust badges (Free Cancellation, Hotel Pickup, etc.)

---

## Implementation Sequence

1. `AirbnbPhotoGrid.js` — lowest risk, pure display
2. `ExperienceTitleArea.js` — reuse-heavy
3. Stateless batch: `ExperienceHighlights.js`, `WhyTravelersLove.js`, `IncludedExcluded.js`, `MeetingPointCard.js`, `ExperienceFAQ.js`
4. **`DayTripBookingWidget.js`** — remove `StickySidebar` from return (line 373), remove StickySidebar import. **Hard prerequisite for Step 5.** Double-sticky produces no runtime error — just broken stickiness. Commit and smoke-test booking widget standalone before starting Step 5.
5. `PremiumBookingPanel.js` — only start after Step 4 committed. Verify booking still works with StickySidebar at page level.
6. `RelatedExperiences.js` — new RTK fetch
7. `DayTripDetailPage.js` rewrite — last, all components built; right column wraps PremiumBookingPanel in StickySidebar

---

## Verification

**After each component:** No console errors, correct data at 1280px / 768px / 375px.

**Integration:**
- `#reviews` hash scrolls to reviews
- `#gallery` hash scrolls to photo grid
- Date selection triggers ratecard refetch
- Booking widget adds to cart
- Mobile: single column, `DayTripMobileBookingBar` visible

**Edge cases:**
- 1 image → single hero, no crash
- Empty `tour_highlights` → fallback to HTML blob
- No inclusions → section hidden
- No reviews → "No reviews yet"
- No timeline → wrapper hidden

**Build:** `npm run build` clean. `RelatedExperiences` must be `ssr: false`.

---

## Related

- [[experiences-2026-marketplace-redesign]] — browse page redesign (Phase 1 shipped)
- [[trip-detail-deep-review]] — prior detail page audit
- [[trip-detail-page-review]] — prior design review
- [[design-system-audit-2026-05-31]] — design tokens in use
- [[smartenplus-2026-ux-direction]] — overall UX direction

---

## Scrutiny Notes (2026-06-02, session #31)

Codebase verified post-spec. Four issues found and resolved above.

| # | Finding | Resolution |
|---|---------|------------|
| A | `DayTripDetailHeader.js` overlap with `ExperienceTitleArea.js` — spec said "not modified" without clarifying import is removed in Step 7 | Retirement note added to Files NOT Modified |
| B | `useGetContractsQuery` has no `exclude_slug` param — current contract silently appears in own Related list | Client-side filter documented in RelatedExperiences.js spec |
| C | Step 4→5 hard dependency not explicit in sequence — double-sticky breaks silently | Prerequisite language added to Steps 4 and 5 |
| D | Hash nav has 4 moving parts — "Keep: all refs" too easy to skim past during rewrite | Full breakdown added to DayTripDetailPage.js rewrite notes |
