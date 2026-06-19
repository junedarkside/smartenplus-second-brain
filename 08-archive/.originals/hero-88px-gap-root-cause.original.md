# Hero 88px Gap — Root Cause

## Summary
88px white gap between header bottom and hero image on non-homepage pages. Caused by double-offset: sticky header reserves 88px + `pt-[88px]` on `<main>` adds another 88px. Sticky covers one, leaving visible 88px gap.

## Context
Non-homepage pages use `position: sticky` header. Homepage uses `position: fixed`. The spacing model differs between the two, creating an asymmetric gap.

## The Mechanism

### Homepage (no gap)
```
Viewport
└── [fixed header overlaid at top — 0px, zIndex 1100]
└── [Hero image starts at 0px from viewport top — NO gap]
    └── [Hero content has pt-[88px] → search box pushed below header]
```

- `layout.js`: no `pt-[88px]` on `<main>`
- `main-header.js`: `position="fixed"`
- `homepagev2.js` line 392: `pt-[88px]` on hero child div

### Non-homepage (gap exists)
```
Viewport
└── [sticky header pinned at top — 0px, zIndex 1100]
└── [Gap — 88px white space from pt-[88px] on <main>]
└── [Hero image starts at 88px from viewport top]
```

- `layout.js` line 230: `pt-[88px]` on `<main>` when `!isHomepage`
- `main-header.js`: `position="sticky"`
- Hero children: no `pt-[88px]` offset

### Why Double-Offset
`position: sticky` with `top: 0` keeps element in document flow AND pins it. Combined with `pt-[88px]` on `<main>`, you get 88px (sticky space) + 88px (padding) = 176px equivalent offset. Sticky header covers 88px of it, leaving exactly **88px visible gap**.

## Fix — Option A (recommended)

1. **`layout.js` line 230:** Remove `pt-[88px]` from non-homepage `<main>`
2. **`homepagev2.js` line 392:** Remove `pt-[88px]` from hero child div (redundant after `isCinematic` removal)
3. **Non-homepage hero content divs:** Add `pt-[88px]` to hero content div

Spacing becomes component-local rather than global.

## Additional Finding
88px hardcoded everywhere — not a CSS variable. Define `--header-height: 88px` as CSS custom property for maintainability.

## Files Affected

| File | Change |
|------|--------|
| `components/layout/layout.js` line 230 | Remove `pt-[88px]` from non-homepage main |
| `pages/homepagev2.js` line 392 | Remove redundant `pt-[88px]` on hero child |
| `pages/destinations/index.js` | Add `pt-[88px]` to hero content div |
| `pages/trips/index.js` | Add `pt-[88px]` to hero content div |
| `components/UI/FeaturedImageHeader.js` | Could accept `contentOffset` prop |

## Related
- [[nextjs-fixed-header-per-route]] — The fixed vs sticky pattern that causes this
- [[hero-section-comprehensive-audit]] — Full hero audit including this gap
- [[header-redesign-2026-spec]] — Header redesign spec
- [[smartenplus-header-ux-v1]] — Header implementation v1
