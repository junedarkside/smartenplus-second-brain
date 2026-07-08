---
name: supabase-config-single-source-of-truth
description: ADR — BE .env as single source of truth for Supabase URL + anon key. FE + AD init supabaseClient lazily via GET /api/cs/config/ instead of NEXT_PUBLIC_* build-time vars.
metadata:
  type: decision
  status: accepted
  date: 2026-07-08
  parent: cs-chat-supabase-offload
---

# Supabase Config — Single Source of Truth (BE `.env`)

## Summary

All 3 repos shared one Supabase project but duplicated `SUPABASE_URL` and `SUPABASE_ANON_KEY` in each `.env`. Decision: BE `.env` is canonical. FE + AD fetch these values at runtime via `GET /api/cs/config/` (AllowAny) and init `createClient` lazily. Secrets never leave BE.

## Context

Scan date: 2026-07-08. Same Supabase project (`npehhtcobshckhefrqhw.supabase.co`) across:
- `smartenplus-frontend` — `NEXT_PUBLIC_SUPABASE_URL` + `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `smartenplus-backend` — `SUPABASE_URL` + `SUPABASE_ANON_KEY` + `SUPABASE_JWT_SECRET` + `SUPABASE_SERVICE_ROLE_KEY`
- `admin-dashboard` — `NEXT_PUBLIC_SUPABASE_URL` + `NEXT_PUBLIC_SUPABASE_ANON_KEY`

Rotation risk: changing the key in one repo without the others causes realtime to break on 2 out of 3 surfaces.

## Architecture — Current (pre-change)

```
BE .env                     FE .env.local              AD .env.local
SUPABASE_URL ──────────┐   NEXT_PUBLIC_SUPABASE_URL   NEXT_PUBLIC_SUPABASE_URL
SUPABASE_ANON_KEY ─────┤   NEXT_PUBLIC_SUPABASE_ANON  NEXT_PUBLIC_SUPABASE_ANON
SUPABASE_JWT_SECRET    │   (duplicated, drift risk)   (duplicated, drift risk)
SUPABASE_SERVICE_ROLE  │
                       │
              All 3 same value, no sync mechanism
```

## Architecture — Post-change

```
BE .env  (canonical)
├── SUPABASE_URL              ──→  GET /api/cs/config/ (AllowAny, public)
├── SUPABASE_ANON_KEY         ──→  GET /api/cs/config/ (AllowAny, public)
├── SUPABASE_JWT_SECRET            ← BE only, never served
└── SUPABASE_SERVICE_ROLE_KEY      ← BE only, never served

FE / AD
└── helpers/supabaseClient.js
    └── getSupabase() — lazy fetch /api/cs/config/ → createClient once
```

## Decision

**Chosen mechanism:** runtime `/api/cs/config/` fetch. FE + AD remove `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` from `.env`. `supabaseClient.js` initializes lazily on first `getSupabase()` call.

**Why anon key is safe to serve publicly:** Supabase anon key is public by design — it is embedded in every Supabase client-side SDK invocation and visible in browser network tabs. RLS policies enforce access, not key secrecy. The settings.py comment "NEVER expose SUPABASE_ANON_KEY to client" referred to original OTA-sync context (server-only reads); that restriction does not apply to the chat path which already runs client-side Realtime.

## Tradeoffs Debated

| Approach | Verdict | Reason |
|---|---|---|
| Runtime `/api/cs/config/` | **Chosen** | User preference; single source without secrets manager cost |
| CI/CD secrets manager (Doppler) | Best practice, not chosen | Correct solution but adds paid tooling + pipeline changes |
| Copy-on-rotate convention | Simplest, not chosen | Still manual; drift risk remains |

**Known tradeoffs of chosen approach:**
- 1 extra network round-trip before chat init (negligible — chat inits only when widget opens or staff page loads)
- Boot dependency on BE: if BE is down, chat is already broken (supabase-token mint also fails — no new failure mode)
- Fights Next.js build-time env model — `process.env.NEXT_PUBLIC_*` vars removed; module-level `createClient` replaced with async lazy init

## Implementation Plan (to execute per repo)

### BE — `smartenplus-backend`

**`cs/views.py`** — add `PublicConfigView`:
```python
class PublicConfigView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'supabase_url': settings.SUPABASE_URL,
            'supabase_anon_key': settings.SUPABASE_ANON_KEY,
        })
