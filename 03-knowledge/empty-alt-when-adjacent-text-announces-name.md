# Empty `alt=""` When Adjacent Text Announces the Name

## Summary
Set `alt=""` (empty, not omitted) on a decorative/informative image **when an adjacent element already announces the same name** to screen readers — e.g. an overlay `<h3>` + a parent `aria-label`. Non-empty `alt` then **double-announces** the name. This is the W3C "adjacent text" pattern, not laziness.

## Context
`/destinations` index card (`components/destinations/LocationCard.js:39-54`, session #251). Card image uses `alt=""` while the location name is announced via the overlay `<h3>` (line 52) and the `<article aria-label="…">` (line 34). A mobile debate "critic" flagged `alt=""` on real photos as an a11y bug; verdict: **`alt=""` is CORRECT** here.

## Problem
Card has 3 places that could name the location:
1. `<Image alt="…">`
2. Overlay `<h3>{capitalizedName}</h3>`
3. `<article aria-label="{name}, N stations">`

If all 3 carry the name, a screen reader announces "Bangkok, 8 stations, Bangkok, Bangkok" — redundant, noisy, worse UX than one clean announcement.

## Pattern
```jsx
<article aria-label={`${name}, ${stations.length} stations`}>
  <div className="relative h-40">
    <Image src={photo} alt="" fill ... />          {/* empty — adjacent text names it */}
    <div className="absolute bottom-0 p-4">
      <h3 className="text-white">{name}</h3>        {/* visible + announced name */}
      <p className="text-white/90">{caption}</p>
    </div>
  </div>
  ...
</article>
```

- `alt=""` (empty string) → image is marked **decorative**, skipped by AT. Name comes once from `<h3>` (and the article label gives context: "8 stations").
- Do **not** omit `alt` entirely — an omitted `alt` makes some AT fall back to reading the `src` filename ("default-route.webp"), which is worse.

## Rule
- `alt=""` → image is decorative OR its meaning is fully conveyed by adjacent text/labels.
- Meaningful `alt="description"` → image conveys info NOT present elsewhere (a chart, a directional photo, a unique scene).
- Omitting `alt` → never. Always explicit `alt=""` or `alt="…"`.

## Tradeoffs
- Correct **only** when adjacent text truly duplicates the name. If the photo adds info the text lacks (e.g. "aerial view of the bay"), give it real `alt`.
- SEO: `alt=""` images contribute nothing to image search. Acceptable for UI card imagery; use real `alt` on content/marketing photos you want indexed.
- Sighted users unaffected — `alt=""` just means no tooltip on hover (browsers don't show empty alt).

## Related
- [[text-overlay-gradient-not-flat-for-contrast]] — companion rule for the same card (text legibility over the image)
- [[operator-image-alt-caption-fields]] — when images DO need real alt (operator content)
- [[star-aria-radiogroup-pattern]] — other AT-announcement dedup thinking
- `components/destinations/LocationCard.js:41` — source
