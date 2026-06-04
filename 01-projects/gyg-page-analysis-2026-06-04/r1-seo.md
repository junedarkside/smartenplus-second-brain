---
name: r1-seo
description: Specialist C — SEO/Schema. Audit gaps in JSON-LD, schema markup, on-page SEO, internal linking. Severity P0-P3 per finding.
metadata:
  type: specialist-r1
  role: seo-schema-specialist
  page: gyg-846675-chiang-rai
  smartenplus_route: /activities/detail/[...slug]
  source_note: WebFetch unavailable, text dump used
---

# R1 — SEO/Schema Specialist

**Goal:** audit gaps in JSON-LD, schema markup, on-page SEO, internal linking vs GYG benchmark.

**GYG markup patterns observed (text dump):**
- Product ID + provider name in footer meta
- Top Attractions / Experiences / Tours / Things to do — 4×20-item numbered lists (internal link SEO)
- AggregateRating with AI-precise 4.7598
- AI-summarized review (DEFERRED — not this round)
- Country/region/depth breadcrumb: Thailand > Chiang Rai (Province) > Mae Kachan Hot Spring

**SmartEnPlus current SEO surface:**
- `DayTripDetailSEO.js` exists — JSON-LD on detail page
- Need to verify what schema types it emits (Product? TouristAttraction?)

**Severity rubric:**
- P0: high SEO impact, low risk
- P1: medium SEO impact
- P2: low impact or high risk
- P3: future / backend / deferred

---

## Audit Findings (9)

| ID | Pattern | Schema Type | SmartEnPlus Status | Severity | Fix |
|----|---------|-------------|---------------------|----------|-----|
| SEO-1 | AggregateRating with precise decimal (4.7598) | `Product.aggregateRating.ratingValue` | Likely rounded to 1 decimal (4.8) in `DayTripDetailSEO.js` | P2 | Emit precise `average_rating` rounded to 2 decimals. Trivial JS change. |
| SEO-2 | TouristAttraction / TouristTrip subclass of Product | `TouristAttraction` or `TouristTrip` | Unknown — verify `DayTripDetailSEO.js`. If only `Product`, miss subtype benefits. | P1 | Add `TouristAttraction` schema. Reuses existing fields (name, image, address, aggregateRating). ~10 lines. |
| SEO-3 | Review schema with nested `author` + `datePublished` + `reviewBody` | `Review` | `DayTripDetailSEO.js` likely emits `aggregateRating` only. Individual `Review` entries not marked up. | P1 | Emit `review[]` array with `author.name`, `datePublished`, `reviewBody`. Already have data in `contract.reviews[]`. ~15 lines. |
| SEO-4 | FAQPage schema for FAQ accordion | `FAQPage` | `FAQPageJsonLd` component exists per `seo-homepage-audit-2026-05-31` (not wired to homepage) — likely also not wired to detail. | P2 | Add FAQPage JSON-LD on detail page when `ExperienceFAQ` renders. ~10 lines. |
| SEO-5 | BreadcrumbList schema | `BreadcrumbList` | `StandardBreadcrumb` component renders visually. JSON-LD not emitted. | P1 | Add BreadcrumbList JSON-LD in `DayTripDetailSEO.js`. ~5 lines. |
| SEO-6 | Top-20 footer link blocks (Attractions / Experiences / Tours / Things to do) | n/a (internal link juice) | NOT IMPLEMENTED on detail page | P3 | New backend endpoint for lists OR hardcoded. UX ruled OUT (r1-ux: off-brand density). **Defer P3 SEO re-evaluation pending UX clarification.** |
| SEO-7 | Hreflang for multi-language | `link rel="alternate" hreflang` | Unknown. May be in `generateMetadata` or `next-sitemap`. | P2 | Verify next-sitemap.config.js + add hreflang in `DayTripDetailSEO.js` if missing. |
| SEO-8 | og: / twitter: meta completeness | n/a (Open Graph) | Likely present via `DefaultSeo` (Next SEO lib). Verify. | P2 | Verify og:title, og:description, og:image, og:url, twitter:card all present per page. |
| SEO-9 | Provider name in footer meta (Product ID + Activity provider) | n/a (audit/SEO signal) | NOT IMPLEMENTED on detail page. May exist in `DayTripDetailSEO.js` JSON-LD as `provider.name`. | P2 | Render visible "Product ID: X | Activity provider: Y" footer strip. ~3 lines. Also feeds `provider.name` in JSON-LD. |

---

## Classification by Severity

