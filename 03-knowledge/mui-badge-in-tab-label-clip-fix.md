# MUI Badge Inside Tab Label — Clip Fix

## Summary
MUI `<Badge>` wrapping a `<Tab>` label text clips the pill at the tab boundary unless the Badge wrapper has explicit padding-right.

## Problem
`<Tab>` constrains its label to natural text width. `<Badge>` positions the pill at top-right of the anchor element. With a large negative `right` offset (e.g. `right: -14`), the 20px pill overflows the tab's `overflow: hidden` boundary and is visually clipped.

## Fix
Add `pr` (padding-right) to the Badge root so the label box widens to include pill space:

```jsx
<Badge
  badgeContent={count}
  color="error"
  max={99}
  sx={{ pr: 1.5, '& .MuiBadge-badge': { right: -6, top: 6 } }}
>
  Tab Label Text
</Badge>
```

- `pr: 1.5` = 12px — creates room inside the tab boundary for the pill
- `right: -6` — positions pill at trailing edge without overflowing
- `top: 6` — vertically centers with tab text

## Why
MUI `<Tab>` does not automatically expand for badge overflow. The Badge badge sub-element is absolutely positioned relative to the Badge root, not the Tab container. `pr` widens the root → tab receives wider label → pill stays inside bounds.

## Contrast: Badge on Icon (no issue)
`<Badge>` wrapping an icon in `<ListItemIcon>` works without `pr` because icons have fixed square dimensions with natural padding on all sides.

## Related
- [[command-centre-pending-badge-implementation]]
- MUI v5.14.15 confirmed
