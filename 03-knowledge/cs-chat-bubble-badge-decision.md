# CS Chat Bubble Badge Decision

## Summary
FE chat bubble unread pill: `bg-orange-500`, 99+ cap, staff-only + closed-status gate. Debated 2026-07-14 via 3-agent structured debate.

## Context
Customer-facing CS chat widget (`ChatBubble.js` + `ChatWidget.js`). FAB in bottom-right. Unread count badge shown top-right of FAB when staff messages arrive while chat is closed.

## Decision

### What ships
- **Color:** `bg-orange-500` (changed from `bg-red-500`)
  - Red = error/danger semantic axis. CS unread is informational — staff replied, not an alert.
  - Orange = notification axis. Visually distinct on blue FAB (`bg-blue-600`).
- **Cap:** `99+` — correct for a 1:1 CS chat. Customer will never see 99+ in practice; badge signals "unread exist", not precise count. Standard iOS/Gmail/Slack pattern.
- **Counting gate:** staff-only (`sender !== 'customer' && sender !== 'system'`) + `state.status === 'closed'` — correct. No self-count noise, no system message spam.
- **Reset:** on `OPEN` action → `unreadCount: 0` — correct.
- **Geometry:** `min-w-[20px] h-5 rounded-full` — correct for FAB context. Vault unified-badge-system-pattern applies to admin card clusters, NOT FAB buttons.

### Unified badge pattern scope clarification
`unified-badge-system-pattern.md` was written for admin dashboard operator-card badge clusters (MUI `Chip`, 28px). Customer-facing FAB badge is a different surface — compact pill, own geometry rules.

## Deferred

| Item | Reason deferred |
|------|----------------|
| `unreadCount` localStorage persistence | Needs namespace, TTL, server reconciliation design. Not a one-liner. |
| Open-but-not-scrolled unread tracking | Requires scroll position hook + last-read cursor. Separate UX ticket. |
| Reducer-level unit test for `ADD_MSGS` gate | Current tests cover `ChatBubble` display only; gate logic untested at reducer level. Low risk, low priority. |

## Root Bug Fixed (2026-07-14 session #245)
Transport hooks were gated on `state.status === 'open'`. Closing chat stopped realtime/polling → no messages ever arrived while closed → `unreadCount` stayed 0 → badge never rendered.

**Fix in `ChatWidget.js`:**
```diff
- enabled: state.status === 'open' && USE_REALTIME
+ const transportActive = !!state.conversationId && state.status !== 'need_email' && state.status !== 'need_otp';
+ enabled: transportActive && USE_REALTIME
```
Transport now runs whenever `conversationId` exists (open OR closed). Auth-gate states excluded. Verified working — staff reply in AD → badge appears on FE bubble.

## Files Changed
- `components/chat/ChatBubble.js` line 16: `bg-red-500` → `bg-orange-500`
- `components/chat/ChatWidget.js`: transport gate fixed (`transportActive` replaces `status === 'open'`)
- Branch `fix/chat-bubble-unread-pill-color` → merged `develop` → pushed `01d8d617`

## Related
- [[cs-architecture-decision]]
- [[cs-chat-getstream-hybrid-2026-07-13]]
- [[unified-badge-system-pattern]]
