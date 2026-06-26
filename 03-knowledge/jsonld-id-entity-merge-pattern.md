# JSON-LD @id Entity Merge Pattern

## Summary
When the same real-world entity (Organization, Person, etc.) is emitted in JSON-LD on **multiple pages**, give every copy the **same `@id`** so Google/AI engines merge them into one entity. Omitting `@id` (or using different ones) splits the entity → conflicting signals, wrong-domain attribution, lost E-E-A-T.

## Problem
Two failure modes observed on smartenplus.co.th:
1. **Dual BlogPosting** — blog posts emitted a canonical BlogPosting + a raw Yoast `@graph` Article node pointing at the unused `blog.smartenplus.co.th` subdomain. No shared `@id` → Google treated them as two competing article entities, AI engines cited the wrong domain. ([[seo-aeo-geo-live-audit-2026-06-22/r6-external-reconciliation-2026-06-25]] C4)
2. **About page** had zero JSON-LD; homepage had the only TravelAgency but with no `@id`. Adding a second TravelAgency to About without a shared `@id` would have duplicated the org entity.

## Pattern
```jsx
// Homepage — canonical org entity, declare the @id
{
  "@context": "https://schema.org",
  "@type": "TravelAgency",
  "@id": `${origin}/#organization`,   // <-- the anchor
  "name": "SmartEnPlus", ...
}

// About page (or any other page) — SAME @id → Google merges
{
  "@context": "https://schema.org",
  "@type": "TravelAgency",
  "@id": `${origin}/#organization`,   // matches homepage → one entity
  "identifier": { "@type": "PropertyValue", "name": "TAT License", "value": "11/06622" },
  ...
}
```
The `@id` is an IRI (usually `${siteOrigin}/#organization`, `/#website`, or a slug). Same `@id` across pages = same entity; fields merge. The page that declares the richest set (TAT license, address, sameAs) wins the merged result.

## When to use
- Org/LocalBusiness/Organization emitted on >1 page (home + about + footer-driven).
- Author `Person` referenced from every blog post (should point to a real `/author/{slug}` page, not the homepage).
- Product/Service restated on category + detail pages.

## Anti-pattern
Emitting a full duplicate entity without `@id` on each page → N competing entities. This is what the Yoast `@graph` did (different `@id` per domain).

## Detection
Grep for `@type` blocks lacking `@id` on entity types:
```bash
grep -rn '"@type": "TravelAgency"\|"@type": "Organization"' pages/ components/ | ...
```
Any org/Person block without a matching `"@id"` is a split risk.

## Related
- [[seo-aeo-geo-live-audit-2026-06-22/r6-external-reconciliation-2026-06-25]] (C4 dual BlogPosting, About schema)
- [[nextseo-v6-jsonld-silent-drop]] — raw `<script>` is the reliable emit path for these blocks
- [[structured-data-schema-patterns]]
