# OTA Chat Realtime — Implementation + Audit Fixes

**Date:** 2026-07-08  
**Status:** ✅ FULLY TESTED + EXTENDED 2026-07-08. All merged → develop (BE `943cabe` · FE `436499b0` · AD `1b62ed3`). Comeback hybrid + soft-link + merge gate implemented. 10/10 identity-switch scenarios PASS.  
**Linked notes:** [[chat-supabase-migration-plan]] · [[ota-magic-link-trip-view]] · [[cs-guest-identity-best-practices]] · [[cs-realtime-be-traffic-design-verdict-2026-07-08]]

---

## What Was Built

OTA guests arriving at `/my-trip?token=<signed>` can now open realtime chat without email OTP. Both FE and AD show OTA booking context (source chip + booking_id).

### Backend Changes

**`cs/models.py`** — 2 new nullable fields on `Conversation`:
```python
ota_booking_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
ota_source     = models.CharField(max_length=20, null=True, blank=True)
```
Migration: `0011_add_ota_fields_to_conversation` (safe, no lock risk at current table size).

**`cs/views.py` — `ConversationCreateView.post()`** — new OTA branch before existing email branch:
1. Reads `ota_token` from request body (type-guarded: `isinstance(str)`)
2. Validates via `load_ota_trip_token()` → gets `{email, booking_id, source}`
3. Validates `CsOtaBooking` exists + not canceled + `is_magic_link_valid`
4. Get-or-create conversation by `(guest_email, ota_booking_id)` on open/pending status
5. Returns `ConversationSerializer` + `guest_token`

**`cs/serializers.py`** — both `ConversationSerializer` and `ConversationInboxSerializer` expose `ota_booking_id`, `ota_source` (read-only).

**`ConversationListView.get()`** — `?ota_booking_id=` filter added.

### Frontend Changes (`components/chat/ChatWidget.js`)

- Reads `router.query.token` on `/my-trip` only (`typeof string` guard for duplicate `?token=` params)
- On `handleOpen` with `otaToken` present: POST `{ota_token}` → get guest_token → open chat
- localStorage key `ota_conv_${btoa(otaToken).slice(0,16)}` stores `{conversationId, guestToken, ts}`
- Restore effect: on page refresh, restores from key if entry < 23h old (guards guest_token 24h TTL)
- `handleLeave` + `handleConversationClosed`: clear key on explicit leave/server-close

### Admin Dashboard Changes

**`components/cs/ConversationList.js`** — OTA source chip + booking_id in secondary text.  
**`components/cs/ConversationDetail.js`** — OTA header bar (source chip, booking_id, "View booking →" link).  
**`pages/cs/index.js`** — `?ota_booking_id=` deep-link pre-fills search (via `useEffect` + `router.isReady`).  
**`pages/dashboard/command-centre/index.js`** — "Chat" column in OTA bookings tab → routes to `/cs?ota_booking_id=<id>`. Tab deep-link (`?tab=1`) honored via `useEffect` + `router.isReady`.

---

## Audit Findings + Fixes (all applied in fix/ota-chat-audit)

| # | Sev | Issue | Fix |
|---|-----|-------|-----|
| 2 | HIGH | Canceled/nonexistent booking opened chat | Mirror `OtaTripView` checks in `ConversationCreateView` |
| 3 | HIGH | Non-string `ota_token` → `.strip()` → 500 | `isinstance(str)` type guard |
| 4b | HIGH | guest_token TTL 24h; returning day-2 guest restores expired token → silent 403 loop | Store `ts` in localStorage; discard entries >23h on restore |
| 4a | MED | `handleLeave` didn't clear OTA localStorage key | Clear key on leave + server-close |
| 5 | HIGH | Duplicate `?token=` → array → BE 500 | `typeof rawOtaToken === 'string'` guard |
| 9 | LOW | Chip in ListItemText primary → `<div>`-in-`<p>` hydration warning | `component: 'div'` on primaryTypographyProps |
| 10 | HIGH | CS inbox pre-filter dead: `useState(router.query...)` before hydration | `useEffect` + `router.isReady` seed |
| 11 | LOW | Command-centre `?tab=` param ignored | `useEffect` + `router.isReady` tab sync |

**Deferred (no code, product decisions):**
- #6: Logged-in user on OTA link gets guest conv (acceptable)
- #7: PDPA gate bypass (pre-existing all chat flows, separate task)
- #8: Multi-conv per email possible (staff awareness)

---

## Pending Ops

- [ ] Run `python manage.py migrate` on server (migration `0011`)
- [ ] Auth identity switch gaps → see [[ota-chat-auth-switch-analysis-2026-07-08]]
