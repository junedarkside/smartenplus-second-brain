# FeaturedImageHeader Usage Matrix

## Summary
Cross-page comparison of `FeaturedImageHeader` component usage. 12 pages audited — 10 use the component, 2 have no hero. Identifies inconsistencies in cinematic mode, min-height, search CTA, and H1 typography.

## Context
`FeaturedImageHeader` (`components/UI/FeaturedImageHeader.js`) is the shared hero component. Props: `title`, `imgUrl`, `children`, `actionButton`, `customMinHeight`, `blogTitle`, `onImageLoad`, `onImageError`, `imageLoaded`, `isCinematic`. Container defaults: `min-h-[200px] sm:min-h-[250px] md:min-h-[460px]`.

## Usage Matrix

| Page | Component | Cinematic | Min-Height | Search in Hero | H1 Size | H1 Weight |
|------|-----------|-----------|------------|----------------|---------|-----------|
| Homepage v2 | `FeaturedImageHeader` | Yes | `min-h-screen` | Yes (ProductSearchForm) | `lg:text-3xl` | Bold |
| Homepage v1 | `FeaturedImageHeader` | No | `min-h-[460px]` | Yes (ProductSearchForm) | `lg:text-3xl` | Bold |
| Destinations | `FeaturedImageHeader` | No | `md:min-h-[460px]` | Yes (SearchBar) | `lg:text-3xl` | Bold |
| Trips Index | `FeaturedImageHeader` | No | `md:min-h-[460px]` | No | `lg:text-3xl` | Bold |
| Blog Index | `FeaturedImageHeader` | No | `md:min-h-[460px]` | Yes (WP Search) | `lg:text-5xl` | Bold |
| Blog Post | `FeaturedImageHeader` (dynamic) | No | `md:min-h-[460px]` | No | `lg:text-5xl` | Bold |
| Trip Detail | `FeaturedImageHeader` | No | `md:min-h-[460px]` | No | `md:text-3xl` | Semibold |
| Activities Detail | `FeaturedImageHeader` | No | `md:min-h-[460px]` | No | — | — |
| Search Results | `FeaturedImageHeader` | No | `md:min-h-[460px]` | No | — | — |
| Airport Transfers | `FeaturedImageHeader` | No | `md:min-h-[460px]` | No | `lg:text-3xl` | Bold |
| **Activities Browse** | **None** | N/A | None | No | MUI h4 | Bold |
| **Trip Detail (by ID)** | **None** | N/A | None | No | — | — |

## Key Inconsistencies

1. **Homepage `min-h-screen`** vs all others `md:min-h-[460px]` — jarring visual drop navigating from homepage
2. **Blog H1 `text-5xl`** — 67% larger than homepage `text-3xl`
3. **Trip Detail `font-semibold`** — lighter weight vs `font-bold` everywhere else
4. **2 pages have no hero at all** — Activities Browse (MUI Typography), Trip Detail by ID
5. **No consistent CTA treatment** — white panel / MUI SearchBar / WP Search / none
6. **`isCinematic` homepage-only** — suppresses back button, uses `inset-0` layout
7. **ColorThief dynamic gradient** — homepage only. Other pages use gray `rgb(156, 163, 175)` fallback

## 2026 Direction
Per [[smartenplus-2026-ux-direction]]: reduce homepage to 55-60vh, standardize `font-bold` + `text-3xl` H1 everywhere, add heroes to Activities Browse and Trip Detail by ID.

## Related
- [[hero-section-comprehensive-audit-2026-05-26]] — Full audit with fix recommendations
- [[hero-88px-gap-root-cause]] — 88px gap between header and hero on non-homepage pages
- [[smartenplus-2026-ux-direction]] — Strategic hero height direction (45-60vh)
- [[design-systems]] — Design token reference
- [[smartenplus-wireframe-architecture]] — Full platform wireframe IA
