# Header-Hero Gap — UX Analysis

## Observation

The gap is caused by two stacked vertical offsets:

1. **Non-homepage `main` has `pt-[88px]`** (layout.js line 230) to push content below the sticky header. The header is `position: sticky` with `top: 0, zIndex: 1100` (main-header.js line 40-41). When sticky is at page top (not yet scrolled), it occupies the 88px but the hero starts visually at y=0 of the page viewport. Since the hero's parent container does NOT have an explicit top offset matching the sticky header height, the hero image's top edge aligns with the viewport top, directly behind the sticky header.

2. **Hero content uses `top-1/2 -translate-y-1/2` centering** (FeaturedImageHeader.js line 83, homepagev2.js line 392). This centers content vertically within the hero container — meaning the top half of the hero content is pushed down by half the hero height. On smaller hero heights, this adds visible space at the top of the hero before content appears.

The result on non-homepage pages: Hero image visible BEHIND sticky header (z-index layering), while the hero's content (title, search bar) is centered in the remaining space below the sticky header. This creates a visual disconnect — the header and hero feel misaligned rather than cohesive.

## User Perception

- **Landing on a non-homepage page:** The sticky header sits at the top with a subtle glass/blur effect. Below it, the hero image starts at y=0 (overlapping the header area) while the hero's text/content is pushed down by the centering transform. This gives the impression the hero "starts behind" the header — a visual gap of misalignment between header and content.
- **The `pt-[88px]` on `main` does not affect the hero image** — it only offsets the main content column. The hero's `<header>` container is a sibling inside `<main>` (homepagev2 line 386), not a wrapper around all main content. So the hero image positioning is governed entirely by FeaturedImageHeader's own `min-h` and `absolute` positioning relative to the page.
- On the homepage, `position: fixed` header scrolls away, so the hero starts at y=0 with no overlap and no `pt-[88px]` needed — the gap does not manifest.

## Scroll Behavior Impact

- **Scrolling down (non-homepage):** As the page scrolls, the sticky header remains pinned at top. The hero image scrolls with the page, partially disappearing behind the sticky header. The content centered inside the hero (via `top-1/2`) also scrolls but remains centered within the shrinking hero area. The gap between header bottom and hero content changes minimally since both scroll together.
- **The `top-1/2 -translate-y-1/2` centering effect persists regardless of scroll** — the hero content is always vertically centered inside the hero container, not anchored to the hero's top edge.

## Sticky vs Fixed Header Effect

| | Homepage (fixed) | Non-homepage (sticky) |
|---|---|---|
| Header position | Fixed, scrolls away | Sticky, always visible at top |
| Content offset | None needed | `pt-[88px]` on `<main>` |
| Hero image start | y=0, fully visible | y=0, behind sticky header (overlap) |
| Gap manifestation | None | Header/hero appear misaligned |

The fixed header scrolls out of the way, so hero image starts from y=0 without visual conflict. The sticky header stays, creating overlap with the hero image that is perceived as a gap between the header's bottom edge and the hero content.

## Root Cause Hypothesis

The gap is a **visual layering issue**, not a spacing measurement error:

1. The sticky header (`zIndex: 1100`) sits on top of the hero image layer. The hero image starts at `top-0` of the viewport, but the header overlays the top 88px of the page.
2. The hero content (title, search) is vertically centered inside the hero container, pushing it down. This creates the perception that the hero content "starts below" where it should, relative to the header.
3. The `pt-[88px]` on `<main>` only offsets the MAIN content flow, not the hero image container (which is positioned `absolute` inside `FeaturedImageHeader`).
4. The 88px value is hardcoded, not a CSS variable tied to the actual header height — if the header's rendered height differs from 88px (due to line-height, padding, font-size), the offset becomes incorrect.

**Perceived gap = (header height) + (hero centering offset) — (how much hero image actually shows above header)**

## Recommendation

1. **Add a top offset to the hero container equal to the header height** — instead of hero starting at y=0, it should start at `top-[88px]` on non-homepage. This ensures the hero image starts BELOW the sticky header, eliminating overlap.
2. **Change hero content anchor from `top-1/2 -translate-y-1/2` to `top-[offset] flex items-start`** — so content aligns to hero top, not center. This removes the centering push-down that creates the "content gap" appearance.
3. **Replace hardcoded 88px with a CSS custom property** (`--header-height: 88px`) on the body or root element. This ensures consistency across components and easy adjustment if header height changes.
4. **Homepage behavior remains unchanged** — fixed header scrolls away so hero can start at y=0. This is the correct behavior for homepage.