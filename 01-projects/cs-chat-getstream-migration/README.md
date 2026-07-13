# CS Chat → GetStream Migration (Hybrid, Free Tier)

> **STATUS:** AUDIT-COMPLETE · **CONDITIONAL** · 2026-07-13 (session #242). See [[audit-2026-07-13]]. NO code shipped. 4 blockers (B1–B4) + Python 3.9↔SDK≥3.10 conflict clear before Phase 1.

## Summary

Migrate CS chat hot path from current stack (Django + Supabase Realtime + custom JWT mint + Channels-dormant) to **GetStream Build (free tier)** with hybrid scope:

- **NEW conversations** route through GetStream (`stream-chat-react` + `getstream` Python SDK)
- **OLD conversations** stay on Django polling / Supabase Realtime fallback (no backfill)
- **Supabase stays** for OTA booking mirror + sync tasks (orthogonal to chat)
- **Django** keeps canonical archive (`cs.Message` written by webhook + defensive sync task)

## Why now

Current realtime chat malfunctioning on multiple fronts (per user report 2026-07-13):

1. Reconnect / gap-fill bug (L1 fix shipped `88e845de` but flaky)
2. Token refresh / 401-403 silent fail (Supabase JWT mint fails → realtime dies without recovery)
3. OTA guest / auth-switch race (wrong conv shown on identity change)
4. Image-send broken (just-shipped `53f30576`, deploy pending)
5. **No prod notification** when new message arrives
6. **Chat history display** — FE fixed (Django pagination, `useChatRealtime.js:91-115`); AD works (`ConversationDetail.js:44-47`) — **stale, drop or narrow** (audit)

In-house fix cost = 3-6 sprints of careful rework. GetStream ships all of this out-of-box.

## Decision rationale

**GetStream Build (free) tier:**
- $0/mo, 1,000 MAU, 100 concurrent
- Sufficient for current volume (tens of widgets/day)
- Comfortable headroom for 12-18mo growth

**Hybrid scope** (not full swap):
- Old conversations preserved on Django (read-only via existing `MessageListView` polling)
- Zero historical data loss
- Reversible: flip `cs_chat_transport=legacy` → all convs back on Django

**Supabase kept** (not full vendor exit):
- OTA booking mirror (`CsOtaBooking`) needs Supabase Realtime for sync tasks
- Migration cost (Supabase → DynamoDB / S3-only) not justified by chat alone

## Tier qualification — BLOCKING before Phase 1

| Check | Status (audit-2026-07-13) |
|---|---|
| 1. Build plan = $0 (no CC) | ✅ CONFIRMED |
| 2. Maker credit NOT required | ✅ Build = free tier; Maker = red herring |
| 3. MAU definition | ⚠️ Phase 0 |
| 4. Message retention | ✅ Indefinite ("as long as plan active") |
| 5. Webhook on Build | ⚠️ Phase-0 POC (public docs silent) |
| 6. PDPA region | ✅ Singapore selectable on Build — sign DPA + lock SG + Sec 29 SCC |

**If any check fails → STOP + escalate.** Use vendor-lockin-critic must-haves from [[getstream-migration-debate-2026-07-13]].

## Implementation phases (audit-ready)

See [[implementation-plan-2026-07-13]] for full detail.

- **Phase 0** (1 sprint): Tier qualification spike + POC
- **Phase 1** (1 sprint): Backend token + webhook
- **Phase 2** (2 sprints): Frontend Stream hook
- **Phase 3** (1 sprint): Admin staff hook
- **Phase 4** (1 sprint): Image pipeline parity
- **Phase 5** (0.5 sprint): Cutover flag + monitoring
- **Phase 6** (4-6 weeks): Shadow parallel-run + full cutover

**Total: ~6.5 sprints + 4-6 weeks shadow** ≈ 3 months calendar.

## Architecture

```
┌─────────────────┐
│  NEW CONV       │──GetStream──AD/Staff real-time WS
│  (after cutover)│              ↓ webhook archive
└─────────────────┘              ↓
                          Django cs.Message (archive)
                          ↓
                          Supabase cs_messages (OTA sync mirror only)

┌─────────────────┐
│  OLD CONV       │──Django polling (useChatPolling.js)
│  (pre-cutover)  │──or Supabase Realtime fallback
└─────────────────┘
```

**Conv switch:** `Conversation.transport` field — `legacy` | `stream`. Widget dispatches per-conv.

**Source of truth:** Django `cs.Message` (always). Stream = hot path; archive mirror via webhook.

## Estimated cost

| Item | Cost |
|---|---|
| GetStream Build (free tier) | $0/mo |
| Overage risk | Build is HARD-CAPPED (rate-limits on exceed, no paid overage). $0.09/user + $0.99/concurrent = Start PAID tier ($499/mo) only |
| Engineering time | 6.5 sprints (~13 weeks for 1-2 engineers) |
| Vendor count after migration | 2 (Supabase + GetStream) — same risk surface as today |

## Files in this folder

- `README.md` — this file (overview + decision rationale)
- `implementation-plan-2026-07-13.md` — 6-phase audit-ready plan

## Related

- [[getstream-migration-debate-2026-07-13]] — 4-agent debate verdict (parent decision)
- [[cs-chat-getstream-hybrid-2026-07-13]] — ADR capturing this hybrid decision
- [[cs-architecture-decision]] — parent ADR; transport decision lineage
- [[cs-chat-supabase-offload]] — prepared alternative path (NOT executed; superseded for chat by this hybrid)
- [[chat-image-send-server-convergence]] — image pipeline this plan replaces
- [[chat-sender-session-bleed]] — sender-integrity pattern preserved
- [[cs-realtime-be-traffic-design-verdict-2026-07-08]] — BE traffic design constraint (still binding until cutover)

## Critical files (3 repos, read for planning)

### Backend (`smartenplus-backend`)
- `cs/views.py:1334-1406` — `SupabaseTokenView` pattern (mirror for `StreamTokenView`)
- `cs/views.py:62` (`_resolve_guest_token`) + `cs/views.py:426` (`_resolve_message_sender`) — auth resolution helpers
- `cs/models.py` — `Conversation`, `Message` schemas
- `cs/supabase_jwt.py` — `mint_supabase_jwt()` pattern (mirror for `mint_stream_jwt`)
- `cs/tasks.py` — `sync_chat_messages` Celery pattern
- `cs/urls.py` — route registration
- `cs/serializers.py` — conversation list/detail serializer
- `Smartenplus/settings.py` — env var block
- `requirements.txt` — add `getstream`

### Frontend (`smartenplus-frontend`)
- `components/chat/ChatWidget.js` — dispatcher (branch on `conv.transport`)
- `components/chat/ChatPanel.js` — current chat UI (replaced by StreamPanel wrapper)
- `hooks/useChatRealtime.js` — current realtime hook (replaced by `useGetStreamChat`)
- `hooks/useChatPolling.js` — fallback path for old convs (kept)
- `helpers/supabaseClient.js` — current client pattern (mirror for Stream)
- `helpers/chatImage.js` — S3 presigned URL allowlist (extend for Stream CDN)
- `package.json` — add `stream-chat` + `stream-chat-react`

### Admin (`admin-dashboard`)
- `hooks/useStaffChatRealtime.js` — staff realtime hook (replaced)
- `hooks/useStaffInboxRealtime.js` — inbox realtime (swap Supabase source → Stream)
- `store/api/csApi.js` — add `getStreamToken` mutation
- `pages/cs/index.js` — branch `conv.transport === 'stream'` → Stream detail
- `components/cs/ConversationDetail.js` — current detail UI (replaced by Stream wrapper)
- `package.json` — add `stream-chat-react`

## Branch strategy (per CLAUDE.md git policy)

- `feat/be-stream-token-webhook` (BE work)
- `feat/fe-stream-chat-hook` (FE work)
- `feat/ad-stream-staff-hook` (AD work)
- Each PR merge to `develop` only — never `main` directly
- Deploy order: BE → AD → FE (back-to-front pattern)

## Done definition

### This session (vault-only)

- ✅ This `README.md` created
- ✅ `implementation-plan-2026-07-13.md` created
- ✅ `04-decisions/cs-chat-getstream-hybrid-2026-07-13.md` created
- ✅ `index.md` updated
- ✅ `log.md` updated
- ✅ `master-state.md` Section 1 updated to session #241
- ✅ NO code changes to any of 3 repos
- ✅ NO commits
- ✅ NO branches

### Future sessions (post-audit)

- Phase 0 spike → Phase 6 cutover, gated on audit verdict
- Each phase = separate multi-session project
- Audit gate: sign-off from 2+ engineers + 1 ops + 1 legal/PDPA