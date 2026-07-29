# WP-GraphQL Batch Hydration by databaseId (FE-side)

## Summary
When Django stores only a WordPress `databaseId` (e.g. a blog bookmark's sentinel-CT object_id), hydrate the title/slug/image on the **frontend** via one WP-GraphQL batch query — keep WordPress the source of truth, no Django→WP HTTP coupling.

## Problem
Blog bookmarks persist only `wordpress_post_id` (WP is authoritative for post content). The Saved page needs real titles + deep links. Resolving server-side would put a WP HTTP call inside the Django list endpoint (slow, couples the repos). Resolving one-post-at-a-time on the FE = N calls.

## Pattern
One RTK Query in `blogApi` (WP GraphQL endpoint), `posts(where: { in: [ids] })`:
```js
getPostsByDatabaseIds: builder.query({
  query: (ids = []) => ({ url: '', method: 'POST', body: JSON.stringify({
    query: `query GetPostsByIds($in: [ID]) {
      posts(first: 100, where: { in: $in }) {
        nodes { databaseId slug title featuredImage { node { sourceUrl } } }
      } }`,
    variables: { in: ids.map(String) }
  })}),
  transformResponse: (res) => (res?.data?.posts?.nodes || []).reduce((m, n) => {
    m[n.databaseId] = { title: n.title, slug: n.slug, image: n.featuredImage?.node?.sourceUrl || null };
    return m;
  }, {}),
}),
```
Page collects the blog ids from the bookmark list, calls once (`skip` if none), passes the `{[databaseId]: {...}}` map into each row.

## Why
- **One call for all rows** — no N+1 at the browser.
- **WP stays source of truth** — no title copy stored in Django, no staleness.
- **Map return shape** = O(1) row lookup by id, order-independent.

## Gotchas
- WP GraphQL `where: { in: [...] }` takes `[ID]` (stringify the ids).
- WP titles carry HTML entities (`&amp;`) — render plain (safe) or decode if fidelity matters.
- Blog routes by **slug**, but bookmark stores **databaseId** → this query is the id→slug bridge; without it the row can't deep-link.

## Related
- [[adr-saved-page-product-favorites]] — Saved page blog rows shipped this
- [[batched-genericfk-hydration]] — BE counterpart (contract/product hydration)
