# react-api-field-access-null-guard-pattern

## Summary
API contract fields rendered client-side must guard null/undefined/empty before access: `contract.ratecard.map(...)` crashes if `ratecard` is null; `Math.max(...[])` returns `-Infinity`; `item.operator.operator_name` throws if `operator` missing.

## Why It Matters
SSR/ISR pages serialize API responses that may omit optional nested objects. One null `ratecard` or `operator` crashes the whole list render, not just one card. These crashes surface as blank pages / error boundaries, not graceful degradation.

## Detail
```jsx
// CRASH — ratecard null → TypeError; empty array → -Infinity
rate: Math.max(...contract.ratecard.map(i => i.selling_rate))

// SAFE — guard length, default to 0
rate: contract.ratecard?.length ? Math.max(...contract.ratecard.map(i => i.selling_rate)) : 0,

// CRASH — operator missing
{item.operator.operator_name}
// SAFE
{item.operator?.operator_name}
```
Rule: any `arr.map`, `Math.max/min(...arr)`, or `a.b.c` chain on API data needs a guard. `Math.max(...[])` = `-Infinity` (not 0) — always guard empties.

## Constraints / Gotchas
- Spread into `Math.max/min` on an empty array yields `-Infinity`/`Infinity` — guard the `.length` first, don't rely on a sentinel.
- Filter loops iterating `contract.route.departure_station` across many contracts: one bad row crashes the whole filter. Optional-chain every nested access in loops.

## Related
- [[trip-page-full-audit]] — C2/C3/C4/M2 crash bugs source
- [[activities-day-tour-page-review]] — same pattern on activities
