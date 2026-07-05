---
name: chat-supabase-impl-tasks
description: Granular task breakdown for the chat → Supabase Realtime migration with per-task model assignment (Haiku/Sonnet/Opus) to minimize execution cost. Gated on cs-chat-supabase-offload ADR flipping to accepted.
metadata:
  type: project
  status: draft
  date: 2026-07-05
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

### P1 — Supabase schema + RLS (SQL; reference `smartenplus-backend/cs/models.py`)
| ID | Task | Model | Size | Done when |
|---|---|---|---|---|
| 1.1 | SQL: `cs_conversations` + `cs_messages` tables mirroring `cs/models.py` fields, index `(conversation_id, created_at)` | Haiku | S | Tables live in Supabase, columns match models |
| 1.2 | Enable Realtime on `cs_messages` (INSERT) | Haiku | S | `postgres_changes` INSERT event fires on test row |
| 1.3 | RLS policies: conversation-scoped customer/guest SELECT+INSERT, `app_role: staff` full, sender-column enforcement (customer can't insert `sender='cs'` — preserve [[chat-sender-session-bleed]]) | Sonnet | M | Policies applied, positive-path works with minted JWT |
| 1.4 | **Security review:** PostgREST negative tests — anon key alone = 0 rows; conv-A JWT can't read conv B; sender spoof denied; staff JWT full access | **Opus** | R | All negative tests fail closed, findings logged here |
| 1.5 | Verify free-tier Realtime limits (concurrent conns, msgs/mo) on OTA-store project → same-vs-dedicated project decision | Sonnet | R | Decision line added to [[cs-chat-supabase-offload]] |

### P2 — Django Supabase-JWT mint (backend: `cs/views.py`, `cs/urls.py`, `Smartenplus/settings.py`)
| ID | Task | Model | Size | Done when |
|---|---|---|---|---|
| 2.1 | `SUPABASE_JWT_SECRET` env wiring, **no default** (rule from [[ota-p2-impl-plan]]) | Haiku | S | Boot fails loud without env; ENV.md row added |
| 2.2 | `POST /api/cs/supabase-token/`: SimpleJWT bearer → user claims; `X-CS-Guest-Token` → `guest:<conv_id>` claims; `IsAdminOrIsStaff` → `app_role: staff`. HS256, ≤24h TTL, claims per ADR sketch | Sonnet | M | All 3 tiers return valid Supabase-accepted JWT |
| 2.3 | Endpoint tests: 3 auth tiers, TTL bound, claim shape, wrong-token 403 | Sonnet | S | Tests pass in `cs/tests/` |
| 2.4 | **Security review** of claims/TTL/secret handling — diff only | **Opus** | R | Sign-off or fixes logged |

### P3 — Customer widget swap (smartenplus-frontend: `components/chat/`, `hooks/`)
| ID | Task | Model | Size | Done when |
|---|---|---|---|---|
| 3.1 | `@supabase/supabase-js` install, client singleton (`helpers/supabaseClient.js`), `NEXT_PUBLIC_SUPABASE_URL`/`ANON_KEY` env | Haiku | S | Client imports clean, build passes |
| 3.2 | `hooks/useChatRealtime.js`: history select → subscribe INSERT filtered by conv → send insert. Mirror `useChatPolling` return shape so `ChatWidget` diff stays minimal | Sonnet | M | Hook drop-in matches polling hook contract |
| 3.3 | Wire into `ChatWidget.js` behind `cs_chat` flag variant (transport picker); `useChatPolling.js` untouched = rollback path | Sonnet | S | Flag flips transport live, no widget state-machine change |
| 3.4 | Two-transport smoke: send/receive on both paths, hidden-tab, reconnect | Sonnet | R | Checklist in PR description all ✅ |

### P4 — Staff inbox (admin-dashboard)
| ID | Task | Model | Size | Done when |
|---|---|---|---|---|
| 4.1 | Inbox page skeleton: conversation list + thread panel (reuse existing dashboard layout/table patterns) | Sonnet | M | Renders with mock data, <200 lines/component |
| 4.2 | All-conversations Realtime subscribe + reply insert (staff JWT) | Sonnet | M | Customer msg appears <1s; reply lands in widget |
| 4.3 | Staff JWT fetch (P2 endpoint) + Django ticket/booking context links in thread header | Sonnet | S | Links resolve to existing dashboard routes |

### P5 — Batch archive sync (backend; clone `cs/tasks.py::sync_ota_bookings` PostgREST pattern)
| ID | Task | Model | Size | Done when |
|---|---|---|---|---|
| 5.1 | Celery task: pull `cs_messages WHERE id > cursor` via PostgREST, bulk insert `cs_message`, advance cursor | Sonnet | M | Messages appear in Django after run |
| 5.2 | Cursor storage + idempotency test (run twice → identical count) | Sonnet | S | Test passes |
| 5.3 | Django admin action "Sync chat now" (fires 5.1) | Haiku | S | Button works in admin |
| 5.4 | Beat registration runbook — prod DB `PeriodicTask` (DatabaseScheduler, per [[prod-capacity-celery-audit]] — NOT celery.py) | Haiku | R | Runbook section added below |
| 5.5 | PDPA erasure: extend deletion flow to Supabase rows ([[cs-consent-gdpr-model]]) | Sonnet | S | Erase removes both stores |

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
*(append during build)*

## Related
[[chat-supabase-migration-plan]] · [[cs-chat-supabase-offload]] · [[cs-architecture-decision]] · [[prod-capacity-celery-audit]] · [[ota-p2-impl-plan]]
