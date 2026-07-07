# Chat 409 Handoff — 2026-07-07 (#222)

> **RESOLVED 2026-07-07 (#223).** H5 was wrong — the upsert never ran at all. Real RC: test account `junedarkside@gmail.com` is `is_staff/is_admin/is_superuser`, so `SupabaseTokenView`'s STAFF tier matched first and returned a conversation-less staff JWT **without calling `upsert_cs_conversation`** — conv 3 never mirrored to Supabase → FK 23503 on every send. Explains all anomalies: no log line (call site never reached), guest conv 4 landed (guest tier does upsert), staff JWT passed RLS. Fix: staff tier now requires explicit `scope='staff'` (BE `5071926`); admin-dashboard hooks send it (`4a766af`); FE debug logs reverted (`91485ac6`). All merged → develop. Verified live: `upsert_cs_conversation id=3 status=201`, row landed, customer-tier claims correct, staff-scope tier intact. Real (non-staff) customers were never affected. Duplicate open conv 5 closed in Django.
Customer login → POST `/rest/v1/cs_messages` → HTTP 409 → `code:'23503', details:'Key (conversation_id)=(3) is not present in table "cs_conversations".'`. RC pinned: BE `upsert_cs_conversation` is silently no-op'ing on Supabase project `npehhtcobshckhefrqhw`. **Not yet fixed** — log line never observed in BE stdout despite patches. Resume point = obtain real Supabase response for the upsert call, then either JWT-claim fix or pivot to INSERT-not-UPSERT.

## Symptom
- Authenticated user `junedarkside@gmail.com` opens realtime chat (`NEXT_PUBLIC_CHAT_REALTIME=true`).
- POST `https://npehhtcobshckhefrqhw.supabase.co/rest/v1/cs_messages` returns 409 Conflict via supabase-js stack `eval @ index.mjs:351 → executeWithRetry @ index.mjs:306`.
- FE error log after try/catch wrap:
  ```
  code: '23503',
  message: 'insert or update on table "cs_messages" violates foreign key constraint "cs_messages_conversation_id_fkey"',
  details: 'Key is not present in table "cs_conversations".',
  ```

## Evidence Trail (SQL / Trace)

| Run | Query / Trace | Result | Ruled |
|---|---|---|---|
| 1 | SQL: `seq_last vs MAX(id)` on `cs_messages_id_seq` | `max_id=59, seq_last=60, is_called=true` → seq healthy | H1 (PK drift) **out** |
| 2 | SQL: `pg_constraint` on `cs_messages` | only PK + FK on conv_id + sender CHECK | H3 (extra UNIQUE) **out** |
| 3 | SQL: collation/version + UNIQUE-text-index | `datcollversion=153.120`; no rows | H4 (text-UNIQUE col drift) **out** |
| 4 | FE grep: `supabase.from('cs_messages').insert(` | exactly 1 hit at `components/chat/ChatPanel.js:42` | single writer confirmed |
| 5 | FE: handleSend instrumentation round 1 | `console.log('[CHAT-SEND] payload', ...)` did not fire | suspect: `await supabase.auth.getSession()` throws `AuthSessionMissingError` |
| 6 | FE: try/catch wrapper around getSession | captured full error object — confirmed 23503 with conv_id=3 | real path pinned |
| 7 | SQL P1: `SELECT * FROM public.cs_conversations WHERE id = 3` | **0 rows** | FK target missing |
| 8 | SQL P2: `SELECT count(*), max(id)` | `1 row, max_id=4` | only 1 conv in Supabase |
| 9 | SQL P3: recent 5 rows | row id=4 = guest / `june_pinkfloyd@hotmail.com` / user_id=null / status=open | only conv is guest, not the logged-in customer |

## Hypotheses Tested

### H1 — PK sequence drift on `cs_messages`
- **Status:** REFUTED by Run 1.
- Evidence: sequence advanced past `MAX(id)`.

### H2 — Stale FE `conversationId` in reducer after guest→user transition
- **Status:** PARTIAL. Run 6 shows `conversationId=3` is what the FE believes is active. The 3 was returned by BE `ConversationCreateView`. So H2 is "symptom amplifies" — but the upstream cause is BE using an id that does not exist in Supabase.
- Evidence: BE returns id, FE sets reducer, FE posts.

### H3 — Extra UNIQUE constraint drift
- **Status:** REFUTED by Run 2.

### H4 — Collation drift → false 23505
- **Status:** REFUTED by Run 3 (no text-index). `datcollversion=153.120` mismatch IS real on `postgres` DB and should be `ALTER COLLATION "default" REFRESH VERSION + REINDEX` as ops hygiene, but NOT the 409 cause.

### H5 — BE upsert silently no-ops → token mints against missing row
- **Status:** **PRIMARY SUSPECT. UNVERIFIED.**
- Mechanism inferred: `cs/supabase_client.py:114-138` `upsert_cs_conversation` POSTs to `/rest/v1/cs_conversations` with `Prefer: resolution=merge-duplicates` but no `?on_conflict` and no `return=representation`. On this project's PostgREST version, the merge-default-with-no-target may silently no-op; alternatively the BE `try/except RuntimeError` swallows non-`RequestException` 4xx; either way, row id=3 never lands and `SupabaseTokenView.post` returns 200 with a JWT carrying `conversation_id=3`.

## What Was Attempted

### Commit `70c9103` — `fix/chat-conv-upsert-conflict`
File: `smartenplus-backend/cs/supabase_client.py:114-141`
- URL: `?on_conflict=id`
- Header: `Prefer: resolution=merge-duplicates,return=representation`
- Added `logger.info(...)` after `raise_for_status()` to capture status + body.
- Already had `logger.warning(...)` inside except (with response info).

### Commit `c6a12e3` — `fix/chat-conv-upsert-conflict`
File: `smartenplus-backend/Smartenplus/settings.py:536`
- Added `'cs': {'handlers': ['console'], 'level': 'INFO', 'propagate': False}` to `LOGGING['loggers']`. Without this, `cs.supabase_client` logger inherits root `WARNING` → INFO calls dropped silently.

### Commits `da69cef1`, `94fb2552`, `bc80be88` — `debug/chat-409-console-log`
File: `smartenplus-frontend/components/chat/ChatPanel.js`
- Module-load log to confirm fresh chunk.
- `handleSend entered` log before early-return.
- try/catch around `supabase.auth.getSession()` (was throwing AuthSessionMissingError).
- Prop-token capture (`token`/`guestToken`/realtimeReady).
- Captured error object's `status`/`code`/`message`/`details`/`hint` — produced the 23503 evidence.

### Diagnostic queries
A–D to refute H1/H3/H4. P1/P2/P3 to confirm Supabase state.

## What's Left

1. **Bounce** BE (`python manage.py runserver` exit + restart) — confirm c6a12e3 is loaded.
2. **Re-run** customer send → grep BE stdout for `upsert_cs_conversation id=3 status=...`.
3. **If log line appears**: paste back. Decides next move:
   - `status=201 + body=[{...id:3...}]` → row landed. Decode JWT at jwt.io — read `conversation_id` claim. If mismatch → RLS check uses wrong id.
   - `status=200 + body=[]` → PostgREST didn't insert. Pivot to plain INSERT (drop `resolution=merge-duplicates`).
   - `status=4xx + body=<...>` → paste body verbatim. Most likely RLS or payload shape.
4. **If log line STILL missing after bounce**: switch `logger.info` to `print(...)` in `upsert_cs_conversation` — bypasses Django LOGGING entirely. Single line edit; commit on same branch.

## Files In Flight

### BE branch `fix/chat-conv-upsert-conflict`
- `smartenplus-backend/cs/supabase_client.py` (commit `70c9103`)
- `smartenplus-backend/Smartenplus/settings.py` (commit `c6a12e3`)

### FE branch `debug/chat-409-console-log`
- `smartenplus-frontend/components/chat/ChatPanel.js` (commits `da69cef1`, `94fb2552`, `bc80be88`)
- After RC fix verified, revert all 4 `[DEBUG-409]` log blocks → commit on same branch → merge both branches to develop per CLAUDE.md git policy.

### Vault
- `master-state.md` Section 1 (this session) + Section 2 (new CHAT-409-DIAGNOSIS row).
- `01-projects/chat-409-diagnosis-handoff-2026-07-07.md` — this file.
- `07-logs/log.md` — session-end line.

## Next Session Acceptance Criteria

- [ ] BE bounced; c6a12e3 served.
- [ ] `upsert_cs_conversation id=3 status=... body=...` observed in stdout (or `print(...)` substituted if not).
- [ ] One of the three forks above resolved.
- [ ] Customer send → no `409` in Network tab, no `[CHAT-SEND] error` group, no FK 23503 in BE log.
- [ ] 5+ consecutive sends land for one customer.
- [ ] FE debug logs reverted and merged.
- [ ] BE fix verified and merged.
- [ ] Master-state Section 2 row moved to `07-logs/closed-items.md`.
