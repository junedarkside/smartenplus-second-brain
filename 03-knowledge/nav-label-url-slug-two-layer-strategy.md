# Nav Label / URL Slug Two-Layer Strategy

## Summary
Nav labels and URL slugs should differ on travel platforms: nav = brand word, URL = SEO word.

## Context
Discovered during SmartEnPlus homepage terminology audit (2026-06-05). Conflict: nav said "Experiences" but URL was `/activities`. Initial instinct was to align them. Investigation found the split is intentional and correct.

## Decision
Keep nav label and URL slug as separate concerns. Do not force them to match.

## Details

**Layer 1 — URL slug:** SEO-optimized, stable, never changed after production indexing.
- Uses high-volume transactional keyword ("activities" has higher booking-intent search volume than "experiences")
- Google indexes the URL, not the nav anchor text
- Changing a production URL = risk to backlink equity + months of re-crawl

**Layer 2 — Nav label:** Brand-optimized, user-facing, safe to change any time (text-only edit, zero SEO impact).
- Uses premium/aspirational word ("Experiences" signals Airbnb-tier product)
- Users read nav labels, not URL slugs
- Can evolve with brand positioning without touching URLs

## Industry Benchmark
- Airbnb: nav = "Experiences", URL = `/s/experiences` → canonical pattern
- Viator: nav/marketing = "Experiences", SEO pages use "things to do" + "activities"
- GetYourGuide: nav = "Tours & Activities", SEO pages target "activities" keywords

## Tradeoffs
- **Pro:** Brand language upgrades without SEO cost
- **Pro:** URL equity preserved indefinitely
- **Con:** Slight inconsistency if user copies URL and sees "activities" vs "Experiences" in nav — minor, acceptable
- **Con:** Requires discipline: never let internal team assume URL = brand term

## Consequences
Apply this pattern to any future brand term evolution. Change nav labels freely. Treat URL slugs as permanent infrastructure.

## Related
- [[homepage-terminology-audit-2026-06-05]]
- [[production-url-rename-cost-framework]]
- [[nextjs-307-vs-301-product-reclassify]]
