# Zeitrip MVP Product Spec

## Summary

MVP built around single itinerary timeline—not marketplace cart. Time-based planning surfaces gaps, overlaps, transfer buffers where current tools are weak. First corridors: Bangkok-Chiang Mai, Bangkok-Phuket/Krabi, Bangkok-Koh Samui.

## Context

12Go owns transport, GetYourGuide owns activity discovery. Gap: no platform offers "finished trip" feel—separate tickets glued together. Zeitrip fills this with better trip composition.

## Problem

Travelers get "ticket booth confusion" when booking Thailand trips. Must manually coordinate transport legs + activities across multiple platforms. No visibility into conflicts or transfer buffers until after payment.

## Details

**MVP Flow:**
1. User chooses origin, destination, dates, trip style
2. System proposes transport skeleton
3. System recommends activities fitting arrival/departure windows
4. User confirms in one itinerary view
5. System flags conflicts before checkout

**First Thailand Corridors:**
- Bangkok → Chiang Mai (overnight train/VIP bus + temple/food/wellness)
- Bangkok → Phuket/Krabi (flight/bus/ferry + island/beach activities)
- Bangkok → Koh Samui/Koh Tao (ferry+bus+local tours, itinerary coordination critical)

**UX Priorities:**
- One timeline for all bookings
- Visible transfer buffer between segments
- Conflict warnings before payment
- Suggested alternates when slot too tight
- Bundle-level summary: total cost, total travel time, free time left

**Differentiation vs 12Go:** Not "more inventory"—better trip composition. Transport+activity matching, schedule-aware recommendation, finished product feel.

**Positioning:** "Plan your Thailand trip in one timeline: transport, experiences, and buffers included."

## Decision

Build MVP as single timeline itinerary planner on 3 key corridors. Differentiate on confidence (not inventory) — traveler sees instantly whether transport+activity can coexist without stress or impossible timing.

## Tradeoffs

- Timeline UI + conflict detection is complex (vs simple cart/checkout)
- Fixed corridors limit breadth but enable focus
- "Finished product" positioning requires curated inventory, not just aggregation

## Consequences

- Product scope: wizard flow + timeline UI + conflict engine
- v1 spec needs: user flow, key screens, data model, bundle logic rules
- Success: bundle vs standalone booking rate, conflict detection accuracy

## Related

- [[thailand-bundle-architecture]] — bundle design, UX principles, supply model
- [[thailand-platform-analysis]] — competitive positioning
- [[business-development-thesis-2026-2029]] — strategic alignment