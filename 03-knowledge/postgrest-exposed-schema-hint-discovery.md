---
name: postgrest-exposed-schema-hint-discovery
description: PostgREST/Supabase leaks its full exposed-schema list in the error hint on any invalid Accept-Profile — use it to discover schemas with only the anon key, no service-role.
metadata:
  type: reference
---

# PostgREST Exposed-Schema Discovery via Error Hint

Supabase/PostgREST rejects a request for a non-exposed schema with error code `PGRST106` and a
`hint` that **lists every exposed schema**:

```
Accept-Profile: __probe__
→ {"code":"PGRST106",
   "hint":"Only the following schemas are exposed: api, lompraya, public, contract_rate, gmail12go, gmailklook, gmailsmart",
   "message":"Invalid schema: __probe__"}
```

The root introspection endpoint (`/rest/v1/`) needs the **service_role** key ("Only the `service_role`
API key can be used for this endpoint"). But the hint above leaks the same schema list to the **anon key**.

## Use

Fire one deliberately-bad-schema request, parse the hint, cache the list:

```js
const { error } = await supabase.schema('__probe__').from('AnyTable').select('*').limit(1)
const schemas = parseExposedSchemas(error?.hint || error?.message || '') // split on ", " after "exposed:"
```

- `supabase-js` v2 exposes the hint at `error.hint` (`PostgrestError`).
- Cache module-level — the list is session-stable; don't re-probe per query.
- If a table isn't in the default schema (`api`/`public`), address it with `.schema(name)` /
  `Accept-Profile: <name>` header. A missing table returns `PGRST205` ("Could not find the table
  '<schema>.<Table>' in the schema cache") — different from the `PGRST106` bad-schema case.

## Applied

admin-dashboard `hooks/useOperatorRouteIds.js` — discovers the operator's Supabase schema to load
`RouteID` station ids without a backend proxy. See [[supabase-per-operator-schema-routeid]].

## Related

[[station-mapping-multi-operator-design]] · [[master-state]]
