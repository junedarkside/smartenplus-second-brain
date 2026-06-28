# Three-Layer Gap Coverage Matrix

## Summary
Conceptual framework for computing SmartEnPlus catalog coverage gaps. Three independent layers (Reference / Live / Admin) + five coverage lenses (Join / Private / Charter / Experiences / Activities).

## Context
Audit started 2026-06-28. Need systematic way to identify "what should exist vs what does exist vs what's loaded but unsurfaced." See [[products-live-catalog-audit]].

## Details

### Three layers

| Layer | Source | Definition | What it tells us |
|---|---|---|---|
| Reference | Curated location set ([[thailand-location-coverage-framework]]) | Master universe of TH + cross-border locations | What *should* exist |
| Live | `sitemap.xml` + public APIs | What's actually published for sale | What we *actually* sell |
| Admin | Prod read-only Django shell | What operators have loaded | What operators *have loaded* |

### Two gap types

- **Gap** = Reference ∖ Live. Reference location has no live surface.
- **Sub-gap** = Admin ∖ Live. Operator has inventory loaded but it isn't surfacing. Different fix path (data/pipeline fix, not BD outreach).

### Three gap dimensions

| Dimension | Question |
|---|---|
| Location coverage | Does reference location have ≥1 active Route or Contract departing? |
| Route coverage (A→B) | Does natural-demand pair have an active Route? |
| Activity-type coverage | Does each `service_category` value have ≥N contracts at a major hub? |

### Five coverage lenses (per gap)

| Lens | BE filter | Surfacing |
|---|---|---|
| Join | `contract_type=JOIN` ∩ `service_category ∈ {TRANSPORTATION, TRANSFER}` | Shared scheduled |
| Private | `contract_type=PRIVATE` ∩ transport cats | Private vehicle |
| Charter | `contract_type=CHARTER` ∩ transport cats | Hourly charter |
| Experiences | `service_category=MULTI_DAY_TOUR` | Multi-day packages |
| Activities | `service_category ∈ {DAY_TOUR, SPA_WELLNESS, EVENT_TICKET, ATTRACTION_TICKET, FOOD_DINING, ACCOMMODATION}` | Single-day + services |

### Status taxonomy per lens

`missing` / `partial` / `covered`. One gap entry can have multiple lens statuses — e.g. a route may be Join-covered but Charter-missing.

### Computation

```sql
-- Gap (Reference - Live)
SELECT r.station_name
FROM reference_set r
LEFT JOIN live_stations l ON r.station_name = l.station_name
WHERE l.station_name IS NULL;

-- Sub-gap (Admin - Live)
SELECT a.station_name, a.contract_type
FROM admin_active_contracts a
LEFT JOIN live_contracts l
  ON a.departure = l.departure AND a.arrival = l.arrival AND a.contract_type = l.contract_type
WHERE l.contract_id IS NULL;
```

### Discovery recipe

See [[live-catalog-discovery-protocol]] for the full step-by-step (sitemap → APIs → Django shell → cross-ref).

## Decision
Use 3-layer matrix as canonical gap taxonomy. 5 lenses as the per-gap tagging schema. Append-only snapshots per [[products-live-catalog-audit]] cadence (every 4–6 weeks).

## Tradeoffs

- **Pro:** Separates "what should exist" (BD gap) from "what's loaded but hidden" (data fix). Different owners, different urgency.
- **Pro:** 5-lens tagging reveals partial coverage — e.g., has Join but lacks Charter is actionable BD signal.
- **Con:** Reference set is curated, not exhaustive — false negatives possible (gaps that aren't real because no demand).
- **Con:** Admin layer requires Django shell access — barrier for non-engineering BD staff.

## Related
- [[live-catalog-discovery-protocol]]
- [[thailand-location-coverage-framework]]
- [[operator-outreach-question-template]]
- [[transportation-category-audit]]
- [[products-live-catalog-audit]]