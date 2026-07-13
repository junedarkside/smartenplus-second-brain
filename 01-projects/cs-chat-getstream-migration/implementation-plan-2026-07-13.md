# CS Chat → GetStream Migration Implementation Plan

> **STATUS:** AUDIT-COMPLETE · **CONDITIONAL** · 2026-07-13 (session #242). See [[audit-2026-07-13]].
>
> **Scope:** 6 phases + tier-qualification spike. Read top-down before audit.
>
> **⚠️ 4 blockers (B1–B4) + Python 3.9↔SDK≥3.10 conflict must clear before Phase 1.** Corrections below applied inline by audit.
> **Mirror of:** `/Users/charuwatnaranong/.claude/plans/check-vault-and-cs-fluffy-hejlsberg.md` (vault-clean formatting)

---

## Phase 0 — Spike + Tier Qualification (1 sprint) — BLOCKING

**Goal:** Prove Build tier = $0/mo, webhook available, PDPA region acceptable, end-to-end POC works.

> **AUDIT-2026-07-13 additions (BLOCKING):** (a) **Python conflict** — prod = `python:3.9-alpine`, but `getstream==3.5.*` `requires_python >=3.10,<4.0`. Verify install on 3.9; if it fails, add a Python bump + Dockerfile task (undocumented effort). (b) **PDPA gate simplified** — Singapore region IS selectable on Build at provisioning (NOT US/EU-forced, NOT paid-gated): lock SG, sign DPA, draft Sec 29 SCC. (c) **Webhook-on-Build** stays an empirical POC gate (public docs don't confirm it explicitly).

### Tasks

1. **Tier qualification**
   - WebFetch GetStream Build tier fine print (retention period, MAU counter definition, webhook availability, data region options)
   - Sign up Build plan (use shared team email); screenshot billing page = $0
   - Verify NO Stripe payment method required (free tier enforced)
   - Document MAU counter: `active_user_past_30d` vs `any_connected_user` vs `unique_channel_join`
   - Document message retention: indefinite on Build? 30-day? 90-day?

2. **PDPA gate check (BLOCKING)**
   - Confirm data region options on Build (US / EU / APAC / SG)
   - Request DPA from GetStream via `https://getstream.io/security/` or sales contact
   - Check sub-processor list (cloud provider: AWS? GCP? region per region?)
   - **Decision:** if APAC unavailable on Build → escalate (paid tier may be required)

3. **Backend POC**
   - `pip install getstream` in a feature branch (NOT commit)
   - Create `cs/stream_jwt.py` POC: `mint_stream_jwt(user_id='test-user')` returns valid JWT
   - Create `cs/views.py` POC: `StreamTokenView` returns `{token, conversation_id}`
   - curl from local: mint token for test user → verify JWT structure

4. **Frontend POC**
   - `yarn add stream-chat stream-chat-react` in feature branch (NOT commit)
   - Create `pages/test-stream.js` (temp route): `<Chat client={streamClient}><Channel channel={channel}><MessageList /></Channel></Chat>`
   - Token from `POST /api/cs/stream-token/` POC endpoint
   - Open 2 browser tabs → verify message echo works

5. **Webhook POC**
   - Configure webhook URL on GetStream dashboard pointing to local tunnel (Tailscale or ngrok)
   - Send test message → verify webhook fires with `message.new` event
   - Verify HMAC signature using `STREAM_WEBHOOK_SECRET`
   - Verify event payload contains `event.message.id`, `event.message.user.id`, `event.message.text`

### Decision gate

**PASS criteria (all must be true):**
- Build plan = $0 confirmed
- Webhook available + HMAC signature works
- MAU + concurrent limits adequate for 12-18mo growth projection
- DPA obtained OR data region acceptable for current PDPA posture
- POC: 2-tab message echo works end-to-end

**FAIL criteria (any):**
- Free tier auto-bumps to paid
- Webhook not on Build tier
- DPA unobtainable AND data region outside acceptable jurisdictions
- POC fails any critical step

**If FAIL → STOP, document in vault, escalate to vault owner.**

### Verification

- Screenshot of billing page = $0
- Curl test: `POST /api/cs/stream-token/` returns valid JWT (decodable, contains `user_id`)
- 2-tab browser test: message sent in tab A appears in tab B within 1s
- Webhook test: HTTP POST from GetStream → BE receives + verifies HMAC + writes test row to `cs.Message`
- PDPA checklist: DPA obtained, data region confirmed, sub-processor list reviewed

---

## Phase 1 — Backend Token + Webhook (1 sprint)

**Goal:** Production-grade backend endpoints for token mint + webhook archive.

### Tasks

1. **Dependencies**
   - `requirements.txt`: add `getstream==3.5.*` (PyPI 3.5.0, `requires_python >=3.10,<4.0` — NO 5.x line)
   - **Python conflict (audit):** prod = `python:3.9-alpine`, NOT 3.11. SDK requires ≥3.10. Resolve in Phase 0 (bump Python + Dockerfile, or SDK-incompat fallback).

2. **`cs/stream_jwt.py` (new file)**
   ```python
   from getstream import Stream
   
   def get_stream_client():
       return Stream(
           api_key=settings.STREAM_API_KEY,
           api_secret=settings.STREAM_API_SECRET,
       )
   
   def mint_stream_jwt(user_id: str, scope: str = 'customer', conv_id: str | None = None, ttl: int = 86400) -> str:
       """Mint GetStream JWT. 24h default TTL matches guest_token.
       scope: 'customer' | 'guest' | 'staff'
       conv_id: required for customer/guest; None for staff (unscoped)
       """
       client = get_stream_client()
       return client.create_token(user_id=user_id, expiration=ttl)
   ```
   - **Audit correction:** `mint_supabase_jwt` (`cs/supabase_jwt.py:14`) takes a **claims dict** (TTL default 900s), not positional args — do NOT mirror its signature. Use the getstream SDK `client.create_token(user_id, expiration)` directly (above). 24h TTL ≠ supabase_jwt's 15min default; document the divergence.
   - Type hints + docstring

3. **`cs/views.py` — `StreamTokenView` (new class)**
   - Mirror `SupabaseTokenView` (`cs/views.py:1334-1406`) line-for-line
   - Auth check via existing `_resolve_guest_token` + `_resolve_message_sender` helpers
   - Returns `{token, conversation_id}` for customer/guest; `{token, scope: 'staff'}` for staff
   - `staff` branch requires explicit `scope='staff'` (defensive against admin→customer leakage)
   - Throttle: reuse `CsPollThrottle` (`cs/throttles.py:8`) — mirrors `SupabaseTokenView`'s throttle (`views.py:1337`). No `cs_otp` class exists.
   - URL: `POST /api/cs/stream-token/`

4. **`cs/views.py` — `StreamWebhookView` (new class)**
   - Verify HMAC signature using `STREAM_WEBHOOK_SECRET`
   - Handle events:
     - `message.new` → upsert `cs.Message(stream_id=event.message.id, body=..., sender=mapped, conversation_id=mapped)`
     - `message.updated` → no-op (preserves edit history in Stream)
     - `message.deleted` → soft-delete `cs.Message` (set `is_deleted=True` if field added; else hard-delete is OK for chat per current policy)
   - Idempotency: unique index on `Message.stream_id`; `get_or_create` pattern
   - Sender mapping: `event.user.role` → `Message.sender` enum
   - URL: `POST /api/cs/stream-webhook/` (AllowAny, signature-gated)

5. **`cs/migrations/0015_cs_conversation_transport_and_stream_id.py`**
   ```python
   class Migration(migrations.Migration):
       dependencies = [('cs', '0014_<previous>')]
       operations = [
           migrations.AddField(
               model_name='conversation',
               name='transport',
               field=models.CharField(
                   choices=[('legacy', 'Legacy (Django/Supabase)'), ('stream', 'GetStream')],
                   default='legacy',
                   max_length=16,
               ),
           ),
           migrations.AddField(
               model_name='message',
               name='stream_id',
               field=models.CharField(blank=True, db_index=True, max_length=64, null=True, unique=True),
           ),
           migrations.AddField(
               model_name='message',
               name='custom_data',
               field=models.JSONField(blank=True, default=dict),
           ),
       ]
   ```

6. **`cs/models.py` — update `Conversation.transport` default**
   - New convs default to `'legacy'` (until Phase 5 cutover flag flips)
   - Document migration path in model docstring

7. **`cs/serializers.py` — add `transport` field**
   - `ConversationSerializer` (`cs/serializers.py:10`): include `transport`
   - `ConversationInboxSerializer` (`cs/serializers.py:17`): include `transport`
   - `MessageSerializer` (`cs/serializers.py:78`): include `stream_id` (nullable) in `Meta.fields` (`:84`)

8. **BE tests** (`cs/tests/test_stream.py`)
   - `test_mint_token_for_authenticated_user` — Bearer token → 200 + JWT decodes
   - `test_mint_token_for_guest` — `X-CS-Guest-Token` header → 200 + JWT decodes with `conversation_id` claim
   - `test_mint_token_for_ota` — `ota_token` body → 200 + JWT decodes
   - `test_mint_token_staff_requires_scope` — `scope='staff'` explicit → 200; missing → 403
   - `test_webhook_hmac_failure` → 401
   - `test_webhook_message_new_creates_message` → row exists
   - `test_webhook_message_new_idempotency` → duplicate `stream_id` → no duplicate row
   - `test_webhook_message_deleted_soft_deletes` → `is_deleted=True`

9. **`.env.sample`**
   ```
   STREAM_API_KEY=
   STREAM_API_SECRET=
   STREAM_WEBHOOK_SECRET=
   ```

10. **`Smartenplus/settings.py`**
    ```python
    # python-decouple config() — match SUPABASE_JWT_SECRET pattern (settings.py:595-598),
    # NOT os.environ.get() (breaks the project's .env-loading convention)
    STREAM_API_KEY = config('STREAM_API_KEY', default='')
    STREAM_API_SECRET = config('STREAM_API_SECRET')
    STREAM_WEBHOOK_SECRET = config('STREAM_WEBHOOK_SECRET')
    ```

11. **Supabase `cs_messages` mirror unchanged**
    - `cs/tasks.py:sync_chat_messages` continues writing to Supabase for OTA sync
    - No edits to existing Supabase Realtime flow

### Verification

- `pytest cs/tests/test_stream.py -v` → all PASS
- curl POC: mint token for 3 auth tiers → JWT decodable
- Local tunnel test: webhook receives + verifies + writes row
- Migration dry-run: `python manage.py migrate cs 0015 --plan` shows expected operations
- `ruff check cs/stream_jwt.py cs/views.py cs/models.py` → clean

---

## Phase 2 — Frontend Stream Hook (2 sprints)

**Goal:** Production-grade FE integration with custom UI preservation.

### Sprint 2A — Foundation

1. **Dependencies**
   - `yarn add stream-chat stream-chat-react` (verify React 18 compat via package version)
   - Verify peer dependencies

2. **`helpers/streamChatClient.js` (new)**
   ```javascript
   import { StreamChat } from 'stream-chat';
   
   const apiKey = process.env.NEXT_PUBLIC_STREAM_API_KEY;
   let accessToken = null;
   
   export const streamClient = StreamChat.getInstance(apiKey, {
     enableInsights: false, // free tier no-op
     enableWSFallback: true,
   });
   
   export function setStreamToken(token) {
     accessToken = token;
     streamClient.setToken(...) // Stream's dev token pattern
   }
   ```
   - Mirror `helpers/supabaseClient.js` pattern (singleton + setter)

3. **`hooks/useGetStreamChat.js` (new)**
   - Connect to Stream channel via `streamClient.channel('messaging', conversationId)`
   - Subscribe to `channel.on('message.new', ...)` → `onMessages`
   - Subscribe to `channel.on('channel.deleted', ...)` → `onConversationClosed`
   - Token refresh: callback `streamClient.tokenProvider = async () => (await mintStreamToken()).token`
   - Reconnect handling: Stream SDK does this server-side; verify gap-fill on local test
   - Mirror API surface of `useChatRealtime`: returns `{ready}` + accepts `{conversationId, token, guestToken, enabled, onMessages, onConversationClosed}`

4. **`components/chat/GetStreamPanel.js` (new)**
   - Wraps `<Chat client={streamClient}><Channel channel={channel}>...</Channel></Chat>`
   - Custom message bubble component (preserve Tailwind styling — DON'T use Stream's `<Message>` default UI)
   - Custom `<MessageInput>` (preserve `canSendImage` logic, attach button → existing S3 presigned flow)
   - Header preserved from `ChatPanel.js`

### Sprint 2B — Integration + image send

5. **Branch in `ChatWidget.js:175-176`** (⚠️ **audit:** current code is a 2-way `USE_REALTIME` boolean split — no `state.transport` field exists. The snippet below is the TARGET after you add `transport` to the conversation API response + a `SET_CONV` reducer action. Do not assume `state.transport` works today.)
   ```javascript
   const transport = state.transport ?? 'legacy';
   const useStream = transport === 'stream';
   const useRealtime = transport === 'stream' || (transport === 'legacy' && USE_REALTIME);
   const usePolling = transport === 'legacy' && !USE_REALTIME;
   
   useChatPolling({ ...transportArgs, enabled: state.status === 'open' && usePolling });
   const { ready: realtimeReady } = useChatRealtime({ ...transportArgs, enabled: state.status === 'open' && transport === 'legacy' });
   const { ready: streamReady } = useGetStreamChat({ ...transportArgs, enabled: state.status === 'open' && useStream });
   ```

6. **Image send path**
   - File selected → upload to `POST /api/cs/messages/send-image/` (Django, preserves S3 private + presigned)
   - Django returns `{image_url, message_id}`
   - Client sends Stream message: `channel.sendMessage({ text: body, attachments: [{ type: 'image', image_url, asset_url: presigned }], custom_data: { sender_type: 'customer', django_message_id } })`
   - Webhook fires → `cs.Message` row created with `stream_id` + `image` field populated
   - **Text-send path (audit correction):** also replace the `else if (USE_REALTIME)` Supabase-direct-insert branch (`ChatPanel.js:68-81`) with a Stream `sendMessage` call for stream-transport convs. AD side: remove `supabase.from('cs_messages').insert` staff-send branch (`ConversationDetail.js:134-148`) — current realtime-mode staff send bypasses Django entirely, so the webhook becomes the only staff-send archive path.

7. **`.env.local` + `.env.sample`**
   ```
   NEXT_PUBLIC_STREAM_API_KEY=
   NEXT_PUBLIC_CHAT_TRANSPORT=stream|legacy
   ```

8. **FE tests** (`__tests__/hooks/useGetStreamChat.test.js`)
   - Connects to channel on mount
   - Echoes new messages via `onMessages` callback
   - Reconnect: simulate WS drop → verify SDK auto-reconnects + gap-fills
   - Token refresh: mock 14-min mark → verify new token fetched + SDK picks up

9. **`helpers/chatImage.js`** — extend `isAllowedChatImageUrl`
   - Allow Stream CDN URL pattern (verify exact shape from GetStream docs in Phase 0)
   - Keep S3 allowlist as is

### Verification

- `yarn jest useGetStreamChat` → all PASS
- Local dev: 2 browser tabs, customer in FE, staff in AD (Phase 3 AD hook not built yet → manual: send message from Stream dashboard directly) → real-time echo works
- Network drop test: `ifconfig down` for 30s → `up` → gap-fill via Stream SDK
- Image send test: JPEG + HEIC → presigned URL valid 7 days
- Token refresh test: simulate 14-min mark → no disconnect

---

## Phase 3 — Admin Staff Hook (1 sprint)

**Goal:** Staff-side Stream integration under the EXISTING MUI inbox (⚠️ **audit B3:** a full staff inbox EXISTS at `pages/cs/index.js` — this phase swaps realtime source + adds Stream presence/typing, NOT "build staff inbox"). Custom UI.

### Tasks

1. **Dependencies**
   - `yarn add stream-chat-react` to AD `package.json`

2. **`helpers/streamChatClient.js` (new, AD-side)**
   - Singleton with `staff` JWT provider
   - Token from `POST /api/cs/stream-token/` with `scope: 'staff'`

3. **`hooks/useStaffGetStreamChat.js` (new)**
   - Connects to Stream channel for staff-side view of conv
   - `client.channel('messaging', conversationId).watch()` → channel state
   - Subscribe to `channel.on('message.new', ...)` → dispatch RTK cache update
   - Send: `channel.sendMessage({ text, custom_data: { sender_type: 'cs' } })`
   - Mirror `useStaffChatRealtime` API surface

4. **`hooks/useStaffInboxRealtime.js` — modify source**
   - Replace Supabase `postgres_changes` subscription with Stream event subscription
   - `streamClient.on('notification.message_new', (event) => { ... })` → dispatch RTK `getConversations` cache patch
   - OS push notification: same as today (existing service worker)
   - **⚠️ AUDIT BLOCKER B2:** `useStaffInboxRealtime` is mounted GLOBALLY in `pages/dashboard/SideList.js:116` (NOT `pages/cs/index.js`) and is load-bearing for closed-conv auto-reopen mirroring + system-message status transitions (reopen/close/ended) + Web Push. Stream `notification.message_new` fires only for customer messages, NOT system status rows. Must EITHER keep a Supabase/Django subscription for SYSTEM messages alongside Stream, OR re-route status transitions through a Stream system channel — else status propagation silently breaks.

5. **`components/cs/StreamConversationDetail.js` (new)**
   - Wraps `<Channel>` with staff-side custom UI
   - **⚠️ audit:** AD CS module is **MUI sx-prop styled, NOT Tailwind** (zero `className=` in `components/cs/`). Reimplement the bubble in MUI (Box sx) — do NOT reuse the FE's Tailwind `GetStreamPanel.js` bubble. Real AD risk: stream-chat-react CSS-in-JS conflicts with MUI `CssBaseline`/theme (not "Tailwind override").
   - Status change / merge / mark-read buttons → still POST to Django endpoints (orthogonal to transport)

6. **`store/api/csApi.js` — add `getStreamToken` mutation**
   ```javascript
   getStreamToken: builder.mutation({
     query: ({ scope }) => ({
       url: '/api/cs/stream-token/',
       method: 'POST',
       body: { scope },
     }),
   }),
   ```

7. **Branch in `pages/cs/index.js`**
   - `conv.transport === 'stream'` → render `<StreamConversationDetail>`
   - `conv.transport === 'legacy'` → render existing `<ConversationDetail>`

8. **AD tests** (`__tests__/hooks/useStaffGetStreamChat.test.js`)
   - Staff login → token fetched → channel subscribed
   - New customer message → `onMessages` fires
   - Staff sends message → appears in customer's FE tab within 1s

### Verification

- `yarn jest useStaffGetStreamChat` → all PASS
- Manual: staff login to `/cs` → new guest opens conv in FE → appears in staff inbox within 5s → staff replies → customer sees instantly
- OS push notification fires on new message (existing service worker unchanged)
- Inbox badge updates from Stream event (not Supabase)

---

## Phase 4 — Image Pipeline Parity (1 sprint)

**Goal:** Image send works end-to-end on Stream with S3 private + presigned.

### Tasks

1. **Stream attachment event → Django webhook handler**
   - In `cs/views.py:StreamWebhookView`, on `message.new` with attachment, write `cs.Message.image` from `event.message.attachments[0].image_url` (Stream CDN URL)
   - Django re-presigns on read (preserves [[chat-image-send-server-convergence]] pattern)

2. **Image render in `GetStreamPanel.js`**
   - Read `msg.custom_data.image_url` (Stream custom field, Django presigned URL)
   - Pass through `isAllowedChatImageUrl` (extend allowlist for presigned S3 URLs)
   - Lazy `<img loading="lazy" />` with S3 presigned fallback

3. **Image send path (already in Phase 2 but verify)**
   - File → `POST /api/cs/messages/send-image/` (Django)
   - Django returns `{image_url, message_id}`
   - Client sends Stream message with `custom_data: { sender_type: 'customer', image_url, django_message_id }`
   - Webhook fires → `cs.Message` row with `image` populated + `stream_id` set

4. **Tests**
   - HEIC upload (use `heic2any` in test fixture)
   - 20MB cap client-side guard
   - Presigned URL 7-day TTL (mock clock in test)
   - Allowlist blocks rogue URL (return 403 from FE if URL not allowed)

### Verification

- Customer sends HEIC image → staff sees image with valid presigned URL
- After 7 days, presigned URL expires → staff sees broken image → re-fetch from Django endpoint (preserves [[chat-image-send-server-convergence]])
- Rogue URL in Stream custom field → blocked by allowlist

---

## Phase 5 — Cutover Flag + Monitoring (0.5 sprint)

**Goal:** Runtime flag to flip Stream on/off; observability for issue triage.

### Tasks

1. **`.env.local`** — set `NEXT_PUBLIC_CHAT_TRANSPORT=stream` (default for new builds)

2. **Transport selector — ⚠️ AUDIT BLOCKER B1 (`FeatureFlag` cannot hold value):**
   `FeatureFlag` (`cs/models.py:128-140`) has only `key/enabled/updated_by/updated_at` — no `value` field; `FeatureFlagView` (`views.py:725`) only accepts `PATCH {enabled}`. Pick ONE before Phase 5 freezes: (a) migration adding `FeatureFlag.value` CharField (nullable, coexist with `enabled`); (b) dedicated `CsTransportConfig` model; or (c) settings/env `NEXT_PUBLIC_CHAT_TRANSPORT` (Phase 2/5 already reference it). Also note: `cs_chat` kill switch is **FE-ONLY** (no backend FeatureFlag).
   - Default: `'legacy'` until Phase 6 validation passes
   - After validation: flip to `'stream'` via the chosen mechanism

3. **`ConversationCreateView` — populate `transport`**
   - New conv: read FeatureFlag → set `Conversation.transport = flag_value`
   - Old convs: stay `'legacy'` (no migration needed — field defaults to legacy)

4. **Logging**
   - Stream events → Sentry with `transport=stream` tag
   - Webhook errors → log to `cs_webhook_errors` table for nightly review
   - Per-conv transport mix → Grafana panel for ops

5. **`cs_chat` FeatureFlag unchanged**
   - Global kill switch (chat off entirely)
   - Independent from `cs_chat_transport`

### Verification

- Flip `cs_chat_transport=legacy` in Django admin → new convs route to Django polling
- Flip `cs_chat_transport=stream` → new convs route to Stream
- Flip `cs_chat=false` → chat widget hidden entirely
- Sentry errors tagged `transport=stream` filterable

---

## Phase 6 — Shadow Parallel-Run + Cutover (4-6 weeks)

**Goal:** Prove stability under production load, then flip default.

### Week 1-2: shadow run

- All NEW convs on Stream
- Old convs read from Django (no change)
- Webhook archive writing to Django daily
- **Daily diff check:** `count(cs.Message where transport=stream AND created_at > 24h)` vs `count(Stream channel history query via REST)` — must match
- Zero tolerance for message loss

### Week 3: load test

- k6 load test: simulate 100 concurrent widgets
- Verify no Stream 429s (within free-tier concurrent limit)
- Verify webhook keeps up (no drop events)
- Verify Django `cs.Message` writes don't slow down (Webhook handler <100ms p99)

### Week 4: enable default for new visitors

- Flip `cs_chat_transport=stream` as default in Django admin
- Monitor for 1 week

### Week 5: full cutover

- All NEW convs on Stream
- Monitor Supabase Realtime error rate (should drop to <0.1% as no chat traffic)
- Monitor Stream dashboard: connections, messages, errors

### Week 6: decommission Supabase Realtime for chat

- Stop subscribing to `cs_messages` for chat realtime (keep table for OTA sync mirror)
- Remove `useChatRealtime` hook from FE (keep `useChatPolling` as 6-month warm fallback)
- Update docs: chat realtime = Stream

### Post-cutover (6-month warm)

- Keep Django polling fallback in code (do NOT delete)
- Keep `useChatPolling` for emergency rollback
- Quarterly tier review: confirm Build free tier still adequate

### Verification

- 30-day stability check:
  - Zero Stream outages affecting customers
  - Zero webhook drops
  - <0.1% message loss
  - MAU under 100 (well within 1k cap)
  - Webhook p99 latency <100ms
- Mark cutover complete in vault
- Create `04-decisions/cs-chat-getstream-cutover-complete-2026-XX-XX.md` (date TBD)

---

## Send Path Detail (Sender-Integrity Preserved)

Per [[chat-sender-session-bleed]] pattern:

| Actor | Client action | Server verification | `cs.Message.sender` |
|---|---|---|---|
| Customer (BE) | `channel.sendMessage({ custom_data: { sender_type: 'customer' } })` | Webhook reads `event.user.role === 'customer'` | `'customer'` |
| Staff (AD) | `channel.sendMessage({ custom_data: { sender_type: 'cs' } })` | Webhook reads `event.user.role === 'staff'` | `'cs'` |
| System (Django) | Server-side `client.chat.channel(c).sendMessage({ user_id: 'system', text: '...' })` | Direct from BE; no client involvment | `'system'` |

**Spoof protection:**
- Stream server-side auth: customers get JWT scoped to their own `user_id`
- Webhook handler reads `event.user.role` from signed JWT payload — client can't fake this
- Custom `sender_type` field is convenience for FE display, NOT source of truth

---

## Out of Scope (Explicit)

- Backfill old conversations into GetStream (hybrid = Django reads old, Stream owns new)
- Staff inbox UI rebuild (uses Stream's `<ChannelList>` = batteries-included)
- PDPA cross-border consent flow (BLOCKING gate from [[cs-consent-gdpr-model]] — must clear before Phase 0 commits)
- GetStream Enterprise / paid tier (free Build sufficient for current volume)
- Migration of Supabase OTA mirror (stays on Supabase)
- Presence / typing / read-receipts UI changes (Stream provides; UI not changed — Phase 7+)

---

## Risk Matrix

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Build tier MAU cap (1k) hit unexpectedly | Medium | Medium | Build is HARD-CAPPED (rate-limits/errors, no paid overage); CloudWatch alarm on Stream quota; quarterly tier review; upgrade to Start ($499/mo) only path past cap |
| Webhook drops / ordering issues | Low | High | Idempotency on `stream_id`; nightly reconcile task |
| PDPA data region = US/EU (not APAC) | High | Critical | BLOCKING gate before Phase 1 commit; escalate to paid tier if no APAC on Build |
| Sender-spoof bypasses ownership gate | Low | High | Stream server-side auth + role-based perms; webhook trusts `event.user.role` only |
| Free tier auto-bump to paid | Low | High | NO Stripe on signup; quarterly tier review calendar reminder |
| Django `Message` schema divergence (Stream custom fields vs Django fields) | Medium | Medium | `Message.stream_id` = canonical join; `custom_data` JSON field for flexibility |
| React 18 incompatibility with `stream-chat-react` | RESOLVED | — | `stream-chat-react` 14.8.0 peer-deps include `^18.0.0`; pin `stream-chat ^9.49.0` |
| Tailwind styling override conflict (FE only) | Medium | Low | Custom `<MessageInput>` + custom message bubble (no Stream default UI) |
| **AD MUI/CSS-in-JS conflict** (audit new) | Medium | Medium | AD uses MUI sx (NOT Tailwind); stream-chat-react CSS-in-JS may clash with MUI `CssBaseline`/theme — verify in Phase 3 |
| **getstream Python SDK requires ≥3.10; prod = 3.9** (audit new) | Medium | High | Phase 0: install on `python:3.9-alpine`; if fails, Python bump + Dockerfile (undocumented effort) |
| **AD system-message status-transition path lost** (audit B2) | High | High | Keep Supabase/Django sub for SYSTEM msgs OR Stream system channel; preserve `SideList.js:116` mount + all-status RTK patch |

---

## Estimated Effort Summary

| Phase | Sprints | Engineer |
|---|---|---|
| 0 — Spike + tier qualification | 1 | 1 BE + 1 FE |
| 1 — Backend token + webhook | 1 | 1 BE |
| 2 — Frontend Stream hook | 2 | 1 FE |
| 3 — Admin staff hook | 1 | 1 FE (AD) |
| 4 — Image pipeline parity | 1 | 1 BE + 1 FE |
| 5 — Cutover flag + monitoring | 0.5 | 1 BE + 0.5 ops |
| 6 — Shadow parallel-run + cutover | 4-6 weeks | 0.5 ops monitor |

**Total: ~6.5 sprints + 4-6 weeks shadow** ≈ 3 months calendar

---

## Audit Checklist (for other team)

Before approving implementation:

- [ ] Tier qualification result reviewed (Build = $0 confirmed?)
- [ ] PDPA gate result reviewed (APAC region available? DPA obtainable?)
- [ ] Hybrid scope accepted (no backfill of old convs)
- [ ] Branch strategy accepted (`feat/be-*`, `feat/fe-*`, `feat/ad-*`)
- [ ] Sender-integrity pattern reviewed (Stream server-side auth + webhook trust)
- [ ] Image pipeline approach accepted (Django S3 presigned + Stream custom_data field)
- [ ] Cutover flag pattern accepted (FeatureFlag `cs_chat_transport`)
- [ ] Rollback plan accepted (flip flag → legacy, no data loss)
- [ ] Effort estimate accepted (~6.5 sprints + 4-6 weeks shadow)
- [ ] Risk matrix reviewed and mitigations accepted