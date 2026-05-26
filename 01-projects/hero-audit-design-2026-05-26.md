# Hero Section Design Audit — Visual Design

## Homepage Hero (homepagev2.js)

| Aspect | Detail |
|--------|--------|
| Height | `min-h-screen` (full viewport, cinematic) |
| Typography — H1 | `text-lg md:text-2xl lg:text-3xl font-bold` |
| Typography — subtitle | `text-xs md:text-sm lg:text-base` |
| Background | Hero banner carousel (5s interval), `hero-top-gradient` overlay, dynamic dominant-color fallback gradient |
| Overlay effect | 3-stop gradient: `rgba(0,0,0,0.50)` 0%, `rgba(0,0,0,0.20)` 35%, `transparent` 65% |
| CTA | White search form panel (`bg-white mx-2 md:mx-3 p-2 rounded sm:rounded-lg`) — positioned below headline |
| Content layout | Centered text block + search panel beneath, `ScrollIndicator` |
| isCinematic | true — removes back button/share, uses full-bleed inset |

## Destinations Hero (/pages/destinations/index.js)

| Aspect | Detail |
|--------|--------|
| Height | Default: `min-h-[200px] sm:min-h-[250px] md:min-h-[460px]` |
| Typography — H1 | `text-lg md:text-2xl lg:text-3xl font-bold` |
| Background | Static `bgDefault` image, `hero-top-gradient` overlay |
| Overlay effect | Same 3-stop gradient as homepage |
| CTA | MUI-based `SearchBar` component + `StatsDisplay` |
| Content layout | Centered headline + search + stats, all within hero |
| isCinematic | false (default) |

## Blog Index Hero (/pages/blog/index.js)

| Aspect | Detail |
|--------|--------|
| Height | Default: `min-h-[200px] sm:min-h-[250px] md:min-h-[460px]` |
| Typography — H1 | `text-2xl md:text-4xl lg:text-5xl font-bold` — significantly larger than other heroes |
| Background | First post's featured image (dynamic), `hero-top-gradient` overlay |
| Overlay effect | Same 3-stop gradient |
| CTA | WordPress `Search` component |
| Content layout | Centered headline + search, no supporting info |
| isCinematic | false (default) |
| Action button | `DynamicCategoryMenu` rendered as `actionButton` prop (positioned bottom-right) |

## Trip Detail Hero (TripDetailHero + FeaturedImageHeader, /pages/trips/detail/[...slug].js)

| Aspect | Detail |
|--------|--------|
| Height | Default: `min-h-[200px] sm:min-h-[250px] md:min-h-[460px]` |
| Typography — H1 | `text-base sm:text-xl md:text-3xl font-semibold` — smallest headline weight |
| Additional metadata | Product type badge (`bg-gray-500/50 border rounded-md`), departure/arrival times, passenger count, operator link |
| Background | Product cover image, `hero-top-gradient` overlay, `bgDefault` fallback |
| Overlay effect | Same 3-stop gradient |
| CTA | No search form — metadata only |
| Content layout | Centered headline with metadata row below |
| isCinematic | false (default) |

## Homepage v1 Hero (homepagev1.js)

| Aspect | Detail |
|--------|--------|
| Height | `min-h-[460px]` |
| Typography — H1 | `text-lg md:text-2xl lg:text-3xl font-bold` |
| Background | Static `bgDefault`, `hero-top-gradient` overlay |
| Overlay effect | Same 3-stop gradient |
| CTA | White search form panel + `RecentSearch` component |
| Content layout | Same pattern as v2 — headline + search panel |
| isCinematic | false (uses explicit height) |

## Activities Browse Hero (/pages/activities/index.js — FilterDayTripsPage)

| Aspect | Detail |
|--------|--------|
| Height | **No hero image at all** — plain `max-w-[1200px] mx-auto p-2 pb-6 sm:py-8` section |
| Typography — H1 | MUI `Typography variant="h4"` → `font-size: 1.5rem sm:2rem` |
| Background | None — no image/gradient |
| CTA | None |
| Content layout | Standard page content with no visual hero treatment |

## Comparison Table

