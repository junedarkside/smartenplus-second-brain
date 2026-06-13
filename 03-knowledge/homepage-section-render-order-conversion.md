# Homepage Section Render Order Conversion

## Summary
Homepage section render order for transport-booking conversion: Hero+Search → Popular Routes → Locations → Airport Transfer → Reviews (trust before editorial) → Thailand Travel → Guides → News+Activities (tab) → My Bookings CTA → Customer Service. Reviews must be position 5+, not 8+.

## Context
The homepage is the primary entry point for organic traffic, paid ads, and direct visits. The section order is the single biggest conversion lever after the search widget itself. Each section either answers a user objection (cost, trust, what-to-do) or introduces a new one (deep editorial, niche guides).

## Problem
The pre-Q2-2026 homepage put Reviews at position 8, after Thailand Travel, Guides, and News+Activities. Heatmap data + scroll-depth analytics showed 70%+ of mobile users never scrolled past position 5. The result: trust signals (reviews, ratings) were invisible to the majority of users at the exact moment they were deciding to book.

## Details
The conversion-optimized order, with the user-question each section answers:

| # | Section | User question answered |
|---|---------|----------------------|
| 1 | Hero + Search | "What is this site, can I search?" |
| 2 | Popular Routes | "Where do people go?" |
| 3 | Locations | "What cities do you cover?" |
| 4 | Airport Transfer | "Specific use case I have right now" |
| 5 | Reviews | "Can I trust this with my money?" |
| 6 | Thailand Travel | "What's there to do once I'm there?" |
| 7 | Guides | "Help me plan" |
| 8 | News + Activities (tab) | "What's new?" |
| 9 | My Bookings CTA | "I already booked, take me back" |
| 10 | Customer Service | "I need help" |

The load-bearing rule: **trust before editorial**. Reviews/ratings/social proof go before Guides/News/Activities. Editorial content is a retention play, not a conversion play.

## Decision
Lock the order. Any new section proposal must justify insertion without pushing Reviews below position 5. New editorial sections (Guides, News, Activities) belong in positions 6-8, never before 5.

## Tradeoffs
- Pro: conversion-aligned order; reviews visible to the scroll-past-position-5 majority.
- Pro: works for both organic and paid traffic (same first impression).
- Con: editorial team may push for Guides higher — needs to be defended with scroll-depth data.
- Con: a high-performing new section (e.g., a flash sale banner) sometimes wants position 2 — must override intentionally, not incrementally.

## Consequences
- Future homepage redesigns must defend any reorder with scroll-depth + conversion data.
- The "trust before editorial" principle extends to category pages and landing pages.
- The locked order becomes a baseline; A/B tests can shift it, but never silently.

## Related
- [[smartenplus-2026-ux-direction]] — the broader 2026 UX direction this ordering aligns with.
- [[seo-homepage-specialist-team]] — schema and metadata for the homepage ride on the same render order.
