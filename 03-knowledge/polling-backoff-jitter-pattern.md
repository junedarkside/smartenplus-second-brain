# HTTP Polling: Exponential Backoff + Jitter Pattern

## Problem
Fixed-interval polling (e.g., 5s) × N guests = linear request growth → Gunicorn overload. Need: auto-throttle when idle, instant resume on activity, stop when conversation closes.

## Math
```
100 guests × 12 req/min (5s fixed) = 1,200 req/min
100 guests × 2 req/min (30s max backoff) = 200 req/min  ← 6× reduction
```

## Algorithm

```javascript
const BASE_MS = 5_000;
const MAX_MS = 30_000;
const JITTER_MS = 2_000;

// After each poll:
// - New messages → reset idle → next in BASE_MS
// - No new messages → increment idle → next in min(BASE * 1.5^idle, MAX) + random(0..JITTER)
function nextInterval(idleCount, hasNewMessages) {
  if (hasNewMessages) return BASE_MS;
  const exp = Math.min(BASE_MS * Math.pow(1.5, idleCount), MAX_MS);
  return exp + Math.random() * JITTER_MS;
}
```

Jitter purpose: spread bursts. Without jitter, N clients back off to same interval and fire simultaneously.

## Stop-on-Close
Backend returns `conversation_status` in poll response. FE stops poll loop when `'closed'`:
```javascript
if (res.data?.conversation_status === 'closed') {
  onConversationClosed?.();
  return; // no scheduleNext — loop stops
}
```

## 429 Handling
```javascript
if (res.status === 429) {
  const retryAfter = parseInt(res.headers['retry-after'] || '30', 10);
  scheduleNext(retryAfter * 1000);
  return;
}
```

## Backend: DRF ScopedRateThrottle
```python
# throttles.py
class CsPollThrottle(ScopedRateThrottle):
    scope = 'cs_poll'

# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': { 'cs_poll': '60/minute' }
}

# views.py MessageListView
throttle_classes = [CsPollThrottle]
```

## Full Hook Skeleton
```javascript
// idleCountRef resets to 0 on new messages or on effect re-mount
// setTimeout ref stored for cleanup on unmount
// enabled=false → no poll (chat closed or kill switch off)
```

## Key Rules
- Always add jitter — prevents thundering herd after backoff
- Reset idle on ANY new message (not just count > 0)
- Stop-on-close saves BE requests for permanently closed convs
- 429 → use Retry-After header, not fixed delay
- Max interval ~30s — user UX acceptable for idle chat

## Source
Implemented 2026-06-23 session #155. File: `hooks/useChatPolling.js`. Throttle: `cs/throttles.py`, `cs/views.py`.
