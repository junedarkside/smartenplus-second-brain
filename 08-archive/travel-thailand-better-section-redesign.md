# Travel Thailand Better — Section Redesign

## Summary
Replace 3 editorial homepage sections with 1 unified "Travel Thailand Better" section. 1 featured card + 2 secondary cards. Conversion-supportive, not editorial.

## Context

Homepage had 3 separate content sections:
- "Discover Thailand: Guides" (`GuidesSection.js`)
- "Thailand Travel Updates" (`PostSection` news)
- "Travel Stories & Updates" (`PostSection` activities)

This created editorial overload, visual clutter, and confused product identity ("Is this a booking platform or a blog?"). Users scroll past 3 sections of undifferentiated cards. Inspired by GetYourGuide/Klook/Omio — content used sparingly and conversion-supportive.

## Decision

**One section. "Travel Thailand Better."**

- Title: "Travel Thailand Better"
- Subtitle: "Helpful guides and tips to plan your journey with confidence."
- CTA: "View all guides →" top-right → `/blog`
- Positioning: travel assistance / trip planning support, NOT editorial magazine

## Layout

```
Desktop:
┌─────────────────────────────────┬──────────────────┐
│   Featured card (FEATURED badge)│  Secondary card  │
│   Large image top               │  ──────────────  │
│   Title + excerpt + meta below  │  Secondary card  │
└─────────────────────────────────┴──────────────────┘

Mobile: stacked single column, featured first
```

Card anatomy:
- Image top (gray placeholder if no featured image)
- `FEATURED` badge — blue pill, featured card only
- Title bold, 2-line clamp
- Excerpt 2-line clamp, text-gray-500 text-sm
- Meta: clock icon + "X min read" | date (text-xs text-gray-400)

## Implementation

**New file:** `lib/homepage/components/TravelThailandBetterSection.js`
- Data: `data[0]` = featured, `data.slice(1,3)` = secondary
- Data source: `Data` prop (recentPosts from `GET_HOMEPAGE_WORDPRESS_DATA`) — no new API
- Image: `item.node.featuredImage?.node?.sourceUrl`
- URL routing: isFAQ → `/help/faqs/slug`, else `/blog/slug` (same as BlogCardContainer)
- Read time: derived from excerpt word count (`Math.ceil(words / 200)`)
- Date: `date-fns` format `'MMM d, yyyy'`
- Structured data: reuse `GuidesSectionStructuredData` with `data.slice(0,3)`
- NO `ContentCard` wrapper (hardcoded bg-white, cannot override — per CLAUDE.md guardrail)

**Modified:** `pages/homepagev2.js`
- Remove `GuidesSection`, `PostSection` imports
- Remove `SECTION_CONFIGS` object
- Replace 3 section JSX blocks with `<TravelThailandBetterSection data={Data} />`
- Keep `getStaticProps` data fetching intact (WP data still fetched for other uses)

**Kept intact (not deleted):**
- `GuidesSection.js` — other pages may use
- `PostSection.js` — other pages may use
- `BlogCard.js`, `BlogCardContainer.js`
- `newsData`, `activitiesData` fetch in `getStaticProps`

## Homepage Section Order (after redesign)
1. Header
2. DiscoverySection (search hero)
3. PopularRoutesSection
4. LocationsSection
5. ReviewsSection
6. ThailandTravel
7. AirportTransferSection
8. **TravelThailandBetterSection** ← replaces 3 sections
9. MyBookingsSection
10. CustomerServiceSection

## Status

**COMPLETED 2026-05-29.** Commit `ce4d2d7` on `260528-feat/header-redesign-2026`. Pushed to remote.

### What shipped vs spec

| Spec | Shipped | Delta |
|------|---------|-------|
| 1 featured + 2 secondary cards | ✓ | — |
| Featured: image top h-[240px], FEATURED badge, title, excerpt, date | ✓ | — |
| Secondary: image fills card height (flex-1 min-h-[120px]), title only | ✓ | Secondary image is flex-1 not fixed — fills to match featured height |
| AutoStoriesOutlined icon in section header | ✓ | Added in session |
| Subtitle "Helpful guides…" | Removed | User requested removal |
| `lib/**` added to tailwind.config.js content | ✓ | Bug fix — was missing, caused all Tailwind classes to be absent |
| Read time (clock + X min) | Not shipped | Out of scope for now |
| Structured data reuse | Not shipped | Deferred |

### Root Cause Bug Fixed
Tailwind JIT did not scan `lib/` directory. Added `'./lib/**/*.{js,ts,jsx,tsx}'` to `tailwind.config.js` content array.

Branch: `260528-feat/header-redesign-2026` (pushed, not yet merged to main)

## Related

- [[header-redesign-2026-implementation]]
- [[smartenplus-2026-ux-direction]]
- [[smartenplus-product-positioning]]
- [[homepage-ux-review-2026-05-21]]
- [[carousel-design-standard]]
