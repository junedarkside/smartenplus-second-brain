---
name: chat-review-e2e-manual-test-2026-07-07
description: E2E manual test guide for chat feature fixes from deep review (3-repo, 18 bugs). Customer = Chrome :3000 | Staff = Safari :3001 (admin :3001).
metadata:
  type: test-guide
  status: active
  date: 2026-07-07
  branch: fix/chat-review-issues (all 3 repos)
  parent: chat-supabase-migration-plan
---

# Chat Feature Review — E2E Manual Test Guide

> Branch `fix/chat-review-issues` on all 3 repos. Test all fixes before merge to develop.
> Customer surface = Chrome `localhost:3000` | Staff = Safari `localhost:3001`.

## Prerequisites

```bash
# All 3 dev servers running
cd smartenplus-frontend  && npm run dev   # :3000
cd admin-dashboard       && npm run dev   # :3001
cd smartenplus-backend   && python manage.py runserver  # :8000

# Celery worker (for OTP email send)
celery -A Smartenplus worker -l info

# Verify branch
git -C smartenplus-frontend  branch --show-current  # fix/chat-review-issues
git -C admin-dashboard       branch --show-current  # fix/chat-review-issues
git -C smartenplus-backend   branch --show-current  # fix/chat-review-issues
```

Ensure `NEXT_PUBLIC_CHAT_REALTIME=true` in both FE `.env.local` and Admin `.env.local`.

---

## T1 — Guest OTP Flow (FE-B5, FE-B6, FE-B7, BE-S1 deleted)

**What's being tested:** loading state on email submit, no stuck "Verifying…" button, cooldown only fires after send success.

**Chrome (incognito, no session):**
1. Open `localhost:3000` → click blue FAB (bottom-right).
2. Email gate appears. Type a **valid email** (`test@example.com`) → click **"Start chat"**.
3. ✅ Button shows **"Starting…"** and is disabled while request in flight.
4. OTP code form appears. Type **wrong code** (`000000`) → **"Verify code"**.
5. ✅ Error message shown. Button re-enables. Not stuck.
6. Verify correct OTP code sent to email (check SES / test inbox).
7. Type correct code → **"Verify code"**.
8. ✅ Chat panel opens. No stuck "Verifying…" state.

**Resend test:**
9. Repeat from step 1. On OTP step — **disconnect Wi-Fi**, click **"Resend code"**.
10. ✅ Error shown: *"Could not send code. Check your connection."*
11. ✅ No 30s cooldown started (button stays active after reconnect).

---

## T2 — Authenticated Customer Chat (FE-B2 dedupe, FE-D3 token re-mint)

**What's being tested:** messages don't duplicate on re-subscribe; token refresh doesn't tear channel.

**Chrome (logged in as customer):**
1. Open `localhost:3000` → FAB → chat opens (no email gate).
2. Send 3 messages. Confirm all 3 visible, each once.
3. Leave chat open for **15 minutes** (or mock by changing `TOKEN_TTL_MS` in `useChatRealtime.js` to `30_000` for quick test).
4. ✅ After 14min mark — chat still functional, no reconnect flash, no duplicate messages.
5. Send another message.
6. ✅ Message appears once (not duplicated).

