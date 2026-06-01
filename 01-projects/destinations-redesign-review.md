# Destinations Section Redesign Review — 2026-05-29
**Section:** "Popular Travel Destinations" → "Thailand's Top Destinations"
**Branch:** `260528-feat/header-redesign-2026`
**Status:** Research complete — implementation approved pending contrast audit

## Files Under Review
`LocationsSection.js` (wrapper), `LocationGridComponent.js` (grid, homepage-only replace), `LocationsStructuredData.js` (JSON-LD), `LocationsErrorBoundary.js`, `LocationsSkeletonLoader.js`, `pages/homepagev2.js:359` (integration point). Current data shape: `{ location_name, route_count, image }`.

## UX Audit — Composite Score: 22/80 (28%)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Visual Hierarchy | 2/10 | `isFirst` flag drives `loading="eager"` only — zero visual distinction. All 7 cards identical size, weight, overlay. |
| Booking Intent Support | 3/10 | Cards link to `/locations/{slug}` listing page. No price, no departure context, no direct booking affordance. Two hops from booking. |
| Emotional Framing | 2/10 | Only metadata: `(N trips)` — supply count. Nothing communicates "beach escape" or "overnight train." |
| Information Density | 3/10 | Too sparse (no price, no travel time) AND too compressed — name + count crammed into `min-h-[64px]`. |
| Photography Quality Perception | 3/10 | Hardcoded `bg-black bg-opacity-40` on every card regardless of image luminosity. `DEFAULT_ROUTE_IMAGE` fallback can repeat across multiple cards. |
| CTA Effectiveness | 2/10 | "Explore More..." rendered as `bg-gray-100 rounded` div consuming a full grid slot — no icon, no count, reads as maintenance link. |
| Mobile Experience | 4/10 | `grid-cols-1` fallback ok, `min-h-[64px]` too short for image crop |
| Section Title Clarity | 3/10 | Generic. Works on any travel site. |

### Problem Validation
| Problem | Verdict | Evidence |
|---------|---------|----------|
| All cards identical — no hierarchy | CONFIRMED | `isFirst` only affects `loading` prop. No visual difference card 1 vs card 7. |
| Repeated dark overlays feel low quality | CONFIRMED | `bg-black/40` hardcoded. `DEFAULT_ROUTE_IMAGE` fallback repeats. |
| "(11 trips)" not emotionally useful | CONFIRMED | Supply metadata, not user signal. Users evaluate via price anchors or qualitative tags. |
| "Explore More..." wastes space | CONFIRMED | Full grid cell, no imagery. Booking.com/GYG put CTA below grid. |
| Grid feels like sitemap | CONFIRMED | 7 equal-weight cards, no ordering signal. |
| Doesn't support booking intent | CONFIRMED | Links to listing page, not pre-filtered search. Extra hop. |
| Title generic | CONFIRMED | No Thailand specificity or transport context. |

### Platform Comparison — Key Differentiators
- **Airbnb:** Asymmetric masonry. Featured 2× space. Text below image, no overlay.
- **Booking.com:** Carousel of 3 large cards first. Shows property count + starting price. CTA below grid.
- **GetYourGuide:** Gradient overlay adapts to luminosity. CTA repeats destination name.
- **Klook:** 50/50 image/text. Star rating + "from [price]" + descriptor. Horizontal scroll mobile.

**Shared patterns absent from SmartEnPlus:** price anchor, editorial curation signal, gradient overlay, CTA outside grid, horizontal scroll mobile.

### Top 3 Highest-Impact Changes
1. **Surface "from price" anchor or qualitative tag** — converts browsing to comparison. Highest ROI.
2. **Hero card with asymmetric layout** — first card 2 columns / double height. `isFirst` exists, needs to drive visuals.
3. **Move "Explore More..." out of grid** — below-grid button. Card link: "Find routes to [destination]".

### What to Keep
`<article>` semantic markup with `itemScope` / `itemType="https://schema.org/TouristDestination"` + `aria-label` + `role="list"`/`role="listitem"`. WCAG 2.1 AA compliant. Preserve through redesign.

## Design Debate — VERDICT: MODIFIED BRIEF

### Q1: `rounded-2xl` → VERDICT: `rounded-xl`
Codebase drifted to `rounded-xl` (DiscoverySection, AccountCard, ProfileHeader, LocationCard). Current cards use bare `rounded` (4px). Add `imageCard: 'rounded-xl'` token.

### Q2: Asymmetric layout vs ContentCard → VERDICT: Skip ContentCard
`bg-white` irrelevant (photos fill cards), `overflow-hidden` belongs on cards not wrapper, `flex-col` blocks CSS grid. Use `Section` + local grid div — same as `PopularRoutesSection`.

### Q3: Section title → VERDICT: "Thailand's Top Destinations" + subtext
Subtext: `"Find bus, ferry & train routes."` Transport-explicit, editorial feel. Structured data carries SEO weight.

### Q4: Card count → VERDICT: 5–6 with `featured` flag
4 slots excludes Chiang Mai or Hat Yai. Use 5 min, 6 preferred. Negotiate `featured: boolean` with backend. Until landed, `index === 0` = featured.

### Q5: Traveler-context strings → VERDICT: Frontend copy map
Create `lib/homepage/data/destinationCopy.js` — slug-keyed `{ tag, context }` map. Null fallback: no badge.

### Q6: Mobile swipe → VERDICT: Reuse `CardCarouselContainer`
Mirror `PopularRoutesCarousel.js` pattern. `carouselBreakpoint="lg"`. Let container handle breakpoint internally.

