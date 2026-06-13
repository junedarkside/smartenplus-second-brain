# TouristTrip Schema ISO8601 Departure Time

## Summary
`TouristTrip` schema `departureTime` and `arrivalTime` must be full ISO 8601 with date prefix (`"2026-05-20T08:00:00+07:00"`) — not just `"T08:00:00+07:00"`. The prefix-less form is silently invalid; Google rejects it without surfacing a console error, and rich results are disabled.

## Context
JSON-LD's `schema.org/TouristTrip` (and the broader `Trip` family) defines `departureTime` as `DateTime` per schema.org. A `DateTime` MUST include the date. A time-only string starting with `T` is a `Time`, not a `DateTime`. Google's Rich Results Test passes the syntactic check but fails the semantic one, and the result is "no rich result" with no warning visible in normal devtools.

## Problem
In `trip-detail-deep-review-2026-05-20` (finding H2), the schema was emitting `"departureTime": "T08:00:00+07:00"` — time-only. Google accepted the JSON-LD parse, accepted the field, but silently disabled rich result eligibility. No `error` in Search Console, no `warning` in the Rich Results Test (it shows green), but trip carousel eligibility was 0% for months.

## Details
The fix is one line, but the rule is strict:

```json
{
  "@context": "https://schema.org",
  "@type": "TouristTrip",
  "name": "Phuket to Krabi Day Tour",
  "departureTime": "2026-05-20T08:00:00+07:00",
  "arrivalTime": "2026-05-20T17:30:00+07:00",
  "itinerary": {
    "@type": "Place",
    "name": "Krabi"
  }
}
```

Required format: `YYYY-MM-DDTHH:MM:SS±HH:MM`. The timezone offset (`+07:00`) is mandatory for Thailand-based trips; UTC (`Z`) is acceptable but loses local-time semantics.

Validation rule for code review: any `departureTime`/`arrivalTime` value MUST match `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$`.

## Decision
Reject any PR that emits a time-only `departureTime`/`arrivalTime`. Add a unit test that asserts the regex against the rendered schema.

## Tradeoffs
- Pro: rich result eligibility restored, no ambiguity in the data.
- Pro: regex check is one line in CI.
- Con: requires a real date at build time — the schema cannot be a static template with placeholders.
- Con: dynamic dates per trip require backend cooperation to return a proper ISO string.

## Consequences
- All future `Trip`/`TouristTrip`/`Flight`/`BusTrip` schemas inherit this rule.
- Audit checklists for schema work MUST include the regex assertion.
- The Google silent-failure pattern is worth knowing: green test, no rich result, no log.

## Related
- [[structured-data-schema-patterns]] — the umbrella atom for all schema work; this is one of its most-recurring pitfalls.
