# Section Render Order Principles

## Summary
Trust signals must precede editorial content. Mobile scroll depth rules: most users never reach position 8. Reviews (highest-leverage trust signal) should be at position 5, not 8.

## Context
`homepage-ux-review.md`. 3-agent review (UX Research x2 + UI Component Engineer). 11 homepage sections audited.

## Problem
Current render order buries trust signals:
```
1. Hero + Search
2. Popular Routes
3. Guides (blog)       ← blog too early
4. Locations
5. Thailand Travel
6. Airport Transfer
7. News (blog)         ← blog fragments funnel
8. Reviews             ← trust signal buried
9. Activities (blog)   ← sandwiches Reviews
10. My Bookings CTA
11. Customer Service
```

Most mobile users never scroll to position 8.

## Decision

### Recommended Order
```
1. Hero + Search
2. Popular Routes
3. Locations           ← group discovery
4. Airport Transfer    ← group discovery
5. Reviews ← trust before editorial
6. Thailand Travel    ← features/trust
7. Guides (blog)      ← nurture/SEO
8. News + Activities  ← collapse or tab
9. My Bookings CTA
10. Customer Service
```

### Trust Before Editorial Rule
Reviews (aggregate rating + breakdown) is the highest-leverage trust signal. It must appear before any editorial/content sections (Guides, News, Activities). Editorial sections are for SEO + nurture; trust signals are for conversion.

### Mobile Scroll Depth Rule
- Position 1-4: above fold or immediate scroll (< 1 screen)
- Position 5-6: early scroll (< 2 screens)
- Position 7-8: mid scroll (most mobile users reach)
- Position 9+: deep scroll (minority reach)

Sections at position 7+ have20-30% of mobile traffic. Trust signals at position 8 = most mobile users never see them.

## Details

### Nielsen Norman Group Research
Users miss non-first panels in carousels. Feature/trust content should use flat layouts, not carousels. Thailand Travel carousel was flagged for this reason.

### Section Grouping
**Discovery group (positions 2-4):** Popular Routes, Locations, Airport Transfer — user is exploring options.

**Trust group (position 5):** Reviews — user needs social proof before committing to search.

**Editorial group (positions 6-8):** Thailand Travel (features), Guides, News+Activities — nurturing content for SEO and engagement.

**Conversion group (positions 9-10):** My Bookings CTA, Customer Service — bottom-funnel actions.

## Tradeoffs
- Moving Reviews from8→5 is a ~10 minute change — highest ROI fix in the audit
- collapsing News + Activities into tabs or single section reduces section count without losing SEO value
- Guides at position 7 still captures intent-rich users who scroll deep

## Consequences
- Trust signal visibility increases for mobile users
- Editorial sections remain crawlable for SEO
- Section grouping creates clear user journey mental model

## Related
- [[homepage-ux-review]] — full audit findings
- [[homepage-seo-performance-deep-review-2026-05-21]] — SEO structured data