### Design System Alignment
| Element | Decision |
|---------|----------|
| Card radius | `rounded-xl` (12px), add `imageCard` token |
| Section wrapper | Skip ContentCard; use Section directly |
| Heading | "Thailand's Top Destinations" + subtext |
| Overlay | `bg-black/25` rest, `bg-black/10` hover — verify WCAG |
| Whitespace | `gap-4 md:gap-6` destination grid only |
| Hover | `hover:scale-[1.03]` duration-200 |
| Mobile | Swipe via CardCarouselContainer |
| Route count | Remove from UI; keep in `aria-label` |
| CTA | Below-grid text link, brand primary color |

## Implementation Blueprint

### File Change Map
| File | Action |
|------|--------|
| `LocationGridComponent.js` | PRESERVE — used in locations + homepagev1 |
| `LocationsStructuredData.js` | PRESERVE — receives full array |
| `LocationsErrorBoundary.js` | PRESERVE |
| `helpers/designSystem.js` | MODIFY — add `imageCard: 'rounded-xl'` + `imageCard: '12px'` |
| `lib/homepage/data/destinationCopy.js` | CREATE — slug-keyed editorial copy |
| `DestinationsEditorialGrid.js` | CREATE — desktop asymmetric CSS grid (lg+) |
| `DestinationsCarousel.js` | CREATE — mobile/tablet carousel, mirrors PopularRoutesCarousel |
| `LocationsSection.js` | MODIFY — remove ContentCard + LocationGridComponent, add new components + GTM |
| `LocationsSkeletonLoader.js` | MODIFY — asymmetric 5-slot skeleton |
| `pages/homepagev2.js` | MODIFY — remove dead LocationGridComponent import (line 15) |

### DestinationsEditorialGrid.js
Props: `{ items, onItemClick, onItemHover }`. Internal `useMemo` processes: `slug`, `capitalizedLocation`, `imageUrl`, `routeCount`, `copy` (from DESTINATION_COPY), `isFeatured` (index===0), `isEager`, `index` (required for GTM).

**FeaturedCard** (items[0]): `rounded-xl overflow-hidden relative group`, `fill object-cover priority`, overlay `bg-black/25` → hover `bg-black/10`, content pinned bottom `p-4`, name `text-xl font-bold text-white`, tag badge conditional `bg-white/20 text-white rounded`, aria-label with routeCount.

**SupportingCard** (items[1-4]): same pattern, `text-base font-semibold`.

**Desktop grid** (`hidden md:grid`): `2fr 1fr gap-3`. Featured `row-span-2 min-h-[320px]`. Supporting[1-2] `col-start-2 min-h-[152px]`. Sub-row `col-span-2 grid-cols-2`, Supporting[3-4] `min-h-[180px]`.

### destinationCopy.js
Slug-keyed map: bangkok→"Bus & Train Hub", phuket→"Island Gateway", koh-samui→"Gulf Island", koh-lipe→"Remote Beach", hat-yai→"Southern Hub", krabi→"Andaman Base", chiang-mai→"Northern Capital", surat-thani→"Ferry Crossroads". Null fallback: no badge.

### LocationsSection.js
Remove: ContentCard, LocationGridComponent, limit={7}, showExploreLink. Add: DestinationsEditorialGrid, GTM tracking (`sendGTMEvent`), `useCallback` + `useRouter`. SectionHeader: `"Thailand's Top Destinations"` + subtext. Below-grid link: "See all destinations in Thailand →".

GTM events: `destination_click` (name, slug, position, featured, route_count), `destinations_see_all_click`.

### Build Sequence
1. `designSystem.js` token 2. `destinationCopy.js` 3. `DestinationsEditorialGrid.js` 4. `DestinationsCarousel.js` 5. `LocationsSection.js` 6. `LocationsSkeletonLoader.js` 7. Remove dead import 8. lint 9. smoke test 10. contrast audit

## Risk Flags
| Risk | Severity | Mitigation |
|------|----------|-----------|
| LocationGridComponent used elsewhere | HIGH | Do NOT modify. DestinationsEditorialGrid is homepage-only. |
| WCAG: bg-black/25 on light images may fail 4.5:1 | MEDIUM | Test actual images. Fallback: bg-black/35 or text-shadow. |
| ISR featured card stale after backend reorder | MEDIUM | Acceptable. Document assumption. Negotiate `featured` field. |
| Arbitrary Tailwind grid value purged | LOW | Verify content glob covers `lib/**/*.js`. |
| Dead LocationGridComponent import line 15 | LOW | Remove in same PR. |

## Verification Checklist
- Heading + subtext visible, 5 cards, no "(N trips)" text
- Featured card (index 0) spans left column double height
- Cards 4+5 in sub-row, "See all" below grid
- Mobile: carousel visible, all 5 swipeable
- Skeleton matches asymmetric layout
- `/locations` still renders LocationGridComponent (regression)
- JSON-LD `ItemList` in page source
- GTM events fire correctly, `npm run build` clean, WCAG contrast pass

## Scrutiny Notes (2026-05-29)
**M1:** `rounded-xl` justified by codebase drift, not ContentCard nesting. **M2:** Remove outer `md:hidden` wrapper — CardCarouselContainer handles breakpoint. **M3:** `carouselBreakpoint="lg"` not "md" — 2fr/1fr too cramped at 768px. **M4:** `index` must be in processedItems for GTM `destination_position`. Verdict: fix-then-ship, all implementation-level.

## Team Verdict
Proceed with modified brief: `rounded-xl`, skip ContentCard, "Thailand's Top Destinations" + subtext, 5 min destinations, frontend copy map, reuse CardCarouselContainer, `bg-black/25` pending contrast audit, include `index` in processedItems, remove dead import.
