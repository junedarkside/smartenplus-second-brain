---
name: cs-api-contract
description: CS Centralization backend API contract — 7 endpoints (conversations, messages poll/send, status PATCH, OTP request/verify). Polling-based (Gap 4a). Explicit serializer fields, no __all__.
metadata:
  type: decision
  status: draft
  date: 2026-06-21
  parent: cs-architecture-decision
---

# CS API Contract

> **Gap-1 closure 2026-06-21.** Built on [[cs-architecture-decision]] (both-sides-poll, Supabase OUT of message path). Django = single source of truth. All serializers explicit fields — never `__all__` (103 exist in backend; new CS code must not add).

## Permission (confirmed from source)
`IsAdminOrIsStaff` (`accounts/permissions.py:9-14`): `is_authenticated AND (is_admin OR is_staff)`. `is_admin` is a custom `Account` field, not Django built-in. Reuse directly.

## Models (pin before serializers)
**Conversation:** `id` PK · `guest_email` (EmailField null) · `user` (FK Account null, SET_NULL) · `status` (open/pending/closed, default open) · `identity_type` (guest/customer) · `created_at` · `updated_at` · `reopen_count` (int default 0) · `reopen_last_at` (datetime null) — abuse guard: auto-reopen rejected if `reopen_count >= 3` within 1h → 429.
**Message:** `id` PK · `conversation` (FK CASCADE, **NOT NULL** — follows `dialogue/Comment` pattern, ruling: floating message invalid) · `body` (TextField) · `sender` (customer/cs/system, **server-derived, never client-trusted**) · `created_at` (db_index).
**CSOtp:** `email` (EmailField, indexed) · `secret` (CharField — HOTP counter secret) · `attempts` (int default 0) · `expires_at` (datetime) — stored in **PostgreSQL not Redis** (Redis `allkeys-lru` evicts under memory pressure → INVALID_OR_EXPIRED_OTP with no recourse). Periodic cleanup job deletes expired rows.

## Error convention
`{ "error": "human msg", "code": "SCREAMING_SNAKE" }`. HTTP status = category; `code` = frontend discriminator. Follows existing 409-mapping pattern.

## Endpoints

### 1. POST /api/cs/conversations/ — get-or-create (idempotent)
Auth: AllowAny + server identity resolution. Guest sends `{email}`; logged-in uses session (`session.user.email`, email ignored if sent). Looks up open/pending conv → returns or creates.
- **200/201:** `{id, status, identity_type, created}`. Fields: `['id','status','identity_type','created']`.
- Errors: 400 `EMAIL_REQUIRED` (guest no email) · 400 `INVALID_EMAIL`. Closed conv doesn't block new (201).

### 2. GET /api/cs/conversations/ — CS inbox list
Auth: `IsAdminOrIsStaff`. Query: `status`, `page`, `page_size`(max 50, default 20).
- **200:** paginated `{count, next, previous, results:[{id, customer_name, customer_email, last_message_preview(80c), last_message_at, unread_count, status, identity_type}]}`.
- Resolution: name/email from `user` (customer) or `guest_email` (guest, name null). Order `last_message_at DESC NULLS LAST`. `select_related('user')` + prefetch last message (no N+1). `unread_count` = customer-sender msgs after last staff reply; if `read_at` deferred → return 0 + document gap.
- Errors: 401 `NOT_AUTHENTICATED` · 403 `PERMISSION_DENIED` · 400 `INVALID_STATUS`.

### 3. GET /api/cs/messages/?conversation=&cursor= — poll delta
Auth: staff any conv; customer own conv (`conversation.user==request.user`); guest sends signed token in `Authorization: Bearer <token>` header (issued by endpoint 7, `django.core.signing`, TTL 86400s) — `?email=` proof dropped (unfakeable signed token replaces it).
- `cursor` = last seen message **id** (integer, server-side opaque); omitted → last 50. Server does `id > cursor` — **NOT** `created_at > client_time` (client clock drift/DST breaks timestamp cursor for Thai users).
- Response includes `next_cursor` = id of last message in response. FE stores and echoes on next poll.
- **200:** `{messages:[{id, conversation, body, sender, created_at}], next_cursor}`. Empty `{messages:[], next_cursor: current_cursor}` when nothing new. Fields: `['id','conversation','body','sender','created_at']`.
- Errors: 400 `CONVERSATION_REQUIRED` · 404 `CONVERSATION_NOT_FOUND` · 403 `PERMISSION_DENIED` · 400 `INVALID_CURSOR`.

