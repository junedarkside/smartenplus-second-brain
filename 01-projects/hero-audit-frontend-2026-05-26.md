# Hero Section Frontend Audit

## Homepage Hero Implementation

**File:** `pages/homepagev2.js` (lines 388-413)

**Component:** `FeaturedImageHeader`
- Props: `title`, `imgUrl`, `customMinHeight="min-h-screen"`, `isCinematic=true`
- Child content: H1 title, subtitle paragraph, `ProductSearchForm2` wrapped in section with bg-white

**Styling:**
- Tailwind CSS: `absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full z-20 pt-[88px]`
- Hero banner cycling via `useState` + `useEffect` interval (5000ms)
- Image optimization: `getOptimizedImageSizes`, `getOptimalImageQuality`, `placeholder="blur"`, `priority=true`
- Dynamic color extraction via `ColorThief` with `requestIdleCallback`
- Cinematic gradient overlay via `hero-top-gradient` CSS class

**State Management:**
- Local state: `heroBannerIndex`, `heroBannerImage`
- Redux: pulls `fromLocation`, `toLocation`, `calendarStateDate`, `passengerTotal`, `isReturnTrip`

---

## Other Page Heroes Implementation

### 1. Trips Index (`pages/trips/index.js`)
**Component:** `FeaturedImageHeader`
- Props: `title`, `imgUrl={bgDefault}` (no `isCinematic`, no `customMinHeight`)
- Child content: H1 only (no search form)

**Styling:**
- Tailwind: `absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full z-20`
- No cinematic mode, no gradient overlay customization
- Default min-height: `min-h-[200px] sm:min-h-[250px] md:min-h-[460px]`

**State:** Local state for pagination, letter filter, sort type

---

### 2. Destinations (`pages/destinations/index.js`)
**Component:** `FeaturedImageHeader`
- Props: `title`, `imgUrl={bgDefault}`
- Child content: H1, `SearchBar` component, `StatsDisplay`

**Styling:**
- Tailwind: `absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full z-20`
- Same default min-height as trips index

---

### 3. Airport Transfers (`pages/airport-transfer/index.js`)
**Component:** `FeaturedImageHeader`
- Props: `title`, `imgUrl={airportThailand1Image}`
- Child content: H1 only

**Styling:** Same pattern as trips/index.js

---

### 4. Blog Index (`pages/blog/index.js`)
**Component:** `FeaturedImageHeader`
- Props: `title`, `imgUrl={pageDisplayImageSrc}`, `actionButton` (category menu)
- Child content: H1 "SmartEnPlus Blogs", `Search` component

**Styling:**
- Tailwind: `absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full z-20`
- Action button rendered in header's `actionButton` slot (bottom-right)

---

### 5. Blog Post Detail (`components/blog/BlogPostDisplay.js`)
**Component:** `DynamicFeaturedImageHeader` (dynamic import)
- Props: `title`, `imgUrl`, `blogTitle`
- Child content: H1 title, author avatar, date, reading time in footer area

**Styling:**
- Custom child placement: `absolute top-0 left-0 w-full h-full flex items-center justify-center` for H1
- Footer: `absolute bottom-0 w-full p-2` for metadata
- Uses `DynamicFeaturedImageHeader` (client-only) — SSR disabled

---

### 6. Search Results (`components/search/SearchCover.js`)
**Component:** `FeaturedImageHeader`
- Props: `title`, `imgUrl={coverImage || bgDefault}`
- Child content: H1 route display, trip mode chip, passenger selector button, "Edit search" trigger

**Styling:**
- Tailwind: `absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full z-20`
- Mobile: shows `FilterPopover` and filter IconButton at bottom

---

### 7. Activities Browse (`components/activities/browse/FilterDayTripsPage.js`)
**No hero component.** Simple MUI Typography header:
```jsx
<Typography variant="h4" component="h1">
  {filters.location ? `Day Trips in ${filters.location}` : 'Browse Day Trips'}
</Typography>
```
No background image, no `FeaturedImageHeader`.

---

### 8. Trip Detail (`pages/trips/[tripId].js`)
**No hero component.** Plain page with NextSEO. No `FeaturedImageHeader` at all.

---

## Component Reuse Analysis

| Page | Hero Component | Reusable? |
|------|---------------|-----------|
| Homepage | `FeaturedImageHeader` | Yes |
| Trips Index | `FeaturedImageHeader` | Yes |
| Destinations | `FeaturedImageHeader` | Yes |
| Airport Transfers | `FeaturedImageHeader` | Yes |
| Blog Index | `FeaturedImageHeader` | Yes |
| Blog Post | `FeaturedImageHeader` (dynamic) | Yes |
| Search Results | `FeaturedImageHeader` | Yes |
| Activities Browse | None | N/A |
| Trip Detail | None | N/A |

