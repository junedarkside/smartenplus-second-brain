# CS Guest Chat: Storm Risk, Kill Switch & Mitigation Investigation

## Summary
100 concurrent guests = 1,200 req/min → 2× Gunicorn ceiling → prod down. No kill switch exists. 3-agent debate surfaced 4 critical blockers in the proposed design.

## Context
Triggered by question: "how to limit guests from storming BE with chat polls." Scope: frontend `useChatPolling.js` + backend `cs/` app + admin dashboard kill switch. 3-agent Scrutinize debate (Backend / Frontend / Dashboard) run 2026-06-23.

## Problem in Numbers

Each guest tab polls `GET /api/cs/messages/` every 5s = 12 req/min.
Prod Gunicorn: 2 threads × 200ms/req avg = ~10 req/s usable = ~600 req/min ceiling.

| Concurrent guests | req/min | req/s | Impact |
|---|---|---|---|
| 10 | 120 | 2 | safe |
| 50 | 600 | 10 | at ceiling |
| 100 | 1,200 | 20 | queue backlog → timeouts cascade |
| 200 | 2,400 | 40 | OOM kill → ALL services down |

**Marketing email scenario:** 503 Klook guests all open chat → ~600 req/min within 4 minutes → prod down. Not just chat — cart, payment, checkout all share same 2 Gunicorn threads.

**Secondary risk:** DB connection pool exhaustion → payment webhook can't connect → "payment failed" shown while money was charged.

## Current Gaps (Audit 2026-06-23)

| Gap | Location | Severity |
|---|---|---|
| No throttle on `GET /api/cs/messages/` | `cs/views.py` MessageListView | CRITICAL |
| Fixed 5s poll, no backoff | `hooks/useChatPolling.js:4` | HIGH |
| No stop-on-close signal | `useChatPolling.js` + `cs/views.py` | HIGH |
| No kill switch | entire stack | HIGH |
| No conversation creation rate-limit | `cs/views.py:83-100` | MEDIUM |
| `useRateLimitedQuery.js` exists but CS ignores it | `hooks/useRateLimitedQuery.js` | MEDIUM |

## 4 Critical Blockers (Debate Verdicts)

**BLOCKER 1 — `conversation.status` missing from poll response**
`MessageListView` returns only `{ results, next_cursor }`. "Stop poll on closed" mitigation silently fails — `res.data.conversation_status` = `undefined` always, condition never fires, polling continues forever after staff closes conv.
Fix: add `conversation_status` to `MessageListView` response.

**BLOCKER 2 — Flag read permission wrong**
`IsAdminOrIsStaff` at `accounts/permissions.py:4-14` requires authenticated staff to read the feature flag. ChatWidget serves unauthenticated guests. Guest GET → 403 → fail logic undefined.
Fix: flag GET = `AllowAny`. Flag PATCH = `IsAdminOrIsStaff`.

**BLOCKER 3 — No fail-safe on flag endpoint failure**
If `/api/cs/feature-flags/cs_chat/` returns 500, ChatWidget must **fail-open** (default `enabled=true`). Fail-closed = chat disappears for all guests on any backend hiccup → support tickets flood.

**BLOCKER 4 — Silent unmount bad UX**
Flag flip mid-conversation = open chat window disappears, message history lost, no feedback. Guest has no way to know if last message was read.
Fix: show "Chat temporarily unavailable" banner, disable send, don't unmount component.

## 5-Layer Mitigation Plan (Ranked by Effort/Impact)

### Layer 1 — Stop Poll on Closed Conversation (FE+BE, highest ROI)
Backend: add `conversation_status` to `MessageListView` response (fixes BLOCKER 1).
Frontend `useChatPolling.js`: if `data.conversation_status === 'closed'` → dispatch CLOSE, `return` (no next `setTimeout`).
**Effect:** ~80% of long-lived ghost sessions stop immediately after staff closes chat.

### Layer 2 — Exponential Backoff + Jitter (FE only, `useChatPolling.js`)
Track `idleCountRef`. `delay = min(5000 × 1.5^idleCount, 30000) + random(0..2000ms)`.
Reset `idleCount=0` when new messages arrive. Timeline: 5s→7s→10s→15s→22s→30s (stays).
Jitter prevents thundering herd (100 guests backed off to 30s all fire simultaneously).
**Effect:** idle active-conv load drops from 12 req/min → 2 req/min within 5 polls.

