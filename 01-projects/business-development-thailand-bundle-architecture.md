# Thailand Bundle Architecture

## Summary

End-to-end itinerary bundling architecture: MaaS-style transport skeleton + curated activity decoration + high-margin wellness add-ons. Single timeline UI with conflict detection. v1 covers 3 corridors with wizard flow.

## Status

**ACTIVE — Phase 1 (2026-06-09).** Non-transport (DAY_TOUR/SPA_WELLNESS) now live on B2C. Bundle UX is current build priority — cross-sell transport buyers into activities. Full timeline/conflict-detection UI (Zeitrip) gated behind bundle conversion validation.

## Context

Zeitrip's bundle architecture fills the gap between 12Go (transport only) and Klook/GYG (activities only). The product treats transport and activities as components of a single itinerary—not a cart of separate items.

## Problem

Existing platforms give users separate tickets, not a trip. No timeline, no conflict detection, no smart defaults. Users must manually coordinate multi-leg journeys and hope nothing overlaps.

## Details

**Core "Slot" in Journey:**
Own end-to-end itinerary (door-to-door trip). Users pick origin, dates, interests → system builds transport skeleton → decorates with activities → bundles into a complete trip. Lightweight MaaS + tours.

**Bundle Archetypes:**

| Type | Skeleton | Activities | Add-ons |
|------|---------|-----------|---------|
| City Break | Airport transfer → hotel transport pass (BTS/Grab) → return | Temple tour, dinner cruise | Spa, SIM, passes |
| Island-Hopping | Bangkok→South transport → pier → ferry legs | Snorkeling, day trips per island | Spa, boat tours |
| Thematic (food/wellness/adventure) | Multi-stop route (Bangkok→Chiang Mai→Pai) | Theme-filtered packages per stop | Wellness, experiences |

**Bundle Structure (under the hood):**
- Required core: long-distance transport + ≥1 local transfer segment
- Optional core: 1-3 anchor activities
- Add-ons: spa/beauty, SIM, passes (Klook-style upsell inventory)

**UX Principles for "Seamless" Bundles:**
- **Single itinerary timeline:** all segments (train, ferry, taxi, tour, spa) on one view with time gaps + warnings
- **Conflict detection:** overlaps highlighted + alternate slots offered automatically
- **Smart defaults per city:** pre-select "typical" bundles (Bangkok weekend, Phuket 4D3N) → let power users customize
- **Trust layer:** clear refund terms per item, summarized at bundle level (GYG pattern)

**Gamification Hooks:**
- Trip completion progress bar: transport 100%, activities 60%, wellness 20%
- Badges: "optimized bundle" (no overlaps, good buffers, cost-efficiency score)
- Bundle score: price efficiency + time efficiency

**Supply & Partnerships:**
- Transport: integrate 12Go-style APIs or onboard bus/van/ferry operators directly
- Activities: curate high-quality set per destination + exclusive spa slots
- Differentiator: "Travel + Wellness" (massage, salon, clinics) layered onto standard tours—something OTAs touch lightly

**v1 Roadmap:**
- Focus: 2-3 corridors (Bangkok-Chiang Mai, Bangkok-Phuket, Bangkok-Samui) with fixed template bundles
- Wizard: corridor + dates + theme → 1-3 bundle options → timeline UI tweak
- Gamification: Bundle Score + rewards for complete bundle vs standalone

## Decision

Build end-to-end itinerary product with MaaS-style transport skeleton decorated by curated activities and high-margin wellness. Single timeline UI with conflict detection is the core differentiator.

## Tradeoffs

- Supply integration complexity (transport APIs or direct operator relationships)
- Timeline UI + conflict detection is significant engineering
- v1 limited to 3 corridors—scope vs speed tradeoff

## Consequences

- Product requires: transport aggregation, activity curation, spa/wellness partnerships
- UX priority: timeline view and conflict engine
- Success metrics: bundle completion rate, conflict detection accuracy, wellness attach rate

## Related

- [[thailand-platform-analysis]] — where 12Go/Klook/GYG fit in supply
- [[thailand-bundling-margin-strategy]] — margin tier mechanics
- [[zeitrip-mvp-product-spec]] — MVP flow
- [[unified-travel-wellness-thesis]] — wellness as differentiator