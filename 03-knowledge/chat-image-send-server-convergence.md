---
name: chat-image-send-server-convergence
description: Pattern — server-side upload converges dual chat transports; Django insert to Supabase via service role fires realtime broadcast for free; dedup via supabase_id backfill
metadata:
  type: reference
---

**Pattern:** when a chat system has dual transports (Supabase realtime client-insert + Django polling POST), new message types with server-side processing (file upload, moderation, etc.) should **converge on one server endpoint** instead of duplicating logic per transport.

**How it works (SmartEnPlus chat image-send):**

1. Client POSTs multipart to Django endpoint (works uniformly for all auth tiers: Bearer / guest token / OTA-derived guest token)
2. Django processes (validate → WebP compress → S3) and creates local `Message` row
3. Django inserts mirrored row to Supabase `cs_messages` via **service role key** (bypasses RLS)
4. Supabase `postgres_changes` fires → all subscribed realtime clients receive the message instantly — **no client-side Supabase insert needed**
5. Polling clients get it via normal serializer fetch

**Critical dedup requirement:** if a sync task pulls Supabase rows back into Django (dedup by unique `supabase_id`), the endpoint MUST capture the Supabase row id at insert time (`Prefer: return=representation` header) and backfill `Message.supabase_id` immediately — otherwise the sync re-imports the row as a duplicate.

**Ordering requirement:** any business rejection (rate limit, reopen 429) must be decided BEFORE the Supabase insert — realtime broadcast is irrevocable.

**Security note:** RLS is row-level, not column-content-level — a scoped realtime client can still insert arbitrary string values (e.g. spoofed `image_url`). Mitigate at render time with domain allowlist, optionally + SQL CHECK constraint.

**How to apply:** any future chat message type carrying server-processed payloads (files, structured cards, payments) uses this same shape: one endpoint, service-role mirror, supabase_id backfill. [[cs-guest-storm-investigation]]
