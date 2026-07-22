---
name: supabase-per-operator-schema-routeid
description: Operator station ids live in per-operator Supabase schemas (RouteID table). Schema name is a lowercased 8-char truncation of the operator name — not derivable — so match by name-prefix + confirm via the Operator column.
metadata:
  type: reference
---

# Supabase Per-Operator Schema — RouteID

`https://npehhtcobshckhefrqhw.supabase.co` stores each operator's station ids in its **own schema**,
not one shared table. Each schema has a `RouteID` table:

| Column | Meaning |
|--------|---------|
| `Route` | station / pier name (e.g. `Chumphon (airport)`) |
| `ID` | the `operator_station_id` staff map to (string, e.g. `"36"`) |
| `Operator` | operator display name (e.g. `Lomprayah`) |

Today only **`lompraya`** exists (39 rows, `Operator="Lomprayah"`). Exposed schemas seen:
`api, lompraya, public, contract_rate, gmail12go, gmailklook, gmailsmart` (the `gmail*`/`contract_rate`
ones are unrelated — denylist them).

## Gotcha — schema name is NOT derivable from operator name

`Lomprayah` → schema `lompraya`: **lowercased + truncated to 8 chars** (Postgres identifier habit).
The full `lomprayah` schema is **invalid** (verified). So:

- Don't slugify/guess. Don't hardcode a map (fragile as operators grow).
- **Discover** the exposed-schema list from the PostgREST hint
  ([[postgrest-exposed-schema-hint-discovery]]), then pick the schema that is a **case-insensitive
  prefix** of `operator_name` (longest match wins), minus a non-operator denylist.
- **Confirm** the match: after querying `RouteID`, keep only rows where `row.Operator` (lowercased)
  equals the operator name. Zero confirming rows → treat as no-schema (false prefix match) → free-text.

## Applied

admin-dashboard `helpers/operatorRouteIds.js` (`parseExposedSchemas`, `pickSchemaForOperator`) +
`hooks/useOperatorRouteIds.js`. Powers the `operator_station_id` autocomplete in the Station Mapping
dialog (`pages/routemanagement/operators/station-mapping/index.js`). Reuses the shared
`helpers/supabaseClient.js` (Django-JWT-injected client; `.schema(name)` supported in supabase-js v2).

## Related

[[postgrest-exposed-schema-hint-discovery]] · [[station-mapping-multi-operator-design]] · [[seat-availability-reseller-operator-gap]]
