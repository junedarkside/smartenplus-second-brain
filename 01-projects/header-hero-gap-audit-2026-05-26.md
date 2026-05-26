# Header-Hero Gap — Team Synthesis Report
**Date:** 2026-05-26
**Team:** gap-design + gap-ux + gap-frontend → synthesized

---

## The Gap — What It Actually Is

**Root cause: double-offset from sticky header behavior.**

| | Homepage | Non-Homepage |
|--|--|--|
| Header | `position: fixed` — overlays content, no document space | `position: sticky` — reserves 88px document space |
| `<main>` padding | None | `pt-[88px]` on non-homepage |
| Hero image starts at | `y=0` (behind fixed header) | `y=88px` (below sticky header + padding) |
| Hero content offset | `pt-[88px]` on hero child | None on hero child |
| Gap visible? | No (fixed header overlays) | Yes (88px white gap between header bottom + hero top) |

The gap is **88px of white space ABOVE the hero image** on non-homepage pages. The sticky header reserves its 88px in document flow, then `pt-[88px]` on `<main>` adds another 88px of padding — but the sticky header covers 88px of that, leaving exactly 88px of visible gap between the header's bottom edge and the hero image.

---

## Three Agent Findings — Convergence

**Frontend:** Gap is double-offset. Remove `pt-[88px]` from `layout.js` main, add `pt-[88px]` to hero content div on non-homepage pages.

**Design:** Homepage hero child `pt-[88px]` is redundant/leftover from isCinematic removal. Destinations pattern (no `pt-[88px]` on children) is correct baseline.

**UX:** Gap is visual layering issue. Hero image starts at `y=0` behind sticky header (z-index 1100), hero content centered via `top-1/2` creates disconnect.

---

## The Key Inconsistency

| | `layout.js` main | Hero children offset |
|--|--|--|
| Homepage | No `pt-[88px]` | `pt-[88px]` on hero child (line 392) |
| Non-homepage | `pt-[88px]` | None |

**Homepage hero child `pt-[88px]` is now redundant** — it was needed when `isCinematic=true` + fixed header, but with standard `FeaturedImageHeader` + fixed header, the hero image starts at `y=0` behind the fixed header. The padding on hero children is no longer doing useful work on homepage.

---

## Fix Options

### Option A — Remove `pt-[88px]` from `layout.js` (recommended by frontend)
- Remove `pt-[88px]` from `<main>` on non-homepage pages
- Add `pt-[88px]` to hero content div on non-homepage pages (like destinations)
- Homepage hero child `pt-[88px]` becomes irrelevant — remove it too
- Tradeoff: changes all non-homepage pages

### Option B — Remove redundant `pt-[88px]` from homepage hero child only
- Leave `layout.js` as-is (keep `pt-[88px]` on non-homepage main)
- Remove `pt-[88px]` from `homepagev2.js` hero child (line 392)
- This eliminates the homepage redundancy but doesn't fix non-homepage gap
- Tradeoff: smallest change, but gap on non-homepage persists

### Option C — Change non-homepage header to `fixed` (like homepage)
- Change `main-header.js` line 40: `position={isHomepage ? 'fixed' : 'fixed'}`
- Eliminates sticky space reservation → gap closes naturally
- Tradeoff: users lose sticky nav on all pages — significant UX regression

---

## Team Recommendation

**Option A + homepage fix** — two changes:

1. **`layout.js` line 230:** Remove `pt-[88px]` from non-homepage `<main>` — or replace with a page-specific approach where only pages that need it (with non-hero content) add it
2. **`homepagev2.js` line 392:** Remove `pt-[88px]` from hero child div — this is now dead code after `isCinematic` removal
3. **Non-homepage hero content divs:** Add `pt-[88px]` to hero content (like `top-[88px] flex items-start`) — consistent with homepage intent

This makes spacing intentional and component-local rather than global.

---

## Additional Finding

88px is **hardcoded everywhere** — not a CSS variable. If header height changes, every hardcoded value breaks. Consider defining `--header-height: 88px` as a CSS custom property.

---

## Pages Affected

- `components/layout/layout.js` — `pt-[88px]` on main
- `pages/homepagev2.js` — redundant `pt-[88px]` on hero child
- `pages/destinations/index.js` — needs `pt-[88px]` on hero child if Option A
- `pages/trips/index.js` — needs `pt-[88px]` on hero child if Option A
- `components/UI/FeaturedImageHeader.js` — could accept `contentOffset` prop
