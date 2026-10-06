---
name: route-page-section-card-design-tokens
description: Design token standard for section cards on the route trips page — established #456, applied to all 4 cards.
type: knowledge-atom
date: 2026-10-06
tags: [design-tokens, tailwind, route-page, section-card]
---

# Route Page Section Card — Design Token Standard

Established #456. Apply to all section cards on `/trips/[from]/[to]`.

## Card Wrapper

```
mx-2 md:mx-3 xl:mx-0 bg-white border border-gray-200 rounded-md md:rounded-lg p-2
```

- `border border-gray-200` — NOT `outline outline-1 outline-gray-200` (different box model)
- `p-2` — NOT `p-4` (compact)
- `rounded-md md:rounded-lg` — NOT `rounded-lg` only

## Section Heading (h2)

```
text-base font-semibold text-gray-800 mb-2
```

- Tag: `<h2>` — NOT `<p>` or `<h3>`
- `text-base` (16px) — NOT `text-sm` (14px)
- `mb-2` — NOT `mb-1` or `mb-3`

## Body Text

```
text-sm text-gray-800 leading-5
```

## Heading Hierarchy on Route Page

```
h1  — route identity ("Hat Yai to Koh Lipe Ferry")
h2  — section cards (§03 Quick Answer, §04 Route Facts, TripOverview, RouteFAQ)
h3  — operator/item cards inside sections
```

No level skips. Verified via `document.querySelectorAll('h1,h2,h3')` DOM scan.

## Applied Components (verified #456)

| Component | File |
|-----------|------|
| RouteQuickAnswer | `components/trips/RouteQuickAnswer.js` |
| RouteSummary | `components/trips/RouteSummary.js` |
| TripOverview | `components/trips/TripOverview.js` |
| RouteFAQ | `components/trips/RouteFAQ.js` |
