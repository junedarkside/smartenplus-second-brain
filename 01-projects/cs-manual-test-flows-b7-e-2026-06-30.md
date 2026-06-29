---
name: cs-manual-test-flows-b7-e-2026-06-30
description: Click-by-click manual-test guide for CS-Centralization remaining flows B-7, B-8, C, D, E. Team-synthesized (3 agents: FE-UI + admin-UI + BE/data), code-grounded.
metadata:
  type: test-guide
  status: active
  date: 2026-06-30
  parent: cs-centralization-audit-2026-06-29
---

# CS-Centralization Manual Test — Flows B-7 → E

> 3-agent team trace (FE-UI + admin-UI + BE/data), code-grounded with file:line. Customer = Chrome `:3000` | Staff = Safari `:3001`. Booking under test: `ESZ7901601` (Direct). Passed already: A-1, A-2, B-1, B-2, B-3, B-6.

## Prerequisites
- Logged in on Chrome as owner of `ESZ7901601` (Confirmed, not past). Signed in on Safari admin (`:3001`).
- `NEXTAUTH_SECRET` matched (FE + admin).
- **One-open-ticket guard** (`tickets/models.py:173-187`): only 1 OPEN ticket per booking. Resolve/close existing open tickets before new submissions, else 400 "An open ticket already exists for this booking."

## Bug fixed this session
`updateRequestStatus` mutation (`admin-dashboard/store/api/ordersApi.js:201-208`) dropped `resolution_note` (body was `{ request_status }` only). Fixed in admin `9ac7089` — now transmits note. Unblocks `closed_no_action` (BE requires note) + reject-with-note.

---

## B-8 — Cancellation → booking Canceled *(testable now on direct)*

**Customer (Chrome `:3000`):**
1. `http://localhost:3000/bookings/ESZ7901601` → click **"Request Change"** (header bar, pencil icon; `BookingDetailMain.js:191`).
2. Modal *"Request a Booking Change"* → **Request Type** dropdown → pick **"Cancellation"** (`RequestChangeModal.js:20`).
3. (optional) *Additional details* → click **"Submit"** (`:121`).
4. ✅ Toast: *"Request submitted. Our team will contact you shortly."*

**Staff (Safari `:3001`):**
5. `/dashboard/command-centre` → **Direct Requests** tab (filter = `pending`).
6. Find the **cancellation** row → click **"Review"**.
7. Dialog → click **"Mark In Review"** (blue hero, non-terminal, fires immediately).
8. Change status filter (top-right `Select`) → **"in review"** → click **"Review"** on same row again. (No "Reopen" button — re-filter + re-click.)
9. Dialog now: green **"Resolve"** hero + red **"Reject"** + blue **"No Action Needed"**.
10. Click **"Resolve"** → ConfirmDialog *"Confirm Resolve"* → (optional note) → click **"Resolve"** (green). *(Buttons = **Cancel + action label**, NOT Confirm/Back.)*

**✅ Pass:**
- Admin row → `resolved`.
- Chrome `/bookings/ESZ7901601` → **Recent Requests** pill = **"Cancellation Confirmed"** (green; `TicketStatusBanner.js:207`).
- DB: `SELECT booking_status FROM bookings_bookingitem WHERE slug='ESZ7901601';` → **`Canceled`** (side-effect `tickets/views.py:306-314`).

---

## B-7 — Emergency toggle *(OTA ticket only — hidden on direct after admin `1a3ef2a`)*

Needs Flow C OTA data first. On an **OTA** ticket (`/tickets/<ticket_number>`):
1. Safari `:3001` → command-centre Review → **"Open Editor"** → ticket detail.
2. Checkbox **"Emergency — bypass OTA sync wait (same-day / weather cancel)"** (`[id].js:582`) → tick ON. Disabled on terminal statuses.
3. ✅ Pass: label turns **red**; **reload page** → still checked (no toast — verify via reload; `setEmergencyFlag` echoes into local data only).
4. **Bypass test:** OTA ticket `awaiting_ota_update` → Resolve normally 400-blocked ("Cannot resolve awaiting OTA ticket…") → toggle Emergency ON → Resolve succeeds (`clean()` Blocker 3 bypass, `tickets/models.py:122`).

