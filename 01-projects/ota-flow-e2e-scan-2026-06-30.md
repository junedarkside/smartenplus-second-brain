# OTA Flow E2E Scan 2026-06-30

## Summary

E2E code scan of OTA flows (C/E/B-7) deferred from CS-Centralization deploy. 5 issues found: 3 FE bugs fixed on `fix/ota-flow-bugs`, 2 deferred to BE deploy.

## Context

OTA flows deferred per master-state.md resume point #2. CS-Centralization (direct booking flows A/B direct) deployed separately. OTA (`/my-trip`, sync, emergency bypass) ships as next deploy after this scan + test.

## Details — Issues Found

### Bug 1 — CRITICAL (FIXED): `COLORS.gray[400]` crash

**File:** `components/bookings/TicketStatusBanner.js:119`  
**Root cause:** `COLORS` has no top-level `gray` key — correct path is `COLORS.neutral.gray400`. `COLORS.gray` is `undefined`; accessing `[400]` throws `TypeError` at render.  
**Trigger:** Any ticket with an "upcoming" SLA stage (normal state on first open). Crashed both `/my-trip` and `/bookings/[bookingId]` whenever a ticket existed.  
**Fix:** `COLORS.gray[400]` → `COLORS.neutral.gray400`  
**Status:** Fixed on `fix/ota-flow-bugs`

### Bug 2 — MODERATE (FIXED): `data.image.length` unguarded

**File:** `components/bookings/BookingDetail/TripRoute.js:128`  
**Root cause:** `!!data.image.length` — `data.image` not optional-chained. All other field accesses in the file use `data?.x`. Crashes when API returns booking with no `image` field.  
**Fix:** `!!data.image.length` → `!!data?.image?.length`  
**Status:** Fixed on `fix/ota-flow-bugs`

### Bug 3 — PERFORMANCE (FIXED): `ChangeRequestsSection` polls unconditionally

**File:** `components/bookings/ChangeRequestsSection.js:14`  
**Root cause:** `pollingInterval: 60000` hardcoded. `ChangeRequestsSection` only renders on `/bookings/<id>` (direct booking, NOT OTA). Parent `[bookingId].js:28-31` already owns a 60s poll on the same RTK cache key — child polling was completely redundant (two timers, same network request deduped but two schedulers running).  
**Fix (c96b1724):** First attempted `useState(60000)` + `useEffect` denylist gate — correctly caught by 4-agent audit as CLAUDE.md violation ("derive inline, never in useEffect") + the child's stop would be defeated by parent's unconditional timer anyway.  
**Fix (09e3f955 — final):** Removed `pollingInterval`, `useState`, `TERMINAL_STATUSES`, polling `useEffect` from `ChangeRequestsSection` entirely. Parent owns data; child is pure display.  
**Status:** Fixed on `fix/ota-flow-bugs` (`09e3f955`)

### Bug 4 — DATA GAP (DEFERRED): OTA ticket API omits SLA/resolution fields

**File:** `smartenplus-backend/cs/views.py` (`OtaTripView` ~lines 519–527)  
**Root cause:** `GET /api/cs/ota/trip/?token=…` returns tickets with only `ticket_number`, `request_type`, `request_status`, `date_created`, `requested_value`. Missing: `resolution_stage`, `operator_deadline`, `ota_deadline`, `admin_contacted_ota_at`, `admin_contacted_ota_note`, `admin_initiated`, `is_emergency`.  
**Impact:** `TicketStatusBanner` gracefully returns `null` for missing fields (no crash), but OTA customers see blank SLA timeline and no emergency indicator.  
**Status:** DEFERRED — backend-only, no crash, fix in OTA deploy session

### Bug 5 — INTEGRITY (DEFERRED): Backend OTA change-request allows duplicate open tickets

**File:** `smartenplus-backend/cs/views.py` (`OtaChangeRequestView`)  
**Root cause:** Frontend guards `showForm = openTickets.length === 0 && !localSubmitted` (UI only). Backend `OtaChangeRequestView` has no uniqueness guard — direct POST creates multiple simultaneous open tickets per booking.  
**Fix:** Apply `[[genericfk-one-open-ticket-guard]]` pattern — `Ticket.clean()` guard + `full_clean()` in create view.  
**Status:** DEFERRED — backend integrity fix, separate deploy

## Decision

| Bug | Action | Reason |
|-----|--------|--------|
| Bug 1 — SLA dot crash | Fixed FE | 1 line, crashes on ticket open |
| Bug 2 — image guard | Fixed FE | 1 line, moderate crash risk |
| Bug 3 — unconditional poll | Fixed FE | 5 lines, parity with direct-booking path |
| Bug 4 — OTA API data gap | Deferred BE | No crash, backend-only |
| Bug 5 — duplicate ticket guard | Deferred BE | Backend integrity, `[[genericfk-one-open-ticket-guard]]` |

## Manual Test Guide — E2E

### Prerequisites
- Dev server: `npm run dev`
- Backend running with OTA booking seed (use targeted seed from `[[cs-manual-test-flows-b7-e-2026-06-30]]`, NOT destructive `seed_ota_fake_data`)
- Magic link token minted: `POST /api/cs/ota/trip-link/` with a valid `CsOtaBooking.id`

### Flow C — OTA Guest `/my-trip`

