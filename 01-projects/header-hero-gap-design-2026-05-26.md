# Header-Hero Gap — Design Analysis

## Observation

**Layout.js (line 230):**
```jsx
<main ... className={`...${isHomepage ? '' : ' pt-[88px]'}`}>
```
- Homepage: `pt-[88px]` absent on `<main>`
- Non-homepage: `pt-[88px]` applied to `<main>`

**main-header.js (line 40):**
```jsx
position={isHomepage ? 'fixed' : 'sticky'}
```
- Homepage: header fixed, overlays content
- Non-homepage: header sticky, reserves space

**homepagev2.js (line 392):**
```jsx
<div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full z-20 pt-[88px]">
```
- Homepage hero children has explicit `pt-[88px]`

**destinations/index.js (line 83):**
```jsx
<div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full z-20">
```
- No `pt-[88px]` on destinations hero children

## Visual Gap Assessment

**The gap is REAL but MISPLACED.**

On non-homepage pages, the sticky header occupies its natural flow space. The `pt-[88px]` on `main` pushes ALL content — including the hero — down by exactly 88px. The header does NOT overlap content; it reserves its height in the document flow. The hero image begins 88px below the header's bottom edge.

On the homepage, the fixed header overlays content (no `pt-[88px]` on `main`). The hero content has `pt-[88px]` which visually offsets it below the fixed header. This works.

The "gap" feeling likely comes from:
1. The `top-1/2 transform -translate-y-1/2` centering on hero children positions content at the vertical center of the hero container, not at its top
2. The hero image starts at `top-0` of the container — so the image top is flush with the header, but the centered content has 88px top padding, creating a visual disconnect between image top and content

## Spacing Inconsistencies

| Context | Homepage | Non-Homepage |
|---------|----------|--------------|
| `main` padding | None (header fixed) | `pt-[88px]` |
| Header position | `fixed` | `sticky` |
| Hero children `pt-[88px]` | Yes (line 392) | No (destinations) |
| Header offset on main | N/A | 88px |

**Key inconsistency:** Homepage hero children has `pt-[88px]`, but destinations hero children does not. This should be symmetric — either both have it or neither does.

## Root Cause Hypothesis

The 88px offset lives in two different places depending on page type:
- Non-homepage: `pt-[88px]` on `<main>` (correct, compensates for sticky header height)
- Homepage: `pt-[88px]` on hero children div (redundant with fixed header overlay)

The redundant `pt-[88px]` on homepage hero content is likely leftover from the `isCinematic` removal. Previously, the cinematic hero may have used full-viewport height with internal offsets. Now with standard `FeaturedImageHeader`, this padding is misplaced — it should be on the wrapper, not inside the children.

The perceptual gap on non-homepage pages comes from the `top-1/2` transform centering children content in the hero rather than anchoring it to the top. Combined with the gradient overlay at `top-0`, this creates a visual separation between the hero image top and the centered text content.

## Recommendation

1. **Remove `pt-[88px]` from homepage hero children** (homepagev2.js line 392) — this is redundant since the fixed header overlays content, not reserves space. The offset should come from the header's own height, not from hero content padding.

2. **Verify hero centering approach** — `top-1/2 transform -translate-y-1/2` places content at the hero's vertical center. If the intent is to place content below the header line, consider `top-[88px]` instead or reduce the vertical centering offset.

3. **Audit other non-homepage pages** — confirm consistency of hero structure across all pages using `FeaturedImageHeader`. The destinations page structure (no `pt-[88px]` on children) is the correct baseline.

4. **Consider visual anchor** — the gradient overlay `hero-top-gradient` at `top-0 left-0` creates a visual transition zone. This is good, but the gap perception persists because the centered content appears floating rather than anchored to the header baseline.