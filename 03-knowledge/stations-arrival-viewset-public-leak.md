# Stations Arrival ViewSet — Public Contract Leak

## Summary
`ListProductsByArrivalStationViewSet` (`stations/views.py`) is a public, unauthenticated endpoint whose `get_queryset` filtered Contracts by arrival-station slug ONLY — neither `is_actived` nor `is_deleted`. It leaked inactive contracts (pre-existing bug) and would have leaked soft-deleted ones.

## Why it matters
The `is_actived` invariant from soft-delete ([[contract-soft-delete-is-actived-invariant]]) could NOT save this path — it never read `is_actived` in the first place. Found during the soft-delete audit. Fixed by filtering `is_actived=True, is_deleted=False`.

## Pattern (reusable)
When adding a hide/exclude flag to a model, **grep ALL public query paths, not just the obvious list/detail viewset.** `grep -rn "Contract.objects" --include="*.py"` surfaced ~14 `is_actived` paths across 5 apps (products, pages_info sitemap, recommendations, carts, stations) — two of which (`stations`, `carts/utils.py:62`) checked neither the new flag nor `is_actived`. The "load-bearing 2 filters + invariant" assumption only holds if every remaining path keys off the invariant flag; verify, don't assume.

## Note
Frontend does not call `trip-by-arrival-station` (grep of smartenplus-frontend source found no usage) — likely legacy/external. Narrowing its queryset is safe (only removes results).

## Related
- [[contract-soft-delete-is-actived-invariant]]
- [[adr-contract-soft-delete-2026-06-16]]
