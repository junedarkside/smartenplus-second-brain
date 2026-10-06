---
name: fe-content-guard-pattern
description: Pattern for FE components that derive content from ISR data — guard against wrong-route content rendering by checking derived text contains expected route keywords.
type: knowledge-atom
date: 2026-10-06
tags: [pattern, isr, content-guard, route-page]
---

# FE Content Guard Pattern

Use when a component derives display content from ISR text fields (e.g. `overview`, `description`) that may contain stale or wrong-route data (e.g. Django admin hasn't updated the field yet).

## Pattern

```jsx
const Component = ({ text, fromLocation, toLocation }) => {
  const sentence = text?.split(/(?<=[.!?])\s/)[0]?.trim() || '';
  const keywords = [fromLocation, toLocation].filter(Boolean).map(s => s.toLowerCase());
  const relevant = keywords.length === 0 || keywords.some(kw => sentence.toLowerCase().includes(kw));
  if (!sentence || !relevant) return null;
  // render
};
```

## Rules

- Return `null` (not empty div) when guard fails — no layout impact
- Keywords = route-specific identifiers (location names, not generic words)
- `keywords.length === 0` → skip guard (no context to check against)
- Props: pass `fromLocation` + `toLocation` as separate strings, NOT a joined string

## Why

ISR text fields can contain content from a different route until Django admin updates them. Guard prevents wrong-route content from showing. Renders nothing instead of misleading text — better UX than stale data.

## Applied

`components/trips/RouteQuickAnswer.js` — guards `overview` first sentence against departure/arrival location name. If sentence doesn't mention either location, component hides itself.

## Future Upgrade

When BE adds a dedicated `quick_answer` field (separate from `overview`), the content-guard becomes optional since the field is route-specific by definition. Guard stays as defensive fallback.
