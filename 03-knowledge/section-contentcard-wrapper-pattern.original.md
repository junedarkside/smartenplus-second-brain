# Section/ContentCard Wrapper Pattern

## Summary
Missing Section/ContentCard wrappers cause full-bleed cards on mobile. Pattern: Section for page-level padding, ContentCard for card-level constraints. Trip detail audit found 9+ sites hardcoding layout instead of using abstractions.

## Context
`trip-detail-uxui-audit-2026-05-22.md` + `airport-transfer-redesign-2026.md`. Trip detail audit: 32 issues, root cause = Section/ContentCard absent. Airport transfer Pass 2: removed ContentCard (other sections don't use it).

## Problem
Trip detail tree (`pages/trips/detail/[...slug].js`) had zero Section/ContentCard imports. Components hardcoded full-bleed divs:
- `TripDetailsAttribute.js:41` — zero `mx-` everywhere
- `TripDetailsImageAndMap.js:34` — full-bleed all breakpoints
- `TripDetailContent.js:113` — full-bleed all breakpoints
- `[...slug].js:307` — `className='w-full'` missing `max-w-[1200px] mx-auto`

Result: cards touch screen edges on mobile, no standard padding.

## Decision

### Pattern: ContentCard at Component Level, Section at Page Level
```
Page ([...slug].js)
 <Section> ← page-level max-w + horizontal padding
    <ContentCard>              ← card-level rounded + overflow-hidden
      <TripDetailsAttribute />
</ContentCard>
    <ContentCard>
      <TripDetailsImageAndMap />
    </ContentCard>
  </Section>
```

### ContentCard Provides
- `bg-white`
- `flex-col`
- `rounded-md` (or design system token)
- `overflow-hidden` (clips image at corners)

### Section Provides
- `max-w-[1200px] mx-auto`
- Horizontal padding: `px-2 md:px-3 xl:px-0`
- Vertical padding: `py-4` or context-dependent

### When to Skip ContentCard
For photo-led editorial sections (e.g., Destinations, Airport Transfer cards):
- `bg-white` irrelevant — photography fills cards
- `overflow-hidden` should live on individual cards, not section wrapper
- `flex-col` blocks asymmetric CSS grid layouts

**Airport Transfer decision:** Skip ContentCard, use `Section` + local grid div directly. Same escape hatch `PopularRoutesSection` uses.

## Details

### Trip Detail Fix (Implemented)
```jsx
// TripDetail2.js — ContentCard wraps 4 sections
import ContentCard from 'components/common/ContentCard';

<TripDetailsAttribute>
  <ContentCard>
<TripDetailsAttribute />
  </ContentCard>
</TripDetailsAttribute>

<TripDetailsImageAndMap>
  <ContentCard>
    <TripDetailsImageAndMap />
  </ContentCard>
</TripDetailsImageAndMap>
```

### Calendar Mobile Fix
```jsx
// SlideCalendar2.js:985
// BEFORE: md:mx-3 md:rounded-md (no mobile margin/rounding)
// AFTER: mx-2 md:mx-3 xl:mx-0 rounded sm:rounded-md
```

### Trip Details Mobile Fix
```jsx
// [...slug].js:341
// BEFORE: gap-0 my-0 px-0 md:px-3
// AFTER: gap-2 mt-2 px-2 md:px-3
```

## Tradeoffs
- Per-component `mx-` breaks reuse on other pages — ContentCard at parent level is correct
- Skipping ContentCard on editorial sections is intentional — verify with design before skipping
- Section padding at page level means all child sections share same horizontal rhythm

## Consequences
- Trip detail: 8 issues resolved in one ContentCard wrapper pass
- Mobile cards now have consistent horizontal padding
- Reuse on other pages preserved — components stay layout-agnostic

## Related
- [[design-systems]] — design tokens
- [[editorial-grid-layout-pattern]] — when to skip ContentCard
- [[trip-detail-uxui-audit-2026-05-22]] — full audit findings
