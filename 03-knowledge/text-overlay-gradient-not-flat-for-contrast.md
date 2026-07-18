# Text-Overlay Gradient (not flat) for WCAG Contrast

## Summary
When white text sits over a photo, use a **directional bottom gradient** (`bg-gradient-to-t from-black/60 via-black/25 to-transparent`) — not a flat `bg-black/X` overlay. The gradient concentrates darkness at the text baseline (where 4.5:1 is measured) while leaving the upper image readable. A flat overlay needs high opacity *everywhere* to hit contrast at the text, which over-darkens the whole image.

## Context
`/destinations` index card redesign (session #251, `components/destinations/LocationCard.js:50`). Supersedes the open contrast risk flagged in [[editorial-grid-layout-pattern]] ("`bg-black/25` white text may fail 4.5:1 on light images — increase to `bg-black/35` if needed"). Increasing flat opacity was the wrong lever — gradient is the fix.

## Problem
Card name/province overlay bottom-left over arbitrary location photos (some bright, e.g. beaches). Flat `bg-black/25`:
- Fails 4.5:1 on light images (sand, sky) → name illegible.
- Raising to `bg-black/35`+ fixes text but muddies the entire photo — the image (the whole point of an image-forward card) loses punch uniformly.

## Pattern
```jsx
<div className="relative h-40 overflow-hidden">
  <Image src={location.image || DEFAULT} alt="" fill className="object-cover" />
  {/* directional gradient: dark AT text (bottom), fading up */}
  <div aria-hidden="true" className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/25 to-transparent" />
  <div className="absolute bottom-0 left-0 p-4">
    <h3 className="font-semibold text-white">{name}</h3>
    <p className="text-xs text-white/90">{caption}</p>
  </div>
</div>
```

- `from-black/60` (bottom, where text sits) → `via-black/25` (mid) → `to-transparent` (top). Darkest at the text baseline.
- `aria-hidden="true"` on the gradient div — decorative, screen readers skip it (name comes from the `<h3>`, see [[empty-alt-when-adjacent-text-announces-name]]).
- `text-white/90` on secondary caption (slightly dimmer than the `text-white` name) — both clear the gradient's 60% dark region.

## Why not flat
| Approach | Contrast at text | Image quality |
|----------|------------------|---------------|
| Flat `bg-black/25` | ❌ fails on light images | ✅ image visible |
| Flat `bg-black/50`+ | ✅ passes | ❌ whole image muddy |
| **Bottom gradient `from-black/60`** | ✅ passes (dark at baseline) | ✅ upper image clear |

## Tradeoffs
- Works because text is **anchored bottom**. If text floats mid-card or top, flip the gradient direction (`bg-gradient-to-b` / `-to-r`) so dark sits under the text.
- Assumes a fixed text position. Editorial layouts with text at varying heights per card → flat may be simpler (accept the opacity tradeoff).
- No design token yet (single consumer). Comment-marked one-off: `// text-on-image contrast (WCAG 4.5:1), no overlay token yet`. Extract token at 3rd consumer (YAGNI).

## Related
- [[empty-alt-when-adjacent-text-announces-name]] — companion a11y rule for the same card (why `alt=""`)
- [[editorial-grid-layout-pattern]] — prior card pattern; this resolves its open contrast risk
- [[destinations-card-redesign]] — homepage destinations section (text-below-image, different surface)
- `components/destinations/LocationCard.js:50` — source
