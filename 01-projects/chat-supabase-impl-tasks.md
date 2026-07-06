---
name: chat-supabase-impl-tasks
description: Granular task breakdown for the chat → Supabase Realtime migration with per-task model assignment (Haiku/Sonnet/Opus) to minimize execution cost. Gated on cs-chat-supabase-offload ADR flipping to accepted.
metadata:
  type: project
  status: active
  date: 2026-07-05
  updated: 2026-07-07
  parent: chat-supabase-migration-plan
---

# Chat → Supabase — Implementation Tasks + Model-Cost Map

> **Gated:** build only after [[cs-chat-supabase-offload]] flips to `accepted` (trigger in [[cs-architecture-decision]]: >~30 req/s sustained widget polling, or committed staff-inbox build). Source design: [[chat-supabase-migration-plan]].

## Model-cost rules (read before every phase)

1. **Default executor = Sonnet.** Escalate to **Opus/Fable ONLY** for the 3 marked tasks (2 security reviews + 1 cutover go/no-go). Drop to **Haiku** for mechanical/config/runbook tasks.
2. **One phase = one session.** Start each session with: this note + [[chat-supabase-migration-plan]] + the exact file paths in the task row. **Never let the agent re-scan the codebase** — Explore spawn ≈ 739k tokens (project CLAUDE.md routing table).
3. Review tasks (1.4, 2.4, 6.2) read **diffs only**, not repos.
4. Branch per phase off `develop` (`feat/chat-supabase-p<N>`), merge develop only. Never main.
5. If a task balloons past its size est ×2 → stop, log blocker in this note, don't improvise scope.

## Task table

Sizes: S ≈ <100 LOC or config · M ≈ 100-300 LOC · R = review/runbook, no code.

