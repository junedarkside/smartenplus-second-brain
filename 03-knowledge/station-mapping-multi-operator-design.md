---
name: station-mapping-multi-operator-design
description: Why operator_station_id (single string) is enough today, n8n-proxy pattern decision, Supabase RouteID connection, and when to revisit.
metadata:
  type: project
---

# Station Mapping — Multi-Operator Design Decision

## Summary

`OperatorStationMapping` single `operator_station_id` field is sufficient as long as all operators route through an n8n proxy that normalizes per-operator API params. No schema changes needed until a direct-API operator onboards.

## Decision

**Use n8n proxy as the normalization layer.** Each operator gets their own n8n workflow node that accepts the standard `?from=X&to=X&date&time` shape and translates to the real operator API (different param names, POST body, auth headers, etc.). Admin only configures:
1. `operator.seat_availability_api_url` = n8n webhook URL per operator.
2. `OperatorStationMapping.operator_station_id` = the ID n8n passes through to the operator.

**Why:** Backend hardcodes `?from=X&to=X&date&time` URL shape (`operators/views.py:1030-1036`). Supporting per-operator param schemas in Django would require a `param_template` field + string interpolation — premature complexity with zero concrete demand.

## Supabase RouteID Connection

`https://npehhtcobshckhefrqhw.supabase.co/rest/v1/RouteID` = route/station-ID table mirrored into Supabase for OTA sync. Columns: `Route` (text name), `ID` (int — the `operator_station_id` staff enter), `Operator` (text). Staff enter the `ID` as `operator_station_id` when creating mappings for that operator.

**`Operator` column now LIVE (shipped 2026-07-22).** Table is now multi-operator, filterable by operator name. Current rows all populated **`Lomprayah`** — canonical operator name finalized by Supabase team (earlier drafts wrote "Lomphaya"/"Lompraya"; "Lomprayah" is correct). Match the exact `Operator` model row when implementing. Example rows (Lomprayah): `10` = Koh Phangan, `11` = Koh Samui (Pralarn Pier), `14` = Hua Hin, `15` = Phuket, `16` = Surat Thani (Tapee Pier), `39` = Bangkok (Pinklao) (VIP BUS). Route names encode transport mode ("(VIP BUS)" vs pier) — one operator spans modes.

**Auto-sync now unblocked (not yet built).** With the `Operator` column live, `OperatorStationMapping` rows could be auto-synced from Supabase (filter `Operator=X` → pull that operator's `ID`s) instead of manual entry — removing the hand-entry step. Manual entry is still the current path. Revisit building a sync job when a second operator's rows are populated in Supabase.

## When to Revisit

- A direct-API operator joins (bypasses n8n) with different param shape → add `station_id_param_name` to `Operator` model.
- An operator needs extra per-station params (terminal code, gate, etc.) → add `extra_params JSONField` to `OperatorStationMapping`.
- **A reseller contract sells another operator's seats (SmartEnPlus reselling Lomprayah) → mapping lookup hardcoded to `contract.operator` breaks. Fix = `seat_check_operator` FK on Contract.** This case has now materialized → [[seat-availability-reseller-operator-gap]].

## Fixes Applied (2026-07-22)

| Fix | File | What |
|-----|------|------|
| `getAllOperators` truncation | `store/api/operatorsApi.js:70` | Added `?page_size=200` + `transformResponse` |
| Pre-fill operator from filter | `station-mapping/index.js openAdd()` | `{ ...EMPTY_FORM, operator: operatorFilter }` |
| Humanize unique error | `station-mapping/index.js catch` | Maps "unique set" → friendly message |
| Helper texts | `station-mapping/index.js` dialog | Disabled field reason + station ID context |

## Related

[[master-state]] · [[products-live-catalog-audit]]
