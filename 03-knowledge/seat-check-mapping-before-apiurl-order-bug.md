---
name: seat-check-mapping-before-apiurl-order-bug
description: check_seat_availability checks OperatorStationMapping existence before checking seat_availability_api_url — operators with neither get a misleading MAPPING_NOT_FOUND instead of the intended graceful "no API configured" null response.
metadata:
  type: reference
---

# Seat-Check: Mapping Check Runs Before API-URL Check (order bug)

`check_seat_availability` (`operators/views.py:1048-1124`) validates `OperatorStationMapping`
existence for both stations *before* checking whether the resolved operator
(`contract.seat_check_operator or contract.operator`) even has
`seat_availability_api_url` set.

## Symptom

Confirmed live on contract `smart-en-plus-co-ltd-hatyai-any-hotel-to-hatyai-airport-202`
(operator = SmartEnPlus's own entity, id 1 — not a real transport carrier, has zero
`OperatorStationMapping` rows and no `seat_availability_api_url`):

Clicking "Check Now" produces `MAPPING_NOT_FOUND` — a warning telling staff to go configure
Station Mapping — instead of the intended `available: null` / "No availability API
configured" graceful response documented in
[[seat-availability-reseller-operator-gap]] as the expected case for "most contracts."

## Why it happens

Code order is: resolve mapping → **if missing, return 400 `MAPPING_NOT_FOUND` immediately**
→ (only reached if mapping exists) check `api_url` → if null, return 200 `available: null`.

Any operator with *neither* a mapping *nor* an API URL always hits the first branch. The
graceful fallback only actually fires for operators that HAVE mappings configured but happen
to lack an API URL — a narrower case than the docs implied.

## Also: AD has no dedicated render for the graceful case even when reached

`SeatAvailabilityChecker.js`'s `renderResult()` has no branch for `available === null` —
it falls into the generic `severity = warning` path with unhelpful copy ("Response received —
check raw data for details"), not the clear "not applicable" message a reader of the vault
docs would expect.

## Fix candidates (neither applied yet — see master-state Section 2, `SEAT-CHECK-MAPPING-ORDER-BUG`)

- **BE (smaller/safer)**: reorder so the `api_url` null-check runs first, before the mapping
  lookup — restores the documented graceful-degradation behavior for any operator lacking
  API capability, regardless of mapping state.
- **FE (more complete UX)**: gate the whole "Check Operator Seat Availability" section's
  rendering in `pages/routemanagement/contracts/[slug].js:499-501` on
  `operator.seat_availability_api_url` being truthy — avoids showing an inert button at all.
  Requires confirming `ContractDetailSerializer` already exposes that field on the operator
  sub-object (not yet confirmed).

## Related

[[seat-availability-reseller-operator-gap]] · [[station-mapping-seat-api-visibility]] ·
[[n8n-seat-search-response-contract]]