### P1 — Supabase schema + RLS (SQL; reference `smartenplus-backend/cs/models.py`) ✅ DONE 2026-07-07
| ID | Task | Model | Size | Done when |
|---|---|---|---|---|
| 1.1 ✅ | SQL: `cs_conversations` + `cs_messages` tables mirroring `cs/models.py` fields, index `(conversation_id, created_at)` | Haiku | S | Tables live in Supabase, columns match models |
| 1.2 ✅ | Enable Realtime on `cs_messages` (INSERT) | Haiku | S | `postgres_changes` INSERT event fires on test row |
| 1.3 ✅ | RLS policies: conversation-scoped customer/guest SELECT+INSERT, `app_role: staff` full, sender-column enforcement (customer can't insert `sender='cs'` — preserve [[chat-sender-session-bleed]]) | Sonnet | M | Policies applied, positive-path works with minted JWT |
| 1.4 ✅ | **Security review:** PostgREST negative tests — anon key alone = 0 rows; conv-A JWT can't read conv B; sender spoof denied; staff JWT full access | **Opus** | R | Verified live via curl — JWT-scoped, RLS enforced |
| 1.5 ✅ | Verify free-tier Realtime limits — same-project decision | Sonnet | R | Same project (npehhtcobshckhefrqhw), works |

### P2 — Django Supabase-JWT mint (backend: `cs/views.py`, `cs/urls.py`, `Smartenplus/settings.py`) ✅ DONE 2026-07-07
| ID | Task | Model | Size | Done when |
|---|---|---|---|---|
| 2.1 ✅ | `SUPABASE_JWT_SECRET` env wiring | Haiku | S | Set in `.env`; ENV.md row added |
| 2.2 ✅ | `POST /api/cs/supabase-token/`: 3 auth tiers (SimpleJWT / guest token / staff). HS256, 24h TTL | Sonnet | M | All 3 tiers return valid Supabase-accepted JWT |
| 2.3 ✅ | Endpoint tests: 3 auth tiers, TTL bound, claim shape, wrong-token 403 | Sonnet | S | Tests pass in `cs/tests/` |
| 2.4 ✅ | **Security review** of claims/TTL/secret handling | **Opus** | R | Signed off |

### P3 — Customer widget swap (smartenplus-frontend: `components/chat/`, `hooks/`) ✅ DONE 2026-07-07
| ID | Task | Model | Size | Done when |
|---|---|---|---|---|
| 3.1 ✅ | `@supabase/supabase-js` install, `helpers/supabaseClient.js` singleton with `accessToken` callback (NOT `auth.setSession` — GoTrue rejects Django JWTs) | Haiku | S | Build passes |
| 3.2 ✅ | `hooks/useChatRealtime.js`: mint JWT → `setSupabaseToken()` → history select → subscribe INSERT → returns `{ready}` | Sonnet | M | Hook live, `ready` gates Send button |
| 3.3 ✅ | `ChatWidget.js` wired; `ChatPanel.js` inserts via `supabase.from('cs_messages').insert()` when `USE_REALTIME=true`; polling path untouched | Sonnet | S | Flag flips transport; widget state-machine unchanged |
| 3.4 ✅ | Two-browser smoke test passed — FE↔admin both send/receive <1s | Sonnet | R | ✅ confirmed by user |

### P4 — Staff inbox (admin-dashboard) ✅ DONE 2026-07-07
| ID | Task | Model | Size | Done when |
|---|---|---|---|---|
| 4.1 ✅ | `ConversationDetail.js`: staff inserts via `supabase.from('cs_messages').insert()` when `USE_REALTIME=true` | Sonnet | M | Staff send works |
| 4.2 ✅ | `useStaffChatRealtime.js`: staff JWT mint → subscribe per-conv INSERT | Sonnet | M | Customer msg appears <1s in admin |
| 4.3 ✅ | `useStaffInboxRealtime.js`: all-convs subscribe → debounced `refetch()`; `cs/index.js` polling disabled when realtime on | Sonnet | S | No 5s polling spam; inbox auto-refreshes |

### P5 — Batch archive sync (backend; clone `cs/tasks.py::sync_ota_bookings` PostgREST pattern) ✅ DONE 2026-07-06
| ID | Task | Model | Size | Done when |
|---|---|---|---|---|
| 5.1 ✅ | Celery task: pull `cs_messages WHERE id > cursor` via PostgREST, bulk insert `cs_message`, advance cursor | Sonnet | M | Messages appear in Django after run |
| 5.2 ✅ | Cursor storage + idempotency test (run twice → identical count) | Sonnet | S | 4 tests pass |
| 5.3 ✅ | Django admin action "Sync chat now" (fires 5.1) | Haiku | S | Button works in admin |
| 5.4 ✅ | Beat registration runbook — prod DB `PeriodicTask` (DatabaseScheduler, per [[prod-capacity-celery-audit]] — NOT celery.py) | Haiku | R | Runbook below |
| 5.5 DEFERRED | PDPA erasure: extend deletion flow to Supabase rows ([[cs-consent-gdpr-model]]) | Sonnet | S | DataErasureRequest model not built |

### P6 — Backfill + cutover
| ID | Task | Model | Size | Done when |
|---|---|---|---|---|
| 6.1 | Management command: existing `cs_message` → Supabase, idempotent upsert by original id | Sonnet | S | Counts match both sides, re-run safe |
| 6.2 | **Cutover go/no-go:** review P1-P5 evidence, soak plan (staff-tested conv → % → all), rollback rehearsal confirmation | **Opus** | R | Written go/no-go in this note |
| 6.3 | E2E verification run — checklist from [[chat-supabase-migration-plan]] §Verification | Sonnet | R | All items ✅ |

### P7 — Rollback readiness
| ID | Task | Model | Size | Done when |
|---|---|---|---|---|
| 7.1 | Rollback runbook (flag flip → polling; one sync run to drain Supabase-only msgs) + live flag-flip test | Haiku | R | Rehearsed once on staging/dev |

## Cost summary

~23 tasks: **6 Haiku · 14 Sonnet · 3 Opus.** Opus confined to security (1.4, 2.4) + cutover (6.2), all diff/evidence-only reads. Sequencing: P1→P2 strict; P3 and P4 parallel after P2; P5 parallel with P3/P4; P6 last; P7 anytime after P3.

## Blockers / decisions log

### Critical gotchas learned during P1-P5 (2026-07-07)

**SUPABASE_JWT_SECRET — use Legacy JWT Secret, not the new secret key**
- Supabase dashboard shows `sb_secret_...` on API Keys page → this is the new Supabase secret key, NOT the JWT signing secret
- PostgREST uses the **Legacy JWT Secret** (HS256 shared secret) to verify tokens
- Location: Dashboard → Settings → **JWT Keys** → **Legacy JWT Secret** tab → **Reveal**
- The value is a long base64 string (not UUID, not `sb_secret_` prefix)
- Set in backend `.env` as `SUPABASE_JWT_SECRET=<revealed-value>`
- Verify signing: `hmac.new(secret.encode(), header_payload, hashlib.sha256)` must match anon/service_role key signatures

**supabase-js v2 auth pattern for Django JWTs**
- `supabase.auth.setSession()` = WRONG — GoTrue validates against `auth.users`; Django users have no entry there → 401 always
- Correct pattern: `createClient(url, anonKey, { accessToken: async () => accessToken })` + `supabase.realtime.setAuth(token)` via `setSupabaseToken()` export in `helpers/supabaseClient.js`

**PostgREST schema routing**
- Project exposes `gmail12go` + `gmailklook` + `public` schemas
- PostgREST defaults to first configured schema (not `public`)
- Service-role headers MUST include `Accept-Profile: public` + `Content-Profile: public`
- `supabase-js` client sends these automatically for public schema; server-side `requests.post()` must set them manually

**Sequence permission for INSERT**
- `authenticated` role needs BOTH: `GRANT USAGE, SELECT ON SEQUENCE public.cs_messages_id_seq` + `GRANT INSERT ON TABLE public.cs_messages`
- Run in Supabase SQL Editor after creating the table

**Celery beat — production registration (manual step, NOT in code)**
- Project uses `DatabaseScheduler` → tasks registered via Django admin, not `celery.py`
- Must do in BOTH dev (`http://localhost:8000/admin/`) AND prod Django admin:
  - **Django admin → Periodic Tasks → Add →**
  - Name: `Sync chat messages from Supabase`
  - Task: `cs.tasks.sync_chat_messages`
  - Interval: every **15 minutes**
  - Enabled: ✓
- Without this: messages live in Supabase but never archive to Django DB; reports/history/admin ticket views won't see them

**upsert_cs_conversation() — required before first message**
- `cs_messages.conversation_id` FK references `cs_conversations(id)` in Supabase
- Django creates conv locally; Supabase has no row until explicitly upserted
- `SupabaseTokenView` calls `upsert_cs_conversation(conv)` before minting JWT — this populates Supabase conv row first
- Failure is non-fatal (logs, continues to mint) to avoid blocking chat

### P6 pre-deploy checklist (2026-07-06)
- [ ] Add 3 GitHub Secrets to `smartenplus-frontend` repo (Settings → Secrets → Actions):
  - `NEXT_PUBLIC_SUPABASE_URL` = `https://npehhtcobshckhefrqhw.supabase.co`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = anon key (eyJ... value)
  - `NEXT_PUBLIC_CHAT_REALTIME` = `true` (only when Supabase fully tested)
- [ ] Add 3 lines to `smartenplus-frontend/.github/workflows/deploy.yml` after line 132:
  ```yaml
            NEXT_PUBLIC_SUPABASE_URL=${{ secrets.NEXT_PUBLIC_SUPABASE_URL }}
            NEXT_PUBLIC_SUPABASE_ANON_KEY=${{ secrets.NEXT_PUBLIC_SUPABASE_ANON_KEY }}
            NEXT_PUBLIC_CHAT_REALTIME=${{ secrets.NEXT_PUBLIC_CHAT_REALTIME }}
  ```
- [ ] Same for admin-dashboard deploy workflow (check if exists)
- [ ] Supabase `public` schema exposed in PostgREST (owner must do — Settings → Data API → Settings → Exposed schemas)

## Related
[[chat-supabase-migration-plan]] · [[cs-chat-supabase-offload]] · [[cs-architecture-decision]] · [[prod-capacity-celery-audit]] · [[ota-p2-impl-plan]]
