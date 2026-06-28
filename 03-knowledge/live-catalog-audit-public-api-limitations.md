# Live-Catalog Audit — Public API Limitations

## Summary
Concrete list of what Public API Snapshot CAN and CANNOT detect during SmartEnPlus catalog audits. Use this checklist before claiming "full audit done."

## Context
Compiled 2026-06-28 from [[products-live-catalog-audit]] Phase 1 findings. Critical for any future audit that wants to avoid overstating its completeness.

## Details

### ✅ What public API audit CAN detect

| Layer | Detection method |
|---|---|
| Reference ∖ Live (gaps) | Cross-ref reference set against live sitemap + API |
| Live layer coverage | `?service_category=` counts + sitemap station list |
| Operator concentration | Per-contract `operator_name` aggregation |
| Geographic skew | Per-operator location inference from contract names |
| Service category emptiness | `?service_category=X` returning `count=0` |
| Top routes by popularity | `booked_count` field on contracts |
| Demand proxy | `booking_count_30d`, `booking_count_yesterday` |
| Review signal | `average_rating`, `review_count` |
| Charter route scarcity | Type=CHARTER aggregate |

### ❌ What public API audit CANNOT detect

| Layer | Why |
|---|---|
| Admin layer (inactive contracts) | `?is_actived=false` silently ignored — see [[public-api-filter-silent-ignore]] |
| end_date filtering | `?end_date__gte=` silently ignored |
| Station FK pivot | API returns `trip` integer + parseable name, not station FK |
| Route.query_count demand signal | Admin-only field |
| Sub-gaps (Admin yes, Live no) | Cannot see inactive contracts |
| Exact route pair coverage | Parsing contract name string is approximate |
| Reference set stations missing from DB Station table | No Station table exposed |
| Operator inventory not loaded | Cannot see draft contracts |

### Implication for audit claims

When publishing "Phase 1 Public API Snapshot":
- ✅ CAN claim: "X% of service categories have zero inventory"
- ✅ CAN claim: "Charter routes = 0.5% of transport catalog"
- ✅ CAN claim: "SPA_WELLNESS has single-operator concentration"
- ❌ CANNOT claim: "Reference set has X% coverage of live catalog"
- ❌ CANNOT claim: "These specific routes are missing (vs unsurfaced)"
- ❌ CANNOT claim: "Operators have Y inactive contracts ready to surface"

## Decision
Always qualify audit reports with the layer detected (Live only vs Live + Admin). For full Reference + Live + Admin coverage, Django shell access required (Phase 1.5 of [[products-live-catalog-audit]]).

## Tradeoffs

- **Pro:** Clear capability matrix — no overclaiming
- **Pro:** Faster than waiting for DB access (Phase 1 shipped without it)
- **Con:** Some "missing" categories may have inactive inventory (sub-gap)
- **Con:** Geographic gap analysis approximate without station FK pivot

## Related

- [[live-catalog-discovery-protocol]]
- [[public-api-filter-silent-ignore]]
- [[three-layer-gap-coverage-matrix]]
- [[api-smartenplus-co-th-endpoint-inventory]]
- [[products-live-catalog-audit]]