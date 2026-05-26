# Hero Section UX Audit

Dated: 2026-05-26
Scope: Homepage, Trip Detail, Activities Browse, Activities Detail, Search Results, Destinations

---

## Homepage Hero UX

**Component:** `FeaturedImageHeader` + `ProductSearchForm2`

- **Hero style:** Full-screen cinematic (`isCinematic`, `customMinHeight="min-h-screen"`)
- **Hero content:** Marketing title + tagline "Book buses, ferries and trains across Thailand -- instantly confirmed." + embedded search form
- **Search placement:** Embedded directly in hero, centered, full-width within hero bounds
- **Banner rotation:** Auto-rotating hero banners (`heroBanners`) with 5s interval
- **Trust indicators:** None in hero; reviews section appears below fold
- **Scroll indicator:** Yes (down arrow)
- **Navigation integration:** None in hero; sticky header above hero
- **Content hierarchy:** Marketing message first, functional search second

---

## Other Page Heroes UX

### Trip Detail (`trips/detail/[...slug].js`)

**Component:** `TripDetailHero` wrapping `FeaturedImageHeader` (non-cinematic)

- **Hero style:** Standard `FeaturedImageHeader` with gradient overlay, `min-h-[200px] sm:min-h-[250px] md:min-h-[460px]`
- **Hero content:** Route name (H1), type badge, departure/arrival times (transportation only), passenger count, operator name + rating
- **Search placement:** None in hero
- **Trust indicators:** Average rating + review count in hero
- **Cinematic:** No
- **Content hierarchy:** Trip identity first, functional info second

### Activities Browse (`activities/index.js`)

**Component:** None (no `FeaturedImageHeader`)

- **Hero style:** No image hero at all
- **Hero content:** Typography page header "Browse Day Trips" or "Day Trips in {location}", description text
- **Search placement:** Location search below header, text search below that -- both functional, below the fold
- **Trust indicators:** None
- **Content hierarchy:** Filter-first UI, no marketing message

### Activities Detail (`activities/detail/[...slug].js`)

**Component:** `DayTripHero` wrapping `FeaturedImageHeader`

- **Hero style:** Standard `FeaturedImageHeader`, image-focused with minimal overlay
- **Hero content:** "View X Photos" button only; tour name/rating/duration moved to `DayTripDetailHeader` below hero
- **Search placement:** None in hero; `DayTripBookingWidget` appears in sticky sidebar
- **Trust indicators:** Rating/reviews in `DayTripDetailHeader` (below hero fold)
- **Design rationale:** Image-focused, follows Airbnb/GetYourGuide pattern

### Search Results / Trips Browse (`trips/index.js`)

**Component:** `FeaturedImageHeader` with static default image

- **Hero style:** Standard, static background (no cinematic, no rotation)
- **Hero content:** "Explore Thailand's Travel Routes" overlay title + H1 `h1PageTitle`
- **Search placement:** Search form in main content area, NOT in hero
- **Trust indicators:** None
- **Content hierarchy:** Marketing-style hero but no functional search in hero

### Destinations (`destinations/index.js`)

**Component:** `FeaturedImageHeader`

- **Hero style:** Standard, static image, full-width overlay
- **Hero content:** "Thailand All Destinations" title + `SearchBar` component + `StatsDisplay` (location/station counts)
- **Search placement:** Search bar embedded in hero
- **Trust indicators:** Stats (location count, station count)
- **Content hierarchy:** Functional (search) + informational (stats)

---

## UX Inconsistencies

| Pattern | Homepage | Trip Detail | Activities Browse | Activities Detail | Trips Browse | Destinations |
|---------|----------|-------------|------------------|------------------|--------------|--------------|
| Full-screen hero | Yes (cinematic) | No | No hero | No | No | No |
| Hero image rotation | Yes (banners) | No | N/A | No | No | No |
| Search in hero | Yes, embedded | No | No (below fold) | No | No | Yes (SearchBar) |
| Marketing message in hero | Yes | No | No | No | Yes (thin) | No |
| Trust in hero | No | Rating | No | No | No | Stats |
| Cinematic mode | Yes | No | N/A | No | No | No |
| Scroll indicator | Yes | No | N/A | No | No | No |
| Back button in hero | No (cinematic) | Yes (non-cinematic) | N/A | No | Yes | Yes |

**Key inconsistencies:**

1. **Search visibility:** Homepage embeds search in hero; every other page buries search below the fold. Users arriving from marketing channels (ads, links) expecting to search immediately must scroll first on non-homepage pages.

2. **Cinematic vs standard heroes:** Homepage uses `isCinematic` full-screen; Trip Detail and Activities Detail use standard heroes with more overlay content. The visual weight difference is dramatic.

3. **Marketing message presence:** Homepage hero has a clear marketing tagline. Destinations hero has functional stats. Activities Detail has no marketing copy at all. Trip Detail has product facts but no brand message.

4. **Back button visibility:** Non-cinematic heroes show a back button; cinematic hero (homepage) suppresses it. This creates a navigation asymmetry for users who arrive at the homepage from external links.

5. **Activities Browse has no image hero:** Unique among major pages -- uses a plain Typography header with filters below. Breaks the visual pattern established by all other pages.

---

## User Flow Impact

- **Discovery flow:** Homepage hero presents search immediately -- good for direct traffic. Non-homepage pages require scroll before search, creating friction for users who land on inner pages via deep links or back buttons.

- **Trust gap at conversion:** Homepage hero lacks trust signals (no ratings in hero); Trip Detail hero includes ratings. A user in the consideration phase on the homepage cannot assess quality without scrolling.

- **Mobile experience:** Full-screen cinematic hero on mobile may push search below fold on small screens (the search form has `min-h-[300px]` on mobile). Activities Browse collapses filters naturally. Inconsistent mobile hierarchy.

- **Activities users:** Users browsing `/activities` see no hero image at all -- the page feels like a utility tool, not a travel inspiration surface. Compare to GetYourGuide or Airbnb activities pages which always lead with imagery.

---

## Recommendations

1. **Standardize hero search:** Add a search entry point to the hero of Trip Detail, Activities Detail, and Trips Browse -- either embedded (like homepage) or as a CTA linking to the search experience. Homepage pattern is strongest for conversion.

2. **Consider a lightweight hero for Activities Browse:** At minimum a thematic background image with a compact search bar (like Destinations). Remove "Browse Day Trips" as a plain Typography header.

3. **Trust signals in homepage hero:** Add average rating or review count to homepage hero, similar to how Trip Detail surfaces it. Even a small badge would reduce trust gap.

4. **Resolve cinematic toggle:** The `isCinematic` prop suppresses the back button and changes layout behavior. Consider whether homepage should remain cinematic or adopt the standard hero pattern with search more prominently surfaced.

5. **Consistent scroll indicator:** Add `ScrollIndicator` to other full-viewport-height heroes (if any) for consistent "there is more content" signaling.
