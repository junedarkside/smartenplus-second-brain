# WordPress FAQPage Deprecation Note

## Summary
Google deprecated `FAQPage` rich results in August 2023. Do NOT emit `FAQPageJsonLd`. Use visible `<details>`/`<summary>` markup + canonical only. This is a recurring SEO trap encountered twice in the codebase (homepage FAQ removed; /help/faqs recreated without schema).

## Context
`schema.org/FAQPage` used to generate expandable Q&A rich results in Google SERPs. Google retired the rich result surface in August 2023, citing overuse and inconsistent quality. The schema itself is still valid (parsers accept it), but emitting it produces zero SERP benefit while still carrying the maintenance cost.

## Problem
Two separate codebases / PRs reintroduced `FAQPageJsonLd` after the deprecation: one added it to the homepage, another added it to a `/help/faqs` page. Both were reverted after audit. The deprecation is old enough to be forgotten by new audits, so the same recommendation reappears every ~6 months from a developer who didn't know.

## Details
The right pattern for FAQ content:

```jsx
// Visible, accessible, no schema
<details>
  <summary>How do I cancel a booking?</summary>
  <p>Go to My Bookings, select the trip, and click Cancel...</p>
</details>
```

What NOT to do:

```jsx
// DEPRECATED — no rich result, no benefit
<script type="application/ld+json">
{ "@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [...] }
</script>
```

Acceptable companion markup (not deprecated):
- `Article` schema on the page if the FAQ is editorial content.
- `BreadcrumbList` for navigation.
- Standard `<details>`/`<summary>` for UX (no schema needed).

The deprecation affects only the **rich result** — the schema is still valid in a strict sense, and the page may still rank for FAQ-style queries via normal web search. The lost benefit is the SERP-visible Q&A carousel.

## Decision
No `FAQPage` JSON-LD in any new or existing code. Add a code-search guard: `grep -r "FAQPage" pages/ components/` should return zero results. Document the deprecation in the SEO audit checklist so it doesn't reappear in 6 months.

## Tradeoffs
- Pro: zero maintenance cost for a schema that produces no benefit.
- Pro: cleaner JSON-LD output (less for parsers to validate).
- Con: removes the (currently zero) possibility that Google re-enables the rich result.
- Con: requires the FAQ UX to be honest visible content, not schema-laundered SEO.

## Consequences
- New FAQ-style content ships as plain `<details>`/`<summary>` with the same accessibility and SEO value.
- The recurring audit finding stops recurring.
- Any future Google re-enabling of FAQ rich results would be visible in industry news; the deprecation is permanent unless Google announces otherwise.

## Related
- [[structured-data-schema-patterns]] — umbrella for all schema decisions; FAQPage is the canonical example of "valid schema, no benefit."
- [[seo-homepage-specialist-team]] — homepage was the first site to ship the deprecated schema; the team guardrail catches the next attempt.
