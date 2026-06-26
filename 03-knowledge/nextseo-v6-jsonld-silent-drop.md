# next-seo v6 — jsonLd Key Silently Dropped

## Summary
next-seo v6 `NextSeo` (and `DefaultSeo`) props type has NO `jsonLd` field. Passing `jsonLd: [...]` in the props object is silently ignored — schemas never render in HTML.

## Problem
`pages/blog/index.js` built 4 JSON-LD schemas (Organization, WebSite, BreadcrumbList, CollectionPage) and returned them as `jsonLd: [...]` inside a seoConfig object spread into `<NextSeo {...seoData} />`. Live site had 0 JSON-LD blocks despite 4 schemas in code. Discovered 2026-06-21 during SEO audit repro.

## Root Cause
`node_modules/next-seo/lib/types.d.ts:358-378` — `NextSeoProps` interface has no `jsonLd` field. TypeScript doesn't error because `{...seoData}` spread hits "extra props tolerated" behavior.

next-seo emits JSON-LD ONLY via dedicated components: `ArticleJsonLd`, `BreadcrumbJsonLd`, `WebPageJsonLd`, etc.

**Important nuance (verified 2026-06-26):** the dedicated `*JsonLd` components (`FAQPageJsonLd`, `BreadcrumbJsonLd`, `OrganizationJsonLd`, `ProductJsonLd`, `ArticleJsonLd`, `WebPageJsonLd`, …) DO render in v6 — only the `jsonLd` prop on `NextSeo`/`DefaultSeo` is dropped. So the rule is: never use the `jsonLd` prop; use either a dedicated `*JsonLd` component OR a raw `<script type="application/ld+json">`. `components/trips/search/FilterTripsSEO.js` uses `BreadcrumbJsonLd`/`OrganizationJsonLd`/`ProductJsonLd` + `FAQPageJsonLd` (r9).

**⚠️ Gotcha — exact export names matter (r9 build break):** the FAQ component is `FAQPageJsonLd`, NOT `FaqJsonLd`. A wrong name imports `undefined`; `<UndefinedComponent>` throws **React #130 (`args[]=undefined`)** at render. It only fires when the conditional renders — r9's `{faqMainEntity?.length > 0 && <FaqJsonLd/>}` only crashed on FAQ-bearing routes (e.g. `/trips/hatyai/penang`), so local dev on a no-FAQ route (`bangkok/koh-samui`) missed it; `next build` (prerendering the real FAQ route) caught it. **Always verify the export name** (`node -e "console.log(typeof require('next-seo').FAQPageJsonLd)"`) + **test the populated-data path, not just any route.**

## Fix Pattern
Replace `jsonLd` key with raw `<script>` tags, same pattern as `pages/homepagev2.js`:

```jsx
// WRONG — schema never renders
const seoData = { title: '...', jsonLd: [schema1, schema2] }
return <NextSeo {...seoData} />

// CORRECT — raw script tags
const seoData = { title: '...' }
return (
  <>
    <NextSeo {...seoData} />
    {[schema1, schema2].map((schema, i) => (
      <script
        key={i}
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
      />
    ))}
  </>
)
```

## Files Fixed
- `pages/blog/index.js` — 4 schemas (Organization/WebSite/BreadcrumbList/CollectionPage)
- `pages/blog/tags/[slug].js` — 1 schema (BreadcrumbList)

## Detection
```bash
grep -r "jsonLd:" pages/ components/
```
Any hit = dead schema. Fix with raw `<script>` pattern above.

## Related
- [[seo-audit-reconciliation-2026-06-21]] — finding #17
- [[trip-detail-server-side-seo-pattern]] — correct schema-in-SSR pattern
