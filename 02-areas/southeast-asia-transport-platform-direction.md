# Project Direction
## Southeast Asia Transportation & Experience Infrastructure Platform

> Last validated: 2026-05-24 via production data (GA4 + GSC + founder interview)

# Core Identity

The platform IS:
- A **verified B2B supplier** of transportation + tours to 12Go and Klook (current revenue foundation)
- A **Thai tour operator** with own-brand experiences + transportation
- A **direct B2C platform** being built toward long-term competition with 12Go/Klook/GYG
- A **hybrid marketplace** — own-operated tours + third-party operator inventory
- **"Stippl for SEA with real booking"** — AI-assisted journey planner that executes, not just inspires

The platform is NOT: social travel app, gamified platform, generic OTA competing on breadth, hotel-first marketplace, Thai domestic-only.

# Product Vision

> Stippl plans trips but can't book them. 12Go books trips but can't plan them. SmartEnPlus does both — for Southeast Asia.

**Core product loop:** traveler inputs destinations+dates+interests → platform suggests full SEA journey → traveler books everything in one flow → platform coordinates timing, transfers, disruption alerts.

# Business Model Reality

## Current Revenue Split
| Channel | Revenue % | Model |
|---------|-----------|-------|
| B2B supply (12Go, Klook) | ~90% | Markup on contracted inventory |
| B2C direct (SmartEnPlus.com) | ~10% | Markup + own-brand tour margin |

## Long-Term Target
Grow B2C from 10% → 40%+ by building what B2B platforms can't replicate: own-brand bundled experiences.

## Revenue Model by Product
| Layer | Model | Margin |
|-------|-------|--------|
| Transportation (ferries, transfers, vans) | Markup on contracted inventory | Medium |
| Own-brand tours + packages | Direct operation — SmartEnPlus brand | High |
| Third-party experiences | Marketplace commission | Low-Medium |
| Flights | Meta search affiliate (future) | Low / traffic acquisition |

**Note:** Commission model only viable after operator self-serve dashboard exists. Markup is correct for current stage.

# Strategic Position

## Now — Supplier to Incumbents
Supply 12Go + Klook with validated Thailand transportation + tour inventory. This funds the B2C build. **Do not compete with 12Go on breadth today.**

## Path — Dual Channel
Grow B2C direct while maintaining B2B supply. B2B revenue = runway. B2C = long-term margin.

## Target — Platform Competitor
Year 4-5: enough inventory + own-brand tours + journey coordination + direct traffic to compete with 12Go/Klook/GYG directly. **Incumbents cannot easily replicate:** own-operated tours bundled with transportation, deep journey coordination (A→B→C in one booking), SEA island + cross-border route expertise.

# Validated Primary Customer

## B2C: English-speaking independent international traveler

**Evidence:**
- GA4: US highest engagement (53.7%), Thailand only 21.2%
- Support channels: WhatsApp, email, Facebook — all EN, no LINE (Thai-default absent)
- Current booking behavior: single-leg, foreign origin

**Secondary (Phase 2+):** Thai domestic, regional Asian travelers

## B2B: Major travel platforms
12Go (transportation routes), Klook (transportation + tours). Potential next: GetYourGuide, Viator.

# Geographic Strategy (Validated)

| Phase | Market | Basis |
|-------|--------|-------|
| Phase 1 — Year 1 | Thailand (southern islands dominant) | Live: Samui, Lipe, Phi Phi, Lanta, Krabi, Hat Yai, Chiang Mai, Chiang Rai |
| Phase 2 — Year 2 | Malaysia | Langkawi↔Lipe cross-border route already live |
| Phase 3 — Year 2-3 | Vietnam | Independent traveler corridor, build from zero |
| Phase 4 — Year 3+ | Indonesia (Bali/Lombok/Gili) | High complexity, expand after disruption systems mature |

**Principle:** Dominate corridor density before expanding geographically.

# Product Roadmap (Reality-Based Sequence)

## Stage 1 — Now (live)
Simple search + book. Parity with 12Go on UX. Single-leg dominant. B2B supply healthy.