| Step | Action | Expected |
|------|--------|----------|
| C1 | Visit `/my-trip?token=<valid-token>` (clear localStorage first) | PDPA gate shown |
| C2 | Click "I Accept" | Gate disappears, trip data loads (booking #, route, date, passengers) |
| C3 | With no open tickets: check for `OtaRequestForm` | Form present |
| C4 | Submit a request (fill reason field, click Submit) | Form disappears → `TicketStatusBanner` shows `pending` status, no crash |
| C5 | Reload page with open ticket | Form hidden (no double-submit guard working) |
| C6 | Wait 60s or manually advance ticket status on admin | Banner updates to new status (poll confirmed) |
| C7 | All tickets reach terminal status (`resolved`/`rejected`) | Poll stops (Bug 3 fix — verify via network tab: no requests after all terminal) |
| C8 | Visit with expired/invalid token | Error state shown, no crash |

### Flow E — OTA Sync

| Step | Action | Expected |
|------|--------|----------|
| E1 | `POST /api/cs/ota/sync/` or trigger Celery beat | 200 OK, `CsOtaBooking` rows created/updated |
| E2 | Check admin dashboard OTA queue | Synced bookings appear |
| E3 | Run sync again | No duplicate rows (idempotent) |

### Flow B-7 — Emergency OTA Bypass

| Step | Action | Expected |
|------|--------|----------|
| B7-1 | Admin opens OTA ticket in command centre | `is_emergency` toggle visible in admin UI |
| B7-2 | Toggle emergency ON | `Ticket.is_emergency = True`, bypasses normal SLA queue order |
| B7-3 | View ticket on `/my-trip` | SLA timeline fields absent (Bug 4 — documented deferred, no crash) |

### Regression Check — Direct Booking Path

| Step | Action | Expected |
|------|--------|----------|
| R1 | Login → `/bookings/<id>` with open ticket | `TicketStatusBanner` renders, SLA dots show (Bug 1 fix: no crash) |
| R2 | Ticket in `pending` state with future SLA stages | Stage dots: active = brand-blue, upcoming = gray (not crash) |
| R3 | Booking with no `image` field from API | `TripRoute` renders without crash (Bug 2 fix) |
| R4 | Resolved booking with past tickets | `ChangeRequestsSection` visible, polling stops (Bug 3 fix — check network tab) |

## Also Fixed (post-4-agent-audit) — Bug 3b + Bug 3c

### Bug 3b — OTA `/my-trip` had same useState/useEffect anti-pattern (FIXED `09e3f955`)

**File:** `pages/my-trip/index.js:43-66`
Same violation: `useState(false)` + `useEffect` syncing `hasOpenTicket`. Fixed: removed both, inline `bookingRef.current?.tickets` derivation in `pollingInterval`.

### Bug 3c — CRITICAL TDZ crash introduced by Bug 3b fix (FIXED `0657c6fb`)

**File:** `pages/my-trip/index.js:52-57`
`const booking` referenced inside its own destructuring hook call options — JavaScript Temporal Dead Zone: `const` binding doesn't exist yet when options object is evaluated → `ReferenceError` on every render, crashing `/my-trip` entirely.

**Fix:** `useRef(null)` carries previous render's booking value. Ref is readable before `const booking` exists. `pollingInterval` reads `bookingRef.current?.tickets`. After hook returns, `if (booking !== undefined) bookingRef.current = booking` keeps ref in sync.

Caught by final verification scan agent before merge.

## Also Fixed (post-audit) — Bug 3b: OTA `/my-trip` polling also had same anti-pattern

**File:** `pages/my-trip/index.js:43-66`  
**Root cause (pre-existing):** `useState(false)` + `useEffect` to sync `hasOpenTicket` from poll result — same CLAUDE.md violation. On first render `hasOpenTicket=false` → poll disabled → initial fetch fires (RTK mount default) → effect fires → state updates → poll enables. One render cycle behind, unnecessary re-render.  
**Fix (`09e3f955`):** Removed `hasOpenTicket` state + sync effect. `pollingInterval` now inline: `(booking?.tickets ?? []).some(t => ACTIVE_STATUSES.includes(t.request_status)) ? 60000 : 0`. `booking` in options reads previous render's value — RTK re-reads `pollingInterval` each render so gate self-corrects automatically. No state, no effect, same behavior.

**Pattern confirmed — RTK Query self-correcting pollingInterval:**
RTK Query reads `pollingInterval` from hook options on every render. So `pollingInterval: booking?.tickets?.some(...) ? 60000 : 0` naturally self-corrects: first render `booking=undefined` → 0 → mount fetch fires via RTK default → response arrives → re-render → `booking` now has tickets → pollingInterval evaluates correctly. No extra state needed.

## Tradeoffs

- Bug 3 final fix: no `useState`, no `useEffect`, no TERMINAL_STATUSES in `ChangeRequestsSection`. Parent `[bookingId].js` owns the poll. Child is read-only display.
- Bug 3b OTA fix: inline pollingInterval derivation. One render cycle "lag" on first load is acceptable and was already noted in the original code comment.
- Bug 4/5 deferred: no customer-facing crash risk. Bug 4 = visual gap (OTA customers see less info). Bug 5 = integrity gap (only exploitable via direct API call, not UI).

## Related

- [[cs-centralization-audit-2026-06-29]]
- [[cs-manual-test-flows-b7-e-2026-06-30]]
- [[ota-portal-overview]]
- [[genericfk-one-open-ticket-guard]]
- [[serializer-field-omission-starves-ui]]