```

**`cs/urls.py`** — add:
```python
path('config/', PublicConfigView.as_view(), name='public-config'),
```

**`Smartenplus/settings.py` line 596** — update comment:
```python
# Supabase — URL + anon key served via GET /api/cs/config/ (AllowAny; anon key is public by design).
# JWT secret + service role key are BE-only — never serve these.
```

### FE — `smartenplus-frontend`

**`helpers/supabaseClient.js`** — lazy init:
```javascript
import { createClient } from '@supabase/supabase-js';
const BASE_URL = (process.env.NEXT_PUBLIC_API_URL || '').trim();
let client = null;
let accessToken = null;

async function initClient() {
  if (client) return client;
  const cfg = await fetch(`${BASE_URL}/api/cs/config/`).then(r => r.json());
  client = createClient(cfg.supabase_url, cfg.supabase_anon_key, {
    accessToken: async () => accessToken,
    db: { schema: 'public' },
  });
  return client;
}
export async function getSupabase() { return initClient(); }
export function setSupabaseToken(token) {
  accessToken = token;
  if (client) client.realtime.setAuth(token);
}
```

**Call sites** (2 files):
- `hooks/useChatRealtime.js` — `supabase.` → `(await getSupabase()).`
- `components/chat/ChatPanel.js` — `supabase.from(...)` → `(await getSupabase()).from(...)`

**`.env.local`** — remove `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`. Keep `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_CHAT_REALTIME`.

### AD — `admin-dashboard`

**`helpers/supabaseClient.js`** — same lazy pattern (without `db: { schema: 'public' }`).

**Call sites** (3 files):
- `components/cs/ConversationDetail.js` — `supabase.from(...)` → `(await getSupabase()).from(...)`
- `hooks/useStaffChatRealtime.js` — remove module-level `SUPABASE_URL`/`SUPABASE_ANON_KEY` reads; fetch config before isolated `createClient` call
- `hooks/useStaffInboxRealtime.js` — same as above

**`.env.local`** — remove `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`. Keep `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_CHAT_REALTIME`.

## Verification

1. `curl http://localhost:8000/api/cs/config/` → `{"supabase_url": "...", "supabase_anon_key": "..."}`
2. Remove `NEXT_PUBLIC_SUPABASE_URL` from FE `.env.local` → restart → open chat → network tab shows `/api/cs/config/` call → chat connects and receives messages
3. Same for AD: CS inbox realtime subscribes without error
4. Confirm `SERVICE_ROLE_KEY` and `JWT_SECRET` NOT in `/api/cs/config/` response

## What Stays Secret (never served)

| Var | Location | Served? |
|---|---|---|
| `SUPABASE_URL` | BE `.env` | Yes — via `/api/cs/config/` (safe) |
| `SUPABASE_ANON_KEY` | BE `.env` | Yes — via `/api/cs/config/` (safe by design) |
| `SUPABASE_JWT_SECRET` | BE `.env` only | **No** |
| `SUPABASE_SERVICE_ROLE_KEY` | BE `.env` only | **No** |

## Related

- [[cs-chat-supabase-offload]] — full Supabase chat offload ADR (prepared path); this doc is a sub-decision
- [[supabase-jwt-secret-location]] — where to find the correct JWT signing secret
- [[feature-flag-kill-switch-pattern]] — `NEXT_PUBLIC_CHAT_REALTIME` still controls realtime vs polling