### Layer 3 — Handle 429 Gracefully (FE only, `useChatPolling.js`)
On `error.response?.status === 429`: read `Retry-After` header (default 30s), `setTimeout(poll, wait)`, `return`. Without this, frontend hammers retries on 429 → worsens storm.

### Layer 4 — DRF Throttle on Poll Endpoint (BE only)
`cs/throttles.py`: `CsPollThrottle(ScopedRateThrottle, scope='cs_poll')`.
`settings.py`: `'cs_poll': '60/minute'`.
Apply to `MessageListView`. Returns 429 + `Retry-After`. Layer 3 handles the response.

### Layer 5 — nginx Rate-Limit (Infra, last resort)
`limit_req_zone $binary_remote_addr zone=cs_poll:10m rate=10r/s` on `/api/cs/messages/`.
Per-IP (coarser than per-token). Ineffective for hotel/tour-group shared NAT.
Use as DDoS/bot protection only — Layer 4 is more accurate for real guests.

## Kill Switch Design

**Mechanism:** `FeatureFlag` model in Django DB. Toggle via Django admin (MVP, Day 1) + admin dashboard UI (Week 2).

**Model** (add to `cs/models.py`):
```python
class FeatureFlag(models.Model):
    key = models.CharField(max_length=100, unique=True)
    enabled = models.BooleanField(default=True)
    updated_by = models.ForeignKey('accounts.Account', null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)
```

**Endpoints** (add to `cs/views.py` + `cs/urls.py`):
- `GET /api/cs/feature-flags/<key>/` → `AllowAny`, cache 60s, fail-open default
- `PATCH /api/cs/feature-flags/<key>/` → `IsAdminOrIsStaff`

**Frontend hook** (`hooks/useFeatureFlag.js`, new):
```javascript
const [enabled, setEnabled] = useState(true)  // fail-open
useEffect(() => {
  fetch('/api/cs/feature-flags/cs_chat/')
    .then(r => r.json())
    .then(d => setEnabled(d.enabled))
    .catch(() => {})  // silent — keep true
}, [])
```

**Effect timeline:** Staff toggles OFF → within 60s all new page loads skip ChatWidget mount → active sessions show "Chat temporarily unavailable" banner.

**Kill switch options ranked:**
1. Django admin `/securelogin/` → instant, audit trail built-in, zero extra FE work (MVP)
2. Admin dashboard settings page → better UX for non-technical staff (Week 2)
3. nginx `return 503 on /api/cs/` → hardest kill, blocks ALL CS including staff inbox

## Build Order

```
1. BE: FeatureFlag model + migration + Django admin registration
2. BE: GET (AllowAny) + PATCH (IsAdminOrIsStaff) flag endpoints
3. BE: Add conversation_status to MessageListView response
4. BE: CsPollThrottle on MessageListView (60/minute)
5. FE: useFeatureFlag hook (fail-open, default true)
6. FE: useChatPolling mitigations (stop-on-close, backoff, 429 handling)
7. FE: ChatWidget graceful unavailable state (banner + disabled send)
8. Dashboard: custom toggle UI in settings page (deferred Week 2)
```

Steps 1-4 deploy independently. Steps 5-7 require Steps 2+3 live first.

## Open Questions

- [ ] Conversation creation (`POST /api/cs/conversations/`) rate-limit per email? Currently unlimited for closed→open cycles.
- [ ] Is SmartEnPlus behind Cloudflare or direct EC2? Determines whether `$remote_addr` or `X-Forwarded-For` is correct for nginx Layer 5.
- [ ] Flag cache TTL: 60s acceptable for emergency kill, or should tab-focus trigger re-fetch?
- [ ] Should kill switch toggle fire Telegram alert to ops? Reuse `send_telegram_message` (`carts/utils.py:690`).

## Related
[[cs-architecture-decision]] · [[cs-gap-debate-verdicts]] · [[cs-subsystem-weakpoints]] · [[feature-flag-kill-switch-pattern]]
