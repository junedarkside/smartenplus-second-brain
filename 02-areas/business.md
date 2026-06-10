# Business

## Summary
SmartEnPlus is a vertically integrated SEA transportation + tour operator running dual-channel: B2B supply to 12Go/Klook (90% revenue) + B2C direct platform (10%, growing).

## Context
Validated 2026-05-24 via GA4, GSC, operator data, and founder interview. Replaces hypothesis-based direction.
Last updated: 2026-06-09 — non-transport booking live, roadmap sequencing revised (journey builder gated behind cross-sell/bundle validation).

## Validated Customer

**Primary:** English-speaking independent international traveler.

Evidence:
- GA4: US highest engagement (53.7%). Thailand only 21.2%.
- Support: WhatsApp, email, Facebook — all EN. No LINE (Thai-default channel absent).

**Secondary (Phase 2+):** Thai domestic, regional Asian travelers.

## Revenue Reality

| Channel | Revenue % | Model |
|---------|-----------|-------|
| B2B supply (12Go + Klook) | ~90% | Markup on contracted inventory |
| B2C direct (SmartEnPlus.com) | ~10% | Markup + own-brand tour margin |

B2B is the cash engine. B2C is the growth bet. Commission model deferred until operator self-serve dashboard exists.

## Business Model

**Hybrid — not a pure aggregator:**

| Layer | Model | Margin |
|-------|-------|--------|
| Transportation (ferries, transfers, vans) | Markup on contracts | Medium |
| Own-brand tours + packages | Direct operation | High |
| Third-party experiences | Marketplace commission | Low-Medium |
| Flights (future) | Meta search affiliate | Low / traffic |

Own-brand tours validated on Klook and now bookable on SmartEnPlus.com B2C. Cart + checkout support DAY_TOUR/SPA_WELLNESS — fixed 2026-06-02/03 (commits `9ef2752`, `0c3bb14`).

## Product Vision

> "Stippl for SEA with real booking."

Stippl plans trips but can't book. 12Go/Klook book but don't plan. SmartEnPlus target: AI-assisted journey planner that executes — for Southeast Asia specifically.

**Core loop:**
1. Traveler inputs destinations + dates + interests
2. Platform suggests full SEA journey (transport + experiences)
3. Traveler books everything in one flow
4. Platform coordinates timing, transfers, disruptions

No social features. No gamification. Operational utility only.

## Competitive Moat

**#1 — Vertical integration.** Own minivan network (nationwide Thailand) + own-operated tours. 12Go/Klook negotiate with operators. SmartEnPlus IS the operator on key routes.

| Moat | State |
|------|-------|
| Owned minivan network (nationwide Thailand) | Live |
| Own-brand tours (Klook-validated) | Live on B2C (fixed 2026-06-02/03) |
| Tour operator network Thailand | Live |
| Cross-border route (Langkawi↔Lipe) | Live |
| B2B supply relationships (12Go + Klook) | Validated |
| SEO transportation layer | Partial |
| Journey coordination engine | Feature exists, near-zero usage |
| Operator self-serve dashboard | Not built yet |

## Geographic Phases

| Phase | Market | Basis |
|-------|--------|-------|
| Phase 1 — Year 1 | Thailand (southern islands) | Live: Samui, Lipe, Phi Phi, Lanta, Krabi, Hat Yai, Chiang Mai, Chiang Rai |
| Phase 2 — Year 2 | Malaysia | Langkawi↔Lipe already live |
| Phase 3 — Year 2-3 | Vietnam | Build from zero |
| Phase 4 — Year 3+ | Indonesia (Bali/Lombok/Gili) | After disruption systems mature |

## Product Roadmap Sequence

1. **Done:** Simple search + book (parity with 12Go). B2B supply healthy.
2. **Done:** Own-brand tours + packages on B2C platform. DAY_TOUR/SPA_WELLNESS bookable — margin captured directly (2026-06-02/03).
3. **Now:** Cross-sell + bundle UX. Surface own-brand tours to existing transport buyers. Validate Revenue Per Traveler uplift before investing in journey builder.
4. **Next (gated):** Journey builder UI (A→B→C itinerary in one flow) — build only after multi-booking rate rises. UX problem not demand problem.
5. **After:** Post-booking coordination (timeline, alerts, disruption handling).
6. **Later:** Operator self-serve dashboard. B2B API (some inventory still manual to 12Go/Klook).

## Strategic Path

- **Now:** B2B supplier to 12Go + Klook. Don't compete on breadth yet.
- **Year 2-3:** Dual channel. Grow B2C to 30-40%. Own-brand tours already live (2026-06-02).
- **Year 4-5:** Platform competitor to 12Go/Klook/GYG. Stippl-style planning layer on top of owned infrastructure.

## What To Avoid
- Competing with 12Go on inventory breadth before B2C is 30%+ revenue
- Building journey builder before cross-sell/bundle conversion is validated
- Building coordination infrastructure before journey builder UX is fixed
- Thai domestic UX before EN market is saturated
- Commission model before operator self-serve exists

## Decision Log
- **2026-06-09:** Journey builder deferred. Must validate cross-sell + bundle revenue uplift first. Planning UI does not auto-generate revenue — many planning products fail to monetize. Gate: multi-booking rate rising → then build journey builder.

## Related

- [[business-development-thesis-2026]] — **NEW 2026-06-03.** Strategic thesis: "Thailand's Travel Commerce Platform." Four-phase growth model, competitive position on "travel connectivity" not inventory. Growth via bookings per traveler.
- [[southeast_asia_transport_platform_direction]] — Full validated strategy document
- [[operators]] — Contract, TimeSlot, ContractAddon
- [[README]] — Platform overview
- [[tour-system-status]] — Phase 2 gaps, trust signal fields