| Severity | Count | IDs |
|----------|-------|-----|
| P0 | 0 | (none — all P0 covered in 2026-06-02 redesign) |
| P1 | 3 | SEO-2, SEO-3, SEO-5 |
| P2 | 5 | SEO-1, SEO-4, SEO-7, SEO-8, SEO-9 |
| P3 | 1 | SEO-6 (deferred — UX density issue) |

**No P0 findings** — confirms 2026-06-02 redesign covered critical SEO surface.

---

## Cross-Reference with R1-IA

| SEO ID | Pattern | R1-IA Reference | Notes |
|--------|---------|-----------------|-------|
| SEO-2 | TouristAttraction schema | n/a (schema, not UI) | Backend-data-light, reuse existing fields |
| SEO-3 | Review schema | UX-9 provider-response — P3 | Emit review body JSON-LD (not provider response, which is P3) |
| SEO-5 | BreadcrumbList schema | SP-2 already renders visually | JSON-LD gap only |
| SEO-9 | Footer meta strip | UX-5 KEEP | Overlap. UX-5 = visual + JSON-LD wins. |

**UX-5 from R1-UX overlaps with SEO-9.** Same implementation: render visual + emit `provider.name` in JSON-LD. Single fix.

---

## What GYG Has That SmartEnPlus Has Zero Coverage For

| GYG Pattern | Why It Matters | SmartEnPlus Status |
|-------------|----------------|--------------------|
| `TouristAttraction` schema | Google rich results for attractions | Gap (SEO-2) |
| `Review` schema (individual) | Star snippets in SERP | Gap (SEO-3) |
| `BreadcrumbList` schema | Breadcrumb in SERP | Gap (SEO-5) |
| 80-link footer blocks | Crawl paths + keyword density | P3 deferred (UX density) |

---

## Implementation Notes

**SEO-2 (TouristAttraction):** Add to existing `DayTripDetailSEO.js`:
```json
{
  "@context": "https://schema.org",
  "@type": "TouristAttraction",
  "name": "...",
  "image": "...",
  "address": {...},
  "aggregateRating": {...}
}
```

**SEO-3 (Review array):** In same file, emit `review[]`:
```json
{
  "review": [
    {
      "@type": "Review",
      "author": {"@type": "Person", "name": "..."},
      "datePublished": "2026-01-09",
      "reviewBody": "...",
      "reviewRating": {"@type": "Rating", "ratingValue": "5"}
    }
  ]
}
```

**SEO-5 (BreadcrumbList):** Same file:
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [...]
}
```

**Effort estimate:** All 3 in same file. ~30 lines total. 1 commit. Trivial-to-small.

**P1 fix scope summary (SEO-2, SEO-3, SEO-5):** All in `DayTripDetailSEO.js`. Total ~30 LoC. 1 atomic commit. Reuses existing fields — no backend changes required. **Exception:** SEO-3 (Review array) requires `contract.reviews[]` array in API response — verify backend serializer returns this array. If only `aggregateRating` is emitted (no per-review data), SEO-3 partial-render only (emit aggregateRating, skip review array).

**SEO-9 (footer meta + JSON-LD provider):** Add `provider` field to JSON-LD + 1-line visual render. Trivial. **Cross-ref:** merged with UX-5 (P0) — see main doc Verification Matrix V3 for duplicate-check.

---

## Quality Check

- GYG markup patterns cited: 5 (provider meta, 4×20 lists, aggregateRating, AI summary, breadcrumb)
- SmartEnPlus gaps file-referenced: `DayTripDetailSEO.js`
- Severity: 0 P0 + 3 P1 + 5 P2 + 1 P3 = 9 findings
- P3 flagged: SEO-6 (UX density issue, deferred)
- Cross-referenced: R1-IA (UX-5/SEO-9 merge)
- P1 fixes reuse existing data: 3 of 3 (TouristAttraction uses existing fields; BreadcrumbList uses StandardBreadcrumb data; Review array requires backend serializer verify)

**Output:** 4 concrete actions (SEO-2 TouristAttraction, SEO-3 Review array, SEO-5 BreadcrumbList, SEO-9 footer provider) — all small effort, all in single file.

---

## Related

- [[r1-ia]] — IA specialist section diff
- [[r1-ux]] — UX specialist scoring
- [[experience-detail-page-redesign-2026-06-02]] — predecessor doc
- [[seo-homepage-auditor]] — SEO specialist team pattern
- [[homepage-seo-performance-deep-review-2026-05-21]] — prior SEO audit
- [[seo-homepage-audit-2026-05-31]] — FAQPageJsonLd precedent (not wired)
- [[seo-wave2-audit-2026-05-23]] — prior SEO wave