**Shared Hero Component:** `FeaturedImageHeader` in `components/UI/FeaturedImageHeader.js`

**Reuse Pattern:** `FeaturedImageHeader` is the standard hero. Two pages deviate:
- `pages/trips/[tripId].js` — no hero at all
- `components/activities/browse/FilterDayTripsPage.js` — text-only header

---

## Styling Inconsistencies

### 1. Cinematic Mode
- Homepage uses `isCinematic` prop — adds `hero-top-gradient` CSS class and `inset-0` layout
- Other pages do NOT use `isCinematic` — inconsistent visual treatment

### 2. Min-Height
- Homepage: `customMinHeight="min-h-screen"` (full viewport)
- Other pages: default `min-h-[200px] sm:min-h-[250px] md:min-h-[460px]`
- Destinations and Airport Transfers use default despite potentially wanting fuller heroes

### 3. Child Content Positioning
- Homepage: `pt-[88px]` offset for header
- Trips/Destinations/Airport: no offset
- Blog Post: uses `top-0 left-0` for H1 (centered in image), `bottom-0` for metadata
- SearchCover: standard `top-1/2` but with additional mobile filter bar at `bottom-0`

### 4. Dynamic Image Imports
- Blog Post uses `DynamicFeaturedImageHeader` (client-only)
- All others use static import
- Blog Post's `DynamicFeaturedImageHeader` is the same component, just deferred

### 5. Gradient/CSS Classes
- `hero-top-gradient` class applied via `FeaturedImageHeader` internal CSS when `isCinematic`
- No consistent gradient across non-cinematic heroes
- `lg:rounded-b-lg` applied to image in non-cinematic mode only

---

## Technical Inconsistencies

### 1. State Management
- Homepage: Redux state + local state (banner cycling)
- Trips Index: local state only (pagination, filters)
- Destinations: local state only (search, sort, expand)
- Airport Transfers: local state only
- Blog Index: local state (load more)
- Blog Post: local state via hooks + Redux (some analytics)
- SearchCover: Redux + local state
- Activities Browse: local state only
- Trip Detail: local state only

### 2. Dynamic Imports
- Blog Post uses `dynamic(() => import('../UI/FeaturedImageHeader'), { ssr: true })`
- Homepage and others use static import
- Blog Index uses `DynamicCategoryMenu` but static `FeaturedImageHeader`

### 3. Image Optimization
- Homepage: full optimization (`getOptimizedImageSizes`, `getOptimalImageQuality`, `placeholder="blur"`, `priority`, `fill`)
- Other pages: `fill` + `style={{ objectFit: "cover" }}` + `priority` + `placeholder="blur"` (varies)
- `getOptimizedImageSizes` and `getOptimalImageQuality` helpers not used consistently outside homepage

### 4. Color Extraction
- Homepage: `ColorThief` for dominant color background gradient
- Other pages: default gray `rgb(156, 163, 175)` hardcoded

### 5. SEO Approach
- Homepage: inline JSON-LD scripts, `WebPageJsonLd`, `BreadcrumbJsonLd`
- Blog Post: via `BlogPostHeader` component (NextSeo + schema generator)
- Blog Index: via `BlogPageWrapper` + SEO config object
- Other pages: `NextSeo` directly + `<Head>` for pagination links

---

## Recommendations

### High Priority
1. **Standardize hero min-height** — homepage uses `min-h-screen`, others use `md:min-h-[460px]`. Document when each applies or create prop variant (`fullHeight` vs `standard`).

2. **Standardize cinematic mode** — if homepage's `isCinematic` pattern is the desired "featured" look, apply it to Destinations and Airport Transfers too. If not, remove it from homepage for consistency.

3. **Activities/Trip Detail pages need heroes** — `FilterDayTripsPage` and `pages/trips/[tripId].js` lack any visual header. Consider adding `FeaturedImageHeader` for visual consistency.

### Medium Priority
4. **Consistent image optimization** — extract `getOptimizedImageSizes`/`getOptimalImageQuality` usage into `FeaturedImageHeader` itself so all callers get optimized images automatically.

5. **Centralize color extraction** — the `ColorThief` extraction is homepage-only. Either generalize it in `FeaturedImageHeader` as an optional prop, or document that non-homepage heroes use static fallback.

6. **Standardize dynamic import pattern** — Blog Post's `DynamicFeaturedImageHeader` suggests SSR concerns. Audit whether other pages should also use dynamic import.

### Low Priority
7. **Unify SEO setup** — homepage, blog index, blog post each use different SEO patterns (inline JSON-LD vs NextSeo wrapper vs component). Consider a shared `PageHero` wrapper that includes SEO.

8. **Document hero composition rules** — create ADR or update CODE_PATTERNS.md: when to use `isCinematic`, when to include search forms vs plain H1, responsive behavior expectations.
