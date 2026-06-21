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
**Conversation:** `id` PK · `guest_email` (EmailField null) · `user` (FK Account null, SET_NULL) · `status` (open/pending/closed, default open) · `identity_type` (guest/customer) · `created_at` · `updated_at`.
**Message:** `id` PK · `conversation` (FK CASCADE, **NOT NULL** — follows `dialogue/Comment` pattern, ruling: floating message invalid) · `body` (TextField) · `sender` (customer/cs/system, **server-derived, never client-trusted**) · `created_at` (db_index, used as poll cursor).

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

### 3. GET /api/cs/messages/?conversation=&since=&email= — poll delta
Auth: staff any conv; customer own conv (`conversation.user==request.user`); guest needs `?email=` proof (`guest_email==email`, same pattern as `expirePendingCharge` guest auth).
- `since` = ISO 8601 UTC cursor (`created_at > since`); omitted → last 50. (ID-cursor `since_id` valid alternative — pick one, be consistent FE↔BE.)
- **200:** `{messages:[{id, conversation, body, sender, created_at}]}`. Empty `[]` when nothing new (no special code; FE keeps polling). Fields: `['id','conversation','body','sender','created_at']`.
- Errors: 400 `CONVERSATION_REQUIRED` · 404 `CONVERSATION_NOT_FOUND` · 403 `PERMISSION_DENIED` (guest/customer mismatch) · 400 `INVALID_CURSOR`.

### 4. POST /api/cs/messages/ — send
Auth: same as #3. Body `{conversation, body, email?}`. **`sender` forbidden in body — stripped.** Derived: staff→`cs`, else→`customer`.
- **Auto-reopen side-effect:** customer/guest posts to `closed` conv → `status='open'` before save (hard rule, logged). 201 reflects post-transition.
- **201:** MessageSerializer (same fields as #3).
- Errors: 400 `CONVERSATION_REQUIRED`/`BODY_REQUIRED`/`BODY_TOO_LONG`(>4000) · 404 `CONVERSATION_NOT_FOUND` · 403 `PERMISSION_DENIED`.

### 5. PATCH /api/cs/conversations/<id>/ — staff status transition
Auth: `IsAdminOrIsStaff`. Body `{status}` (open|closed only; `pending` not staff-settable). Other fields ignored.
- Transitions: open↔closed, pending→open/closed allowed; →pending rejected; same=idempotent 200.
- **200:** `{id, status, identity_type, updated_at}`.
- Errors: 403 `PERMISSION_DENIED` · 404 `CONVERSATION_NOT_FOUND` · 400 `INVALID_STATUS`/`INVALID_STATUS_TRANSITION`.

### 6. POST /api/cs/otp/request/ — Email-OTP request
Auth: AllowAny. **No user enumeration — always 200 generic.** Rate-limit 3/email/hr (DRF throttle scope `otp_request` or Redis `otp_request:{email}` TTL 3600).
- Logic: validate email → ratelimit → `pyotp` base32 secret → `cache.set(f"cs_otp:{email}", {secret, attempts:0}, timeout=600)` (matches password-reset TTL `accounts/views.py:297`) → SES send (same boto3 as `PasswordResetViewSet`) → SES fail logs warning, still 200.
- **200:** `{detail:"If this email is registered, an OTP has been sent."}`.
- Errors: 400 `EMAIL_REQUIRED`/`INVALID_EMAIL` · 429 `OTP_RATE_LIMITED`. No 404.

### 7. POST /api/cs/otp/verify/ — verify + issue session
Auth: AllowAny. Body `{email, code}`.
- Logic: `cache.get(cs_otp:email)` → miss=`INVALID_OR_EXPIRED_OTP` · attempts≥5=`OTP_RATE_LIMITED` (brute-force guard) · `pyotp.TOTP(secret).verify(code, valid_window=1)` fail→increment attempts → pass→delete key (single-use) → issue JWT.
- **200 (NextAuth CredentialsProvider shape):** `{id(str), accessToken, refreshToken, profile:{email, first_name, last_name, username}}`. accessToken 15min, refreshToken 7day, same signing as existing flow.
- Errors: 400 `EMAIL_REQUIRED`/`CODE_REQUIRED` · 401 `INVALID_OR_EXPIRED_OTP` (expired+wrong indistinguishable) · 429 `OTP_RATE_LIMITED` · 401 `ACCOUNT_NOT_FOUND` (P1a: require existing account; guest-account creation = P1b decision).

## Cross-cutting
- Auto-reopen = view-layer (`conversation.save(update_fields=['status','updated_at'])` before `serializer.save()`); CS Dashboard picks up on next poll, no webhook.
- Throttle: OTP scopes `otp_request: 3/hour`, `otp_verify: 10/hour` (matches `password_reset` scope pattern).
- All outbound chat-path HTTP (none here, but OTP SES) — standard. No `__all__`.

## Open (P1b)
OTP guest-account: create thin `Account(is_guest=True)` + scoped JWT, OR keep guest stateless on `Conversation.guest_email`. P1a = require existing account (`ACCOUNT_NOT_FOUND`).

## Related
- [[cs-architecture-decision]] — polling decision this implements
- [[cs-centralization-stack]] · [[cs-consent-gdpr-model]] · [[cs-centralization-design-concept]]
