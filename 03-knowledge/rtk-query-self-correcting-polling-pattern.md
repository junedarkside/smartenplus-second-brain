# RTK Query Self-Correcting pollingInterval Pattern

## Summary

RTK Query reads `pollingInterval` from hook options on every render. Derive it inline from previous render's query result — no `useState`/`useEffect` needed.

## Problem

Anti-pattern: `useState` + `useEffect` to manage `pollingInterval`:

```js
// WRONG — CLAUDE.md violation: "derive inline, never in useEffect"
const [hasOpenTicket, setHasOpenTicket] = useState(false);
const { data } = useMyQuery(arg, { pollingInterval: hasOpenTicket ? 60000 : 0 });
useEffect(() => {
  setHasOpenTicket(data?.tickets?.length > 0);
}, [data?.tickets?.length]);
```

Problems:
1. Violates CLAUDE.md: "Derive inline or useMemo — never in useEffect"
2. One extra re-render per state change
3. One cycle lag before polling starts/stops
4. When two components subscribe to same cache key, one's `pollingInterval: 0` is defeated by the other's timer

## Solution

Inline derivation from previous render's result:

```js
// CORRECT — no state, no effect
const { data } = useMyQuery(arg, {
  pollingInterval: (data?.tickets ?? []).some(t =>
    ACTIVE_STATUSES.includes(t.request_status)
  ) ? 60000 : 0,
});
```

`data` inside options = previous render's value (from outer scope closure). RTK re-reads `pollingInterval` each render → gate self-corrects naturally:
- First render: `data = undefined` → `pollingInterval: 0` → RTK fires mount fetch anyway (default behavior)
- Response arrives → re-render → `data` has value → `pollingInterval` evaluates correctly

## When NOT to poll in child components

If a parent component already subscribes to the same RTK cache key with its own poll, the child should NOT add its own `pollingInterval`. Two subscribers = two timers. RTK deduplicates the network request but both timers run independently — child's `pollingInterval: 0` cannot stop parent's timer.

```
// [bookingId].js — PARENT owns the poll
useGetCustomerRequestsQuery(bookingId, { pollingInterval: 60000 });

// ChangeRequestsSection — CHILD just reads cache
useGetCustomerRequestsQuery(bookingId, {
  refetchOnMountOrArgChange: true,
  // no pollingInterval — parent owns it
});
```

## Live examples

- `pages/my-trip/index.js` — OTA self-polling query (fixed `09e3f955`)
- `pages/bookings/[bookingId].js:28-34` — parent polls tickets, derives `hasActiveTicket` for a DIFFERENT query's interval (correct pattern)
- `components/bookings/ChangeRequestsSection.js` — child display, no poll (fixed `09e3f955`)

## Related

- [[polling-backoff-jitter-pattern]] — exponential backoff for high-concurrency surfaces
- [[ota-flow-e2e-scan-2026-06-30]] — where this pattern was identified and fixed
