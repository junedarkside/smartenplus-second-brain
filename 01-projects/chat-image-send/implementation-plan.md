# Chat Image-Send — Implementation Plan (from design v2.1)

> **STATUS: IMPLEMENTED 2026-07-13 — all 3 repos merged → develop.**
> BE `0bd8adf` · AD `f473a7f` · FE `53f30576`. 20 new BE tests green; full cs suite green
> (1 pre-existing unrelated failure). Steps 2-4 complete incl. 16-correction gate.
> **Extra fix found during impl:** `ChatMediaStorage.custom_domain = None` — global
> `AWS_S3_CUSTOM_DOMAIN` makes S3Boto3Storage.url() return UNSIGNED URLs, silently
> bypassing querystring_auth (private objects would 403 for every viewer).
> **Deviation:** sync task does NOT map image_url (ImageField holds S3 key, not URL;
> image rows are always Django-created first w/ supabase_id backfill — documented in code).
> **REMAINING (user):** Step 1 Supabase SQL + deploys + prod smoke (see bottom).

**Spec:** `design-2026-07-12.md` (v2.1 — audited). Read it first; this doc = execution checklist only.
**Deploy order:** Supabase SQL → BE → AD → FE. Each step independently deployable + revertable.
**Branches:** BE `feat/chat-image-send` · AD `feat/ad-chat-image` · FE `feat/fe-chat-image`

---

## Step 1 — Supabase (additive, deploy first)

- [ ] New `supabase/migrations/003_cs_messages_image_url.sql`:
  ```sql
  ALTER TABLE public.cs_messages ADD COLUMN image_url text;
  ```
- [ ] Run via same process as 001/002
- [ ] Verify: realtime payload includes column (insert test row, check subscription); old clients unaffected

## Step 2 — Backend (`smartenplus-backend`)

Ordered — each item has acceptance criterion:

- [ ] **2.1** `Smartenplus/media_storages.py` — `ChatMediaStorage(S3Boto3Storage)`: `location='media/cs_chat'`, `default_acl='private'`, `querystring_auth=True`
  - ✓ `.url` returns presigned URL w/ signature params; existing MediaStorage untouched
- [ ] **2.2** `cs/models.py` — `Message.image = ImageField(null=True, blank=True, storage=ChatMediaStorage())` + migration
  - ✓ migration additive nullable; `body` stays non-null (empty string OK for image-only)
