# ParseISO Null Guard for Date Sort

## Summary
`parseISO(null)` returns Invalid Date → `compareAsc` returns NaN → page crashes. Guard pattern: `const dateA = a.field ? parseISO(a.field) : new Date(0);`. Apply to any `parseISO`/`format` from date-fns over user/JSON-supplied dates.

## Context
`date-fns` is the date utility library. `parseISO(string)` parses an ISO 8601 string into a Date. `compareAsc(a, b)` returns -1, 0, or 1. Both are null-tolerant in the sense that they don't throw on `null` — they return `Invalid Date` or `NaN` silently, then crash downstream when a number is expected.

## Problem
A list sorted by a date field (reviews, bookings, contracts) where the date is optional. Example: a contract has `published_at` (nullable — drafts have no published date). Sorting contracts by `published_at` descending:

```js
contracts.sort((a, b) => compareAsc(parseISO(a.published_at), parseISO(b.published_at)));
```

If `a.published_at === null`, `parseISO(null)` returns `Invalid Date`. `compareAsc(InvalidDate, Date)` returns `NaN`. `Array.prototype.sort` treats `NaN` results as 0 (or undefined behavior in some engines), but the actual crash happens later — when MUI Table tries to format the Invalid Date with `format(invalidDate, 'yyyy-MM-dd')`, the call throws because `format` doesn't accept Invalid Date.

The crash is far from the cause. The error stack points at the MUI render, not at the sort.

## Details
The guard pattern:

```js
const toDate = (iso) => (iso ? parseISO(iso) : new Date(0));

contracts.sort((a, b) => compareAsc(toDate(a.published_at), toDate(b.published_at)));
```

`new Date(0)` is the Unix epoch (1970-01-01). Sorting nulls to the bottom (ascending = oldest first) is the common case. For "nulls to top" use `new Date(8640000000000000)` (max Date) or invert the comparator.

Extract the guard as a helper:

```js
// helpers/dateGuards.js
import { parseISO } from 'date-fns';

export const toDate = (iso, fallback = new Date(0)) => (iso ? parseISO(iso) : fallback);
```

Then use `toDate(value)` everywhere you sort/format optional dates.

For `format(invalidDate, '...')` cases, also guard:

```js
import { format } from 'date-fns';
const dateLabel = value ? format(parseISO(value), 'yyyy-MM-dd') : '—';
```

`'—'` (em dash) is the standard "no value" affordance in tables.

## Decision
- Always wrap `parseISO` over user/JSON-supplied data with a null/empty guard
- Use `toDate(value)` helper for sorts, `value ? format(parseISO(value), pattern) : '—'` for displays
- `new Date(0)` is the default fallback (epoch). Invert comparator or use `new Date(8640000000000000)` if "nulls first" is desired.
- Apply to all date-fns functions that don't natively handle null (`parseISO`, `format`, `differenceInDays`, etc.)

## Tradeoffs
- Pro: One helper, one pattern, no scattered null checks
- Pro: Crash is impossible — `new Date(0)` is always a valid Date
- Pro: Standard "—" affordance is consistent across the app
- Con: Hides data quality issues. A contract with `published_at === null` is a draft — sorting it to the bottom with epoch date is correct UX, but a logged warning would help catch the root cause.
- Con: The helper is a small abstraction. For one-off sorts, the inline guard is fine. The helper pays off when 3+ sort sites exist.

## Consequences
This is a generic pattern that recurs in any code sorting by date from API data. Apply by default to all new sort + format sites over optional dates. Add a `toDate` helper to `helpers/dateGuards.js` and import it everywhere. New devs reaching for `parseISO` over optional data should default to `toDate(value)`.

The root cause (operator data missing `published_at`) is worth a backend log + admin warning, but the frontend cannot rely on the backend to always populate fields.

## Related
- [[react-state-no-op-guard-side-effect-prevention]] — sibling "guard before passing to library" pattern