---

## Flow C — OTA `/my-trip` portal

**Prereq — seed OTA data.** ⚠️ Do NOT use `manage.py seed_ota_fake_data` (it runs `CsOtaBooking.objects.all().delete()` → wipes real rows + orphans GenericFK-linked tickets, `seed_ota_fake_data.py:127`). Use targeted shell:
```python
# python manage.py shell
from cs.models import CsOtaBooking; import datetime
CsOtaBooking.objects.update_or_create(
  source='12go', booking_id='TEST-12GO-0001',
  defaults={'booking_date':datetime.date(2026,7,1),'email':'test@example.com',
            'customer_name':'Test','status':'confirmed','destination':'Hat Yai → Koh Lipe'})
```
(Seed dates 2026-07-01..10 → both magic-link TTL checks pass: 7d-from-mint + trip-date+7d.)

**Staff (Safari):**
1. Command Centre → **OTA Bookings** tab → row `TEST-12GO-0001` → **"Copy Link"** (Trip Link col) → **"Copied!"** (`command-centre/index.js:464`).

**Guest (Chrome, incognito):**
2. Paste `http://localhost:3000/my-trip?token=<…>`.
3. PDPA screen → **"I Accept — View My Trip"** (`OtaPdpaGate.js:51`).
4. Trip card *"Your Trip"* → **"Request a Change"** (`OtaRequestForm.js:56`) → *Request Type* native select → **Cancellation** → **"Submit Request"** (`:186`).
5. ✅ Pass: ticket card *"Waiting for Review"* appears; polls 60s.

**Gotcha:** 2nd request on same booking while first open → 400 (one-open guard). `trip_id` NULL on all seeded/synced OTA → emergency manifest fanout no-ops (set manually if testing that).

---

## Flow D — Chat widget *(no seed — `cs_chat` fail-open ON)*

`FeatureFlagView` `get_or_create defaults={'enabled': True}` (`cs/views.py:376`) → chat ON by default. `useFeatureFlag` fail-open (`hooks/useFeatureFlag.js:6`).

1. Chrome any page → bottom-right **blue FAB** (aria "Open customer support chat"; `ChatBubble.js:5`).
2. Guest (no session) → email gate → type email → **"Start chat"** (`ChatGuestForm.js:43`).
3. Type message → **"Send"** (`ChatPanel.js:101`).
4. ✅ Pass: your msg = right blue bubble; staff reply (admin chat inbox) = left bubble.

**Toggle off (kill-switch test):** staff `PATCH /api/cs/feature-flags/cs_chat/ {enabled:false}` (immediate, no 60s lag on write path).

---

## Flow E — OTA sync

**Staff (Safari):**
1. OTA ticket detail → **"Sync Now"** (Supabase banner; `[id].js:326`) → **"Queued!"**. Async — needs Celery worker (`POST /api/cs/ota/sync/` → 202).
2. **No-worker alternative:** `python manage.py sync_ota_bookings --source 12go` (synchronous, `--dry-run` available).

**✅ Pass:** new `cs_otabookingevent` rows (`trigger='sync'`) + `cs_csotabooking.last_synced_at` bumped. *(Counter quirk: `skipped` = updated-in-place, NOT failed; `upserted` = newly-created only.)*

---

## Related
- [[cs-centralization-audit-2026-06-29]] · [[cs-workflow-revised-2026-06-27]] · [[command-centre-ticket-booking-flow]]
- Vault master-state Section 2 REASSESSMENT note (Tier-1 landed).
- BE side-effect + guards: `tickets/views.py:248-319`, `tickets/models.py:108-200`.
