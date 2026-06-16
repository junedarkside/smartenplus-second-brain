# Thailand Bundling and Margin Strategy

## Summary

Thailand bundled travel pricing uses tiered margin structure: low-margin transport as hook, high-margin wellness/SIMs as profit. Value communicated via "Bundle Scores" showing price+time efficiency. Klook uses content marketing to route research-phase traffic to high-margin SKUs.

## Context

Bundling transport+activities requires understanding margin composition to price bundles profitably. The Thailand market has distinct dynamics: thin margins on trains/buses, high margins on add-ons.

## Problem

How to structure bundles that are attractive to travelers (value) while maintaining healthy margins (profitability)? Without clear margin tier logic, bundles either underprice or feel like a scam.

## Details

**Bundle Composition & Margin Tiers:**

| Tier | Components | Margin Profile |
|------|-----------|-----------------|
| Required Core | Trains, buses, ferries, local transfers | Lower (price competition) |
| Optional Core | 1-3 flagship experiences (temple tours, dinner cruises) | Medium |
| High-Margin Add-ons | Spas, massages, SIMs, travel passes | High (underrepresented on OTAs) |

**Value-Based Pricing ("Bundle Scores"):**
- Reward users for booking complete bundles vs standalone items
- Bundle Score = combined price savings + time efficiency (optimized transfer buffers)
- Bundle-level summary: total cost + total travel time + free time left
- Makes "finished product" value clear before payment

**Promotional & Acquisition Tactics (Klook model):**
- Content marketing ("10 tips to stay on budget") catches research-phase traffic → routes to high-margin SKUs
- Influencer codes, referral campaigns, limited-time discounts → early-trip app installs
- Trust layer (GetYourGuide): transparent pricing, robust cancellation policies → premium positioning

**Strategic Integration Gap:**
- Owning end-to-end itinerary (transport+activities+wellness) shifts from "cart of SKUs" to "service provider"
- Earns premium for better trip composition and conflict-aware scheduling
- Note: no specific commission rate data available for Thai transport/activity operators

## Decision

Build bundles with explicit margin tiers. Use Required Core (transport) as acquisition hook, anchor 1-3 activities at medium margin, upsell high-margin wellness/SIMs for profitability. Communicate value via Bundle Score.

## Tradeoffs

- High-margin add-ons require inventory curation (spas, salons) vs just aggregating tours
- Bundle Score UX complexity for v1 MVP
- Rate fence logic needed to prevent business travelers trading down to leisure bundles

## Consequences

- Pricing engine: needs margin tier data per SKU, not just price
- Bundle recommendation: must suggest add-ons based on schedule compatibility, not just upsell
- Success metrics: bundle attach rate, add-on revenue per booking, margin % per bundle

## Related

- [[business-development-thailand-bundle-architecture]] — bundle structure and supply model
- [[business-development-unified-travel-wellness-thesis]] — wellness as high-margin differentiator
- [[business-development-thailand-platform-analysis]] — Klook/GetYourGuide promotional mechanics