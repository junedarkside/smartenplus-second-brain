# Soft-404: API answers 200 with an empty payload

## Summary
`notFound` in ISR must key on what the backend actually returns. Some SmartEnPlus endpoints return 200 with empty collections for unknown ids, so a `res.ok` / 404 check alone leaves a 200 soft-404.

## Context
- `/admin-dashboard-routes/home/<from>/<to>/` for an unknown pair: **200** `{routes:[], contracts:[], route_faq:{…nulls}}`. `/trips/zzzz/yyyy` served 200 full meta.
- `product-detail/<slug>/` unknown: axios throws with `error.response.status === 404`; the old catch rendered a 200 "Trip Not Available".

## Rule
- Return `{ notFound: true, revalidate: 300 }` for: confirmed 404, OR 200 with every content collection empty (routes AND contracts).
- Keep soft 200 for contracts-only pages (real inventory, no editorial route info) and for 5xx/timeouts/network errors, so ISR keeps the last good page. This is the only valid `notFound`-in-catch case and it is status-gated: `error.response?.status === 404`.
- `revalidate: 300` (not 3600): `fallback: 'blocking'` hides routes created within the hour.
- Read `res.status` before `res.json()`; do not throw on 404 into the generic catch.
- Probe the real endpoint with curl before choosing the branch; the report assumed 404 and was wrong.

## Tests worth keeping
Empty payload → notFound; 404 → notFound; 502 → soft page, no `notFound`; timeout (no `response`) → soft page, revalidate 30. Fixtures that used an empty response as a stand-in for a good page must switch to contracts-only.

## Related
[[never-notfound-in-catch-block]] · [[pages-router-notfound-return-shape]] · [[tiered-empty-page-noindex-strategy]] · [[nextjs-rewrites-beforefiles-shadowed-by-dynamic-page]]