## Stage 2 — Next Priority
**Own-brand tours + packages on B2C platform**

Why first: Highest margin. Cannot be replicated by 12Go/Klook (they aggregate, you operate). Already validated — own-brand tours already selling on Klook. Now capture that margin directly by listing on SmartEnPlus.com instead of paying Klook commission.

## Stage 3 — Journey Builder
Set A→B→C itinerary, book multiple legs in one flow.

Multi-leg feature exists but near-zero usage due to UX/discovery friction. Fix the funnel. Required:
- Journey builder UI (set full itinerary before searching)
- Post-booking upsell nudge ("add return?", "add transfer?")
- Multi-modal attachment rate tracking (currently unmeasured)

## Stage 4 — After Journey Builder Has Usage
Post-booking coordination: journey timeline, disruption alerts, transfer buffers. Only valuable after multi-leg usage exists.

## Stage 5 — Infrastructure Layer
Operator self-serve dashboard, reliability data, B2B API for GetYourGuide/Viator expansion.

**B2B API priority:** Some inventory currently delivered manually to B2B partners. Automating via API unlocks more partners (GYG, Viator) without proportional ops headcount growth.

# Competitive Moat (Honest Assessment)

| Moat | Current State | Path |
|------|--------------|------|
| **Owned minivan network** | **Nationwide Thailand — hard to replicate** | Surface on B2C platform |
| **Own-brand tours** | Klook-validated demand, not on B2C yet | Ship Stage 2 |
| **Tour operator network** | Thailand-wide supply relationships | Expand Malaysia, Vietnam |
| B2B supply relationships | Validated — 12Go + Klook pay for it | Add GetYourGuide, Viator |
| Cross-border routes | Langkawi↔Lipe live — rare inventory | Expand Malaysia corridor |
| SEO transportation layer | Partial — route pages exist | Buildable now |
| Journey coordination | Feature exists, near-zero usage | Fix UX first |
| Operator self-serve | Not built | Admin-dashboard repo — future |

**Vertical integration is the real moat:** 12Go/Klook negotiate with operators for every route. SmartEnPlus owns/operates minivans + tours directly. Platform competitors would need years to replicate this infrastructure.

# Supply-Side Reality

**Current model:** Manual contracts per operator, whole period. Operator notifies team on changes → immediate inventory update.

**Availability:** Sufficient for journey builder (immediate update pipeline exists).

**Future bridge:** Structured WhatsApp/LINE template → webhook → auto-update. Simpler than AI scraping, operators already on those channels.

**Future goal:** Operator self-serve dashboard scales both B2B supply volume and B2C inventory.

# Localization

**Phase 1:** English only (validated). **Phase 2:** Thai language when Thai domestic becomes strategic target. **Payment:** Omise + QR Pay live. No Phase 1 gaps.

# Success Metrics

## Year 1 — B2C Foundation
- Own-brand tours live on platform
- B2C revenue % (target: 10% → 20%)
- Multi-modal attachment rate (baseline measurement)
- Repeat B2C booking rate

## Year 2 — Channel Growth
- Malaysia routes live (B2B + B2C)
- Journey builder conversion rate
- B2B expansion: GetYourGuide or Viator supply deal
- B2C revenue % target: 25-30%

## Year 3 — Platform Scale
- Operator self-serve adoption
- B2C revenue % target: 40%+
- Regional route dominance (Thailand + Malaysia)

**Anti-metrics:** Do not optimize for engagement loops, time-in-app, or vanity pageviews.

# What To Avoid

- Competing with 12Go on breadth before B2C is 30%+ of revenue
- Building coordination infrastructure before journey builder UX is fixed
- Thai domestic UX investment before EN market is saturated
- Commission model before operator self-serve exists
- Expanding Vietnam/Indonesia before Malaysia corridor is dense

---

# Final Direction

> SmartEnPlus is a verified SEA transportation + tour operator that supplies 12Go and Klook today, while building a direct B2C platform differentiated by own-brand bundled experiences that pure aggregators cannot replicate. Long-term target: compete directly with 12Go, Klook, and GetYourGuide on SEA transportation and experience coordination.