- [ ] **2.3** `cs/serializers.py` — MessageSerializer: `image_url` SerializerMethodField → `obj.image.url if obj.image else None`; `get_last_message_preview` (line 44) '📷 Photo' branch for image-only
  - ✓ `image_url` in `fields` — polling clients blind without it (audit correction #6)
- [ ] **2.4** `cs/supabase_client.py` — `insert_cs_message(conv_id, body, sender, image_url=None) -> int` w/ `Prefer: return=representation`; `insert_cs_system_message` delegates
  - ✓ returns Supabase row id; 4 existing system-message call sites (views 128/284/314/353) behavior unchanged
- [ ] **2.5** `cs/views.py` — extract `_resolve_message_sender()` (448-471) + `_create_message_with_reopen()` (473-494) from MessageCreateView. REFACTOR ONLY — text path semantics identical, run existing tests before continuing
- [ ] **2.6** `cs/views.py` — `MessageImageCreateView` (AllowAny, MultiPartParser+FormParser, CsImageThrottle):
  1. validate conversation + image present; body optional ≤4000 (NO body-required guard — audit #8)
  2. `_resolve_message_sender()`
  3. **guest gate**: `if sender==SENDER_CUSTOMER and not request.user.is_authenticated and not conv.ota_booking_id → 403 IMAGE_NOT_ALLOWED`
  4. `process_operator_image(f, max_output_size=80*1024, max_dimensions=(1200,1000,800))` — import from `operators.utils`; wrap `UnidentifiedImageError`/`ValidationError` → 400 (audit #10)
  5. save to `msg.image` (private S3 via ChatMediaStorage)
  6. `_create_message_with_reopen()` — reopen 429 BEFORE broadcast
  7. `upsert_cs_conversation(conv)` → `sb_id = insert_cs_message(conv.id, body, sender, image_url=presigned_7day)` → `Message.objects.filter(pk=msg.pk).update(supabase_id=sb_id)` (audit #1 dedup)
  8. Supabase fail → warn + 201 anyway
  - ✓ 7-day presigned for Supabase: `msg.image.storage.url(msg.image.name, expire=7*24*3600)` or boto3 generate_presigned_url
- [ ] **2.7** `cs/urls.py` — `path('messages/send-image/', ...)`
- [ ] **2.8** `cs/throttles.py` — `CsImageThrottle`: custom `get_cache_key()` → guest-token value → user id → IP fallback (audit: Thai shared WiFi). Settings: `'cs_image': '30/hour'` in DEFAULT_THROTTLE_RATES (missing = ImproperlyConfigured, audit #11)
- [ ] **2.9** `cs/apps.py` — `pillow_heif.register_heif_opener()` in `ready()` (idempotent; kills dialogue load-order dependency, audit #12)
- [ ] **2.10** `cs/tasks.py:221-226` — `Message(...)` constructor + image mapping from `row.get('image_url')` (audit #7 — race-window rows)
- [ ] **2.11** `cs/tests/test_image_messages.py`:
  - auth matrix: staff 201 · logged-in 201 · OTA guest-token 201 · plain guest-token **403 IMAGE_NOT_ALLOWED** · no auth 403
  - cross-conv guest token 403 · corrupt file 400 (not 500) · oversized 400 · bad ext 400 · body 4001 → 400 · image-only empty body 201
  - closed conv → reopen · 4th reopen/hr 429 (before Supabase call — mock assert order)
  - Supabase mock: payload includes image_url; supabase_id backfilled
  - throttle: two different guest tokens same IP → independent buckets
- [ ] **2.12** Full existing cs test suite passes (refactor regression)

## Step 3 — Admin dashboard (`admin-dashboard`)

- [ ] **3.1** `store/api/csApi.js` — `sendImageMessage` mutation: FormData(conversation, image, body?), POST `/api/cs/messages/send-image/`, invalidates Message+Conversation, NO manual Content-Type
- [ ] **3.2** `components/cs/ConversationDetail.js` — attach button + hidden file input (accept `image/*,.heic,.heif`) + preview thumb + remove-X + 20MB pre-check. **Image branch BEFORE Supabase insert at line 85** (audit #14). Render `msg.image_url` behind S3-host allowlist: `<img>` max-height 200, lazy, click→new tab
- [ ] **3.3** `hooks/useStaffChatRealtime.js` — history select (:85) + payload map (:109) +`image_url`; **history fetch → Django MessageListView** (fresh presigned, audit privacy fix)
- [ ] **3.4** `pages/dashboard/SideList.js` — **:124 destructure +`image_url`** (audit #13) + :132 preview '📷 Photo'

## Step 4 — Customer frontend (`smartenplus-frontend`)

- [ ] **4.1** `helpers/chatImage.js` — `isAllowedChatImageUrl(url)` (S3 host prefix) + `isHeic(file)`
- [ ] **4.2** `components/chat/ChatWidget.js` — pass `canSendImage={Boolean(state.token) || Boolean(otaToken)}` to ChatPanel
- [ ] **4.3** `components/chat/ChatPanel.js` — attach button ONLY when `canSendImage`. Preview strip (HEIC → filename chip). File → skip USE_REALTIME branch, POST multipart w/ existing header logic (lines 40-42). Handle 429/400/403. Render image behind allowlist. Text path byte-identical
- [ ] **4.4** `hooks/useChatRealtime.js` — history select (:85) + payload map (:114) +`image_url`; **history fetch → Django MessageListView**
- [ ] **4.5** `hooks/useChatPolling.js` — no change (verify only)

## Step 5 — Verification matrix (from design doc)

**OTA / logged-in / staff** × **realtime / polling**:
- [ ] Image-only send renders both directions (polling: up to 30s if idle — backoff)
- [ ] Image + caption
- [ ] Text regression unchanged
- [ ] Admin inbox '📷 Photo' + unread bump
- [ ] Closed conv → reopen; 4th/hr → 429 in UI
- [ ] Reject 25MB / renamed-.exe (400 not 500) / 4001 caption; HEIC → WebP end-to-end
- [ ] DB: single row, supabase_id set, no dup after sync tick; S3 `media/cs_chat/` ≤80KB WebP ≤1200px **private ACL**
- [ ] **Guest:** attach hidden; crafted multipart → 403; text unchanged; guest→login → attach appears
- [ ] **Privacy:** raw S3 URL no params → AccessDenied; presigned works; expired presigned → 403
- [ ] **Throttle:** 2 devices same IP different convs → independent budgets
- [ ] Old conv (>7d) in realtime mode → images load (Django history path)

## Pre-merge gate — 16 audit corrections

All boxed items above map to audit corrections #1-16 in design doc. Before merge, re-read design doc "Critical corrections" section and confirm each ✓.

## Rollback

Revert order-free. Columns nullable additive. ChatMediaStorage scoped — existing media untouched. FE/AD rendering presence-guarded.

---

**Spec:** [[chat-image-send/design-2026-07-12]] · **Pattern:** [[chat-image-send-server-convergence]]
