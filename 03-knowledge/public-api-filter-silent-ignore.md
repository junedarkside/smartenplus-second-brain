# Public API Filter Silent Ignore

## Summary
SmartEnPlus public API silently ignores admin-style query filters (`?is_actived=false`, `?end_date__gte=YYYY-MM-DD`) — returns same dataset as default. Critical caveat for any audit/data work done via public API only.

## Context
Discovered 2026-06-28 during [[products-live-catalog-audit]] Phase 1. Tested API behavior to determine if Public API Snapshot could substitute for Django shell. **Conclusion:** it cannot — admin ground truth unreachable via public API.

## Details

### Silent-ignore filters observed

| Filter | Expected behavior | Actual behavior |
|---|---|---|
| `?is_actived=false` | Returns inactive contracts | Returns same 1224 active contracts |
| `?end_date__gte=2026-06-28` | Returns contracts with end_date ≥ date | Returns same 1224 contracts |

### Detection test

```bash
curl -s "https://api.smartenplus.co.th/contract/?is_actived=false&page_size=2" | jq '.count'
# Returns 1224 (same as default), NOT 0 or different
```

If `count` matches default → filter ignored, NOT applied.

### Why this matters

- **Cannot detect sub-gaps** (Admin yes, Live no) via API alone
- **Cannot filter by end_date** for "currently active" subset
- **Cannot surface inactive inventory** (operators have contracts loaded but disabled)
- Forces direct DB access for any comprehensive audit

### Public API surface (what it CAN do)

| Filter | Works? | Note |
|---|---|---|
| `?service_category=X` | ✅ | Returns filtered list |
| `?page=N&page_size=N` | ✅ | Standard pagination |
| `?summary=true` | ✅ | Compact response |
| `?has_trips=true` | ✅ | Stations with active routes |
| `?destinations_page=true` | ✅ | Destination-shape response |
| `?is_actived=false` | ❌ | Ignored |
| `?end_date__gte=` | ❌ | Ignored |

## Decision
When auditing SmartEnPlus catalog via public API only, **assume Live layer only** — do not infer inactive contracts, sub-gaps, or admin ground truth. For full coverage, Django shell or DB access required. Document this limitation in any audit report derived from public API.

## Tradeoffs

- **Pro:** Clear pattern, easy to detect with one curl test
- **Pro:** Saves wasted hours trying to surface inactive inventory via API
- **Con:** Some admin queries might genuinely work but not been tested (e.g., `?operator_id=X`, `?station_id=X`) — verify before assuming

## Related

- [[live-catalog-discovery-protocol]]
- [[live-catalog-audit-public-api-limitations]]
- [[products-live-catalog-audit]]
- [[api-smartenplus-co-th-endpoint-inventory]]