| Aspect | Homepage v2 | Destinations | Blog | Trip Detail | Homepage v1 | Activities Browse |
|--------|-------------|--------------|------|-------------|-------------|------------------|
| **Height** | `min-h-screen` | `md:min-h-[460px]` | `md:min-h-[460px]` | `md:min-h-[460px]` | `min-h-[460px]` | None |
| **H1 size** | `lg:text-3xl` | `lg:text-3xl` | `lg:text-5xl` | `md:text-3xl` | `lg:text-3xl` | `sm:text-2xl` |
| **H1 weight** | Bold | Bold | Bold | Semibold | Bold | Bold |
| **Hero image** | Rotating banner | Static | First post image | Product image | Static | None |
| **Overlay gradient** | Yes | Yes | Yes | Yes | Yes | N/A |
| **Search CTA** | White panel form | SearchBar component | Search component | None | White panel form | None |
| **isCinematic** | true | false | false | false | false | N/A |
| **Back button** | Hidden | Shown | Shown | Shown | Shown | N/A |

## Inconsistencies Found

1. **[High-Priority] Activities browse has no visual hero**
   The `/activities` page lacks any hero image, gradient, or banner — it opens directly into a filter section with just a Typography heading. This creates a jarring contrast against all other content pages which have at least a FeaturedImageHeader. User jumps from nav directly into content with no visual arrival moment.

2. **[High-Priority] Hero H1 sizes are inconsistent**
   - Blog index: `text-5xl` at lg — the largest headline
   - Homepage v2: `text-3xl` at lg — 40% smaller than blog
   - Destinations: `text-3xl` at lg — matches homepage
   - Trip detail: `text-3xl` at md, `font-semibold` (lighter weight) — smallest visual weight despite being a detail page
   No consistent scale. Blog's oversized H1 is especially jarring next to the more restrained homepage.

3. **[High-Priority] Homepage v2 uses `min-h-screen` while every other page uses `md:min-h-[460px]`**
   The homepage is the only page that goes full-viewport height. This breaks visual rhythm when navigating to any sub-page — the hero collapses from full-screen to 460px. If full-screen is intentional for the homepage impact, it should be a deliberate brand decision documented.

4. **[Medium-Priority] Trip detail H1 weight is semibold vs bold everywhere else**
   `text-base sm:text-xl md:text-3xl font-semibold` vs the standard `font-bold` used on homepage, destinations, blog, and homepage v1. This makes trip detail headlines feel visually lighter/less important than they should be.

5. **[Medium-Priority] Blog hero uses dynamic image (first post) while others use static/default**
   Blog index shows the first post's featured image as the hero background — if the first post changes, the hero changes. All other pages use a stable branded image or product image. This could result in an off-brand hero if a post has an unusual image.

6. **[Medium-Priority] No hero CTA button style consistency**
   - Homepage v1/v2: White rounded panel containing the search form
   - Destinations: SearchBar component (MUI) + StatsDisplay below
   - Blog: WordPress Search component
   - Trip detail: No CTA at all
   The "CTA" treatment varies significantly — there is no shared button/panel style that carries across pages.

7. **[Nitpick] Blog H1 (`SmartEnPlus Blogs`) is redundant with page title**
   H1 reads "SmartEnPlus Blogs" — the `FeaturedImageHeader` title prop also passes `"SmartEnPlus Blogs - Page Header Image"` for the image alt text. This double-mention of the brand name in the hero is redundant and wastes valuable headline space.

8. **[Nitpick] Trip detail hero metadata row is cramped**
   The metadata row (`type badge | departure time | operator link | rating`) mixes icon + text with different font sizes (`text-xs sm:text-sm`). On mobile it wraps awkwardly and the `bg-gray-500/50` badge has no responsive size adjustment.

## Recommendation

1. **Define a hero baseline** — Pick one height value (likely `md:min-h-[460px]`) as the standard for all content pages. Homepage can override with `min-h-screen` only if that visual weight is intentional and documented.

2. **Unify H1 typography** — Settle on one responsive scale and weight. The blog's `text-5xl` should come down to match the rest (`text-3xl`). Trip detail should use `font-bold` instead of `font-semibold`.

3. **Add hero to Activities browse** — Either add a `FeaturedImageHeader` with a static branded image, or investigate if the page should share the same hero pattern as other browse pages.

4. **Standardize CTA treatment** — Pick one pattern (white panel vs embedded component) and apply consistently. Trip detail currently has no hero CTA which may be intentional but looks incomplete next to homepage and destinations.

5. **Lock blog hero image** — Use a dedicated branded banner image rather than dynamically deriving from the first post's featured image.