### 4. POST /api/cs/messages/ — send
Auth: same as #3 (signed token for guests). Body `{conversation, body}`. **`sender` forbidden in body — stripped.** Derived: `IsAdminOrIsStaff`→`cs`, else→`customer`.
- **Auto-reopen side-effect:** customer/guest posts to `closed` conv → check `reopen_count`: if `reopen_count >= 3` AND `reopen_last_at` within 1h → **429 `REOPEN_RATE_LIMITED`**. Otherwise increment `reopen_count`, set `reopen_last_at=now`, `status='open'` (logged). 201 reflects post-transition.
- **201:** MessageSerializer (same fields as #3, no `next_cursor`).
- Errors: 400 `CONVERSATION_REQUIRED`/`BODY_REQUIRED`/`BODY_TOO_LONG`(>4000) · 404 `CONVERSATION_NOT_FOUND` · 403 `PERMISSION_DENIED` · 429 `REOPEN_RATE_LIMITED`.

### 5. PATCH /api/cs/conversations/<id>/ — staff status transition
Auth: `IsAdminOrIsStaff`. Body `{status}` (open|closed only; `pending` not staff-settable). Other fields ignored.
- Transitions: open↔closed, pending→open/closed allowed; →pending rejected; same=idempotent 200.
- **200:** `{id, status, identity_type, updated_at}`.
- Errors: 403 `PERMISSION_DENIED` · 404 `CONVERSATION_NOT_FOUND` · 400 `INVALID_STATUS`/`INVALID_STATUS_TRANSITION`.

### 6. POST /api/cs/otp/request/ — Email-OTP request
Auth: AllowAny. **No user enumeration — always 200 generic.**
- Rate-limit (two layers): Redis `INCR cs:otp:issue:{email}` TTL=3600s cap 3 (per-email, not per-IP — shared NAT breaks DRF IP throttle). DRF throttle acceptable as first-pass only.
- Logic: validate email → ratelimit → `pyotp.HOTP` base32 secret + counter=0 → write to **PostgreSQL `CSOtp` table** (`email`, `secret`, `attempts=0`, `expires_at=now+600s`) — **NOT Redis** (`allkeys-lru` evicts OTP under memory pressure → unrecoverable user lockout) → SES send (same boto3 as `PasswordResetViewSet`) → SES fail logs warning, still 200. OTP type = **HOTP** (counter-based, no clock sync needed — SES delivery latency + client clock drift makes TOTP fragile).
- **200:** `{detail:"If this email is registered, an OTP has been sent."}`.
- Errors: 400 `EMAIL_REQUIRED`/`INVALID_EMAIL` · 429 `OTP_RATE_LIMITED`. No 404.

### 7. POST /api/cs/otp/verify/ — verify + issue session + guest token
Auth: AllowAny. Body `{email, code}`.
- Logic: `CSOtp.objects.get(email=email)` → miss/expired=`INVALID_OR_EXPIRED_OTP` · `attempts>=5`=`OTP_RATE_LIMITED` · `pyotp.HOTP(secret).verify(code, counter=0)` fail→`attempts+=1, save()` → pass→`CSOtp.delete()` (single-use) → issue JWT + **guest signed token**.
- Guest signed token: `django.core.signing.dumps({'email': email, 'conversation_id': conv_id}, salt='cs-guest')` TTL=86400s. Returned alongside JWT so guest can immediately start messaging without full session.
- **200 (NextAuth CredentialsProvider shape):** `{id(str), accessToken, refreshToken, profile:{email, first_name, last_name, username}, guest_token(str|null)}`. accessToken 15min, refreshToken 7day, same signing as existing flow.
- Errors: 400 `EMAIL_REQUIRED`/`CODE_REQUIRED` · 401 `INVALID_OR_EXPIRED_OTP` (expired+wrong indistinguishable) · 429 `OTP_RATE_LIMITED` · 401 `ACCOUNT_NOT_FOUND`.

## Cross-cutting
- Auto-reopen rate-limit enforced in view before `serializer.save()`. `reopen_count` resets to 0 when staff closes conv (clean slate on staff-initiated close).
- OTP rate-limit counters: Redis `cs:otp:issue:{email}` (issue) + `CSOtp.attempts` field (verify brute-force). DRF throttle = IP first-pass only.
- Poll interval: **5-10s minimum** client-side (not 3s). Realistic DB query = 100-300ms → 2 slots / 200ms = 10 req/s usable → 30 simultaneous widgets before queuing. nginx hard timeout 10s on CS endpoints.
- All CS serializers: explicit `fields` list. No `__all__`.

## Open (P1b)
OTP guest-account: create thin `Account(is_guest=True)` + scoped JWT, OR keep guest stateless on `Conversation.guest_email`. P1a = require existing account (`ACCOUNT_NOT_FOUND`).

## Related
- [[cs-architecture-decision]] — polling decision this implements
- [[cs-centralization-stack]] · [[cs-consent-gdpr-model]] · [[cs-centralization-design-concept]]
