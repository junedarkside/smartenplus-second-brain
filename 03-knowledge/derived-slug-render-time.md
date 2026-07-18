# Derived Slug at Render Time

## Summary
When a backend entity lacks a `slug` column, derive it client-side via `slugify(name)` at JSON-LD/build time instead of migrating the schema.

## Context
`/locations` (#252) needed `<ListItem>.url = ${domain}/locations/${slug}`. Backend `Location` model has `location_name` but no `slug` column. Adding a migration + backfill = deploy risk + DB write per row. Locations are <30, slug derivation is pure.

## Decision

```js
import { slugify } from '../helpers/slugify';

const itemListElements = allLocations
  .filter(location => location.location_name)
  .map((location, index) => ({
    '@type': 'ListItem',
    position: index + 1,
    item: {
      '@type': 'TouristDestination',
      name: capitalizeWords(location.location_name),
      url: `${domain}/locations/${slugify(location.location_name)}`,
    },
  }));
```

The page route handler must already use the same `slugify(name)` to resolve `/locations/[slug]` → entity, otherwise the JSON-LD `url` points at a 404.

## When to migrate vs derive

| Signal | Action |
|--------|--------|
| <100 rows, slug never changes | Derive at render |
| >100 rows + slug indexed/searched | Migrate column + backfill |
| Slug must be stable across renames (don't 404 old links) | Migrate + manual slug override field |
| Slug is user-editable (e.g. operator vanity URL) | Migrate — must persist |
| Pure SEO JSON-LD only | Derive is fine |

## Tradeoffs
- **Pro:** zero deploy risk, no DB migration, no backfill job.
- **Con:** if `slugify()` algo changes (e.g. unicode handling), existing external links 404 silently. Pin the helper version or snapshot its output.
- **Con:** two consumers (page resolver + JSON-LD builder) must call `slugify(name)` identically. Extract a single `getLocationURL(location)` helper if risk of drift matters.

## Consequences
- Pure-function deps on `helpers/slugify` + `helpers/capitalizeWords` — keep them pure, no `Date.now()`/locale state.
- If `/locations/[slug]` resolver ever normalises the slug (lowercase trim), JSON-LD must mirror — add a test.

## Related
- `helpers/slugify.js` — current impl
- `pages/locations/[slug].js` — resolver; verify same slugify call
- [[structured-data-schema-patterns]] — `useXStructuredData` consumers