**Quick proxy test (no wait):**
- Open DevTools Network. Filter `supabase-token`. Reload page, open chat.
- ✅ Exactly **1 POST /api/cs/supabase-token/** on open.
- Trigger re-render (resize window). ✅ No second mint fired.

---

## T3 — Conversation-Closed Detection Realtime (FE-B1)

**What's being tested:** when staff close conversation, customer panel shows closed state (not stuck open).

**Chrome (customer):**
1. Open chat. Send 1 message.

**Safari (admin `localhost:3001`):**
2. CS Inbox → open conversation → change **Status** dropdown → **closed**.

**Chrome:**
3. ✅ Chat widget transitions to closed state (FAB visible again or banner shown).

> If system message trigger not implemented: staff close fires `onConversationClosed` via next poll or explicit signal. Check `useChatRealtime.js` — system INSERT with `sender: 'system'` + body containing `'closed'`.

---

## T4 — Staff Inbox Realtime + Token Isolation (AD-B1, AD-B2)

**What's being tested:** opening/closing a conversation doesn't deauth the inbox channel; token re-mints proactively.

**Safari (admin):**
1. Open `localhost:3001/cs`. Inbox loads. Note DevTools → Network → `supabase-token`.
2. ✅ **2 POST /api/cs/supabase-token/** on page load (one for inbox hook, one for chat hook when conv selected).
3. Click first conversation → messages load.
4. Click back to list (close detail). Click another conversation.
5. ✅ Inbox list still updating. No auth error in console. No `CHANNEL_ERROR` in console.
6. Open DevTools Console. Confirm no `[useStaffInboxRealtime] token mint failed` or `[useStaffChatRealtime] token mint failed`.

**Multi-tab test:**
7. Open second Safari tab on `localhost:3001/cs`.
8. ✅ Both tabs functional. No console auth errors. Tokens don't clobber each other.

---

## T5 — Staff Send Error Visibility (AD-D2)

**What's being tested:** realtime send failure shows Snackbar, not silent console.warn.

**Safari (admin, DevTools open):**
1. Open a conversation with a customer.
2. In Network tab → block the Supabase URL (`chrome://settings/privacy` → disconnect network or use DevTools Conditions → Offline).
3. Type a message → **"Send"**.
4. ✅ Send button shows `"…"` while pending.
5. ✅ **Snackbar appears** at bottom-center: *"Message not sent. Please try again."*
6. ✅ Not a silent `console.warn` only.
7. Restore network → retry → message sends.

---

## T6 — Sign-Out Clears Supabase Token (AD-S2)

**What's being tested:** after sign-out, no stale staff JWT in memory.

**Safari (admin):**
1. Open CS inbox. Confirm realtime channel active.
2. Sign out (top-right menu).
3. Open DevTools → Application → Memory (or Console). 
4. ✅ No further Supabase realtime events received (channel cleaned up).
5. ✅ No `[useStaffChatRealtime]` errors after sign-out.
6. Sign back in → inbox works again normally.

---

## T7 — Backend: Authenticated Customer First Chat (BE-B1 fixed)

**What's being tested:** `POST /api/cs/conversations/` no longer crashes on first-time auth user.

```bash
# Get a fresh access token for a user with NO existing conversation
TOKEN="<paste fresh accessToken from browser session>"

curl -X POST http://localhost:8000/api/cs/conversations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

✅ Returns `200` with `{id, status, identity_type, ...}`.
✅ No `500` / `FieldError`.
✅ Run twice → same `id` returned (idempotent — returns existing open conv).

---

## T8 — Backend: Inbox N+1 Fixed (BE-D1)

**What's being tested:** inbox list does not issue N+1 queries.

**With Django Debug Toolbar or logging:**
```python
# settings.py (dev only) — add to LOGGING:
# 'django.db.backends': {'handlers': ['console'], 'level': 'DEBUG'}
```

```bash
# With 10+ conversations in DB:
TOKEN="<staff token>"
curl http://localhost:8000/api/cs/conversations/list/?page_size=20 \
  -H "Authorization: Bearer $TOKEN"
```

✅ Django debug panel shows **≤ 5 queries total** (not 60+ for 20 conversations).
✅ Response includes `count`, `results` with `last_message_preview`, `last_message_at`, `unread_count` populated.

---

## T9 — Backend: Supabase JWT TTL is 15min (BE-S3)

```bash
TOKEN="<staff token>"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/cs/supabase-token/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json")

# Decode payload (base64 middle segment)
echo $RESPONSE | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
token = data['token']
payload = token.split('.')[1]
# Add padding
payload += '=' * (4 - len(payload) % 4)
decoded = json.loads(base64.urlsafe_b64decode(payload))
ttl = decoded['exp'] - decoded['iat']
print(f'TTL: {ttl}s (expected 900)')
assert ttl == 900, f'FAIL: TTL is {ttl}s not 900s'
print('PASS')
"
```

✅ TTL = 900s (15 minutes).

---

## T10 — Backend: Auto-Reopen Rate Limit Atomic (BE-B2)

```bash
# Simulate two concurrent sends on a closed conversation
CONV_ID=<id of a closed conversation>
GUEST_TOKEN="<guest token for that conv>"

# Fire two simultaneous POSTs
curl -X POST http://localhost:8000/api/cs/messages/send/ \
  -H "X-CS-Guest-Token: $GUEST_TOKEN" -H "Content-Type: application/json" \
  -d "{\"conversation\": $CONV_ID, \"body\": \"msg1\", \"sender\": \"customer\"}" &

curl -X POST http://localhost:8000/api/cs/messages/send/ \
  -H "X-CS-Guest-Token: $GUEST_TOKEN" -H "Content-Type: application/json" \
  -d "{\"conversation\": $CONV_ID, \"body\": \"msg2\", \"sender\": \"customer\"}" &
wait
```

✅ Both messages created (reopen allowed — count was 0).
```sql
SELECT reopen_count, status FROM cs_conversation WHERE id = <CONV_ID>;
-- reopen_count = 1 (not 2 — atomic increment)
```

---

## T11 — Backend: `has_more` Flag in Message Poll

```bash
CONV_ID=<conv with > 100 messages>
curl "http://localhost:8000/api/cs/messages/?conversation=$CONV_ID&cursor=0" \
  -H "X-CS-Guest-Token: $TOKEN"
```

✅ Response includes `"has_more": true` when 100 results returned.
✅ Response includes `"has_more": false` when < 100 results returned.

---

## T12 — Backend: Pagination Guard (BE-B5)

```bash
TOKEN="<staff token>"
curl "http://localhost:8000/api/cs/conversations/list/?page_size=abc&page=xyz" \
  -H "Authorization: Bearer $TOKEN"
```

✅ Returns `200` with `page_size=20, page=1` defaults (not `500 ValueError`).

---

## T13 — .env.sample Documented (AD-D1)

```bash
grep "CHAT_REALTIME\|SUPABASE_URL\|SUPABASE_ANON" \
  /Users/charuwatnaranong/Desktop/AdminDashBoard/admin-dashboard/.env.sample
```

✅ All 3 vars present with placeholder values.

---

## T14 — Full Chat Flow E2E (Happy Path)

End-to-end smoke test covering both surfaces.

**Chrome (incognito guest):**
1. Open `localhost:3000` → FAB → email gate → submit email → OTP → verify → chat opens.
2. Send message: *"Hello, I need help with my booking."*

**Safari (admin):**
3. `localhost:3001/cs` → inbox → new conversation appears in real-time (< 2s).
4. Open conversation → message visible.
5. Type reply: *"Hi! I'm here to help."* → Send.

**Chrome:**
6. ✅ Staff reply appears in real-time (< 2s), no page refresh.
7. ✅ No duplicate messages.
8. ✅ No console errors in either browser.

---

## Pass/Fail Tracker

| Test | Description | Result | Notes |
|------|-------------|--------|-------|
| T1 | Guest OTP — loading state + resend error | | |
| T2 | Auth customer — no duplicate messages | | |
| T3 | Staff close → customer closed state | | |
| T4 | Staff inbox realtime — token isolation | | |
| T5 | Staff send error → Snackbar visible | | |
| T6 | Sign-out → Supabase token cleared | | |
| T7 | BE: first-time auth customer 200 | | |
| T8 | BE: inbox N+1 fixed (≤5 queries) | | |
| T9 | BE: Supabase JWT TTL = 15min | | |
| T10 | BE: auto-reopen atomic (reopen_count=1) | | |
| T11 | BE: has_more flag in poll response | | |
| T12 | BE: pagination guard (no 500) | | |
| T13 | .env.sample has chat vars | | |
| T14 | Full E2E happy path | | |

---

## Known Limitations / Out-of-Scope

- **T3** requires a system INSERT with `sender: 'system'` and body containing `'closed'` — currently not emitted by backend on conversation close. Polling-mode closes correctly; realtime-mode close detection via system message is a stub. Document as known gap if test fails.
- **Polling mode** (`NEXT_PUBLIC_CHAT_REALTIME=false`): all fixes except token-isolation and proactive re-mint are still relevant. Repeat T1, T7–T12 with realtime disabled.
- **15-min session test (T2)**: takes real time; shortcut with `TOKEN_TTL_MS = 30_000` in dev.

## Related

- [[chat-supabase-migration-plan]] · [[chat-supabase-impl-tasks]] · [[cs-manual-test-flows-b7-e-2026-06-30]]
- Branches: `fix/chat-review-issues` on FE + BE + admin
- Commits: BE `3602349`, FE `80be992c`, Admin `70d0916`
