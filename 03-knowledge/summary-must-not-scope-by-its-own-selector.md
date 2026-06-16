# A summary must not be scoped by its own selector

## Summary
When summary cards double as filter selectors, compute the summary on the queryset
**before** that selector's filter is applied — otherwise clicking a card collapses every
count to the clicked subset.

## Context
Contracts page (admin, 2026-06-16). Status cards Total / Active / Inactive / Deleted are
both a glanceable tally AND clickable status filters. Clicking **Active** put
`status=active` in the URL.

## Problem
`ContractViewSet.list` computed the summary from `self.get_queryset()` — which already
applied the `status` filter. So clicking Active scoped the summary to active-only:

| Click | Total | Active | Inactive |
|-------|-------|--------|----------|
| none  | 73    | 59     | 14       |
| Active| **59**| 59     | **0**    |

The cards are meant to stay global so the user sees the whole breakdown and knows what
each card would filter to. Selection is shown by the highlighted border, not by mutating
the numbers.

## Decision
Give `get_queryset(apply_status_filter=True)` a flag. The visible rows + pagination keep
the status filter (default). The summary calls `get_queryset(apply_status_filter=False)`
so it reflects every OTHER active filter (operator, search, type…) but not the status
selector itself. The per-status counts are explicit `.filter(is_actived=…, is_deleted=…)`
on that status-less queryset.

## Lesson
- A control that is both "show me the breakdown" and "filter by X" must compute the
  breakdown independent of X. The other filters legitimately scope it; X does not.
- General pattern: a faceted-count sidebar should count each facet against the query
  with that facet's own selection removed (the classic "facet counts" rule).
- Pin it with a test: summary identical across `?status=active|inactive|deleted`.

## Related
- [[adr-contract-soft-delete-2026-06-16]]
- [[serializer-field-omission-starves-ui]]
