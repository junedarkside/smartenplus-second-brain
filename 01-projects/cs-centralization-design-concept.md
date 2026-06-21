---
name: cs-centralization-design-concept
description: UX/UI design concept for CS Centralization — 3 surfaces (customer chat widget, CS Dashboard, Email-OTP login) built on existing designSystem.js; flows, states, visual+token map, a11y, microcopy. Architecture-agnostic.
metadata:
  type: design
  status: draft
  date: 2026-06-21
  parent: cs-centralization-stack
---

# CS Centralization — Design Concept

> **3-agent design pass 2026-06-21.** UX-flow (ux-research-specialist) + visual/token (senior-frontend) + a11y/microcopy (ux-research-specialist). Built ON existing `helpers/designSystem.js` + `ProfileBottomSheet.js`/`Modal.js`/`login.js` shells. **Architecture-agnostic** — polling vs Supabase Realtime is invisible to UX (handled as a latency affordance).

## Design Principles

1. **Reuse-first** — every element maps to an existing token/shell. New tokens only where a real gap is proven (15 flagged, see Gaps).
2. **Service-first** — marketing consent is honest opt-in, never a gate, never pre-checked, shown once/session, separable from the service action.
3. **Architecture-agnostic** — optimistic echo + sent/delivered/failed states make 0-3s transport latency feel instant. UI never exposes poll vs push.
4. **No positional language in alerts** — element names, not "above/below" (per CLAUDE.md rule).

## ⚠️ Blocking Finding — Design-System Token WCAG Failures

A11y audit measured 3 status tokens + gray400 FAIL WCAG AA as text on white. **Affects the whole feature** and any other feature using these for text.

| Token | Ratio on white | Verdict | Rule applied here |
|---|---|---|---|
| `status.success` #10B981 | 2.54:1 | FAIL | icon/dot only, never text |
| `status.warning` #F59E0B | 2.15:1 | FAIL | icon only |
| `status.error` #EF4444 | 3.76:1 | FAIL (normal weight) | icon + badge-dot only; never error text |
| `neutral.gray400` #9CA3AF | 2.54:1 | FAIL | replaced by gray500 (4.83:1 floor) everywhere |

**Safe pairs used throughout:** white-on-`brand.primary` (6.84:1) · `gray900`-on-`gray100` (16.12:1) · `primaryDark`-on-`primaryLight` (8.93:1) · `brand.secondary` #2563eb on white (5.17:1) · `gray700` on white (8.59:1, used for ALL error/success TEXT).

→ Proposed companion text-tokens `status.successText`/`errorText`/`warningText` (G-05..07 below). **File a design-token audit issue against `helpers/designSystem.js` regardless of CS feature** — these failures pre-exist.

---

## Surface 1 — Customer Chat Widget (frontend)

### Identity branch (resolved on first open, not first message)
- **Direct customer** (`session?.id` truthy): opens straight to thread/empty.
- **OTA guest** (no session): opens to lightweight email-gate (email only — no name/phone, reduce friction); stored sessionStorage `cs_guest_email`; gate skipped on re-open same tab.
- **Guest email collides with existing Account:** info banner "We found an existing account — sign in for full order history" + "Continue as guest". Never silent-merge.

### Happy path (logged-in)
`launcher-closed → [click] → panel-open-empty|with-history → composing → sending(optimistic, opacity 0.5) → sent(tick+time) → reply-received(auto-scroll) → [closed when reply] launcher-unread(badge)`

### State inventory (name every state)
`launcher-closed` · `launcher-unread` · `panel-open-empty` · `panel-open-guest-gate` · `guest-identifying` · `panel-open-with-history` · `loading-history`(skeleton bubbles) · `composing` · `sending` · `sent` · `reply-received` · `error-send-failed`(retry) · `error-history-load-failed` · `error-guest-gate-failed` · `offline-no-network`(draft preserved) · `cs-after-hours`(compose hidden, "Leave a message" CTA) · `cs-queued-mode`(amber banner, compose enabled).

### Edge cases
Reconnect recovery (auto-retry failed on reconnect, only here); multi-tab badge per-tab (sessionStorage not localStorage); panel-close-during-sending (continues background, never drops); long history (>50 → "Load earlier" + no scroll-jump unless within 100px of bottom); mobile back-gesture intercept (pushState like ProfileBottomSheet).

### Visual spec
- **Launcher FAB:** 56×56 circle, `brand.primary` bg, white icon, fixed bottom-right 24px, shadow `ELEVATION_TOKENS.lg`, z `Z_INDEX.notification`(see G-10), transition `TRANSITIONS.fast`. Unread badge 20px, `status.error` bg (non-text), white 12px bold count.
- **Panel desktop:** 380×560 (G-12/13), white, `gray200` border, radius `BORDER_RADIUS.container`, shadow `ELEVATION_TOKENS.xl`, fixed bottom-right above FAB.
- **Panel mobile:** ProfileBottomSheet drawer `anchor=bottom`, radius `16px 16px 0 0`(G-04), `max-height:100dvh`, backdrop rgba(0,0,0,0.35), drag handle 32×4 `gray300`.
- **Header:** `brand.primary` bg h56, title `h3`/semibold white (6.84:1), `status.success` online dot + "Online" text label (a11y — not color-alone), close `IconButton` 44px aria "Close chat".
- **Bubbles:** outgoing `primaryDark`/`primaryLight` (8.93:1) radius `12 12 2 12`(G-01) right; incoming `gray100`/`gray900` (16.12:1) radius `12 12 12 2`(G-02) left + 28px agent avatar(G-14); system `gray50`/`gray700` (7.59:1) centered `caption`. Timestamp `gray500` `caption`.
- **Input bar:** `INPUT_CONFIG.base` + `rounded-lg`, min 44px; send `BUTTON_CONFIG.primary` 44×44; attach `BUTTON_CONFIG.secondary` 44px.

```
DESKTOP PANEL 380×560 (fixed bottom-right)
┌─────────────────────────────────────┐ border gray200, shadow xl
│ [brand.primary h56]  ● Online  [✕]  │ white 6.84:1
├─────────────────────────────────────┤ bg gray50
│   ┌ System gray700/gray50 (center) ┐ │
│ [●]┌ incoming gray900/gray100 ────┐  │
│ CS │ Hi! How can I help?         │  │
│    └─────────────────────────────┘  │ 14:31 gray500
│        ┌ outgoing pLight/pDark ──┐  │
│        │ Need help w/ booking    │  │
│        └─────────────────────────┘  │ 14:32
├─────────────────────────────────────┤
│ ┌ INPUT_CONFIG ──────┐ [▶ 44 primary]│
│ └────────────────────┘ [📎 44]       │
└─────────────────────────────────────┘
[■ FAB 56 ●badge] z:notification
```

---

## Surface 2 — CS Dashboard (admin-dashboard, MUI)

### Assignment model (1-5 staff)
Skip per-agent routing — overkill. **Claim-on-open:** opening a thread + typing claims it (initials badge in list row). 2nd agent within 500ms sees "Handled by {A}. You can still read it." + soft-locked composer with "Override and reply" escape. Revisit at >5 staff / >50 tickets/day.

### Happy path
`inbox-with-list → [click row] → thread-loading(skeleton) → conversation-selected → replying → reply-sent(append, clear, row updates) → resolved(confirm dialog → Closed filter + toast)`. New-msg-while-viewing-other: list row bold+dot, top toast "New message — {name}" (`status.info`, 5s, "View"), current thread NOT interrupted.

### State inventory
`inbox-empty` · `inbox-with-list` · `inbox-loading` · `inbox-filter-open/pending/closed` · `thread-loading` · `conversation-selected` · `replying` · `reply-sent` · `resolved` · `new-message-while-viewing-other` · `error-thread-load-failed` · `error-reply-send-failed`.

### Edge cases
Simultaneous-claim banner; **resolved conv gets new customer reply → auto-reopens to Open** (status must not stay Closed silently); reserve search input ("Search by name or email") from day 1; agent session-expiry warning banner; passive disabled attachment icon (avoids V2 layout refactor).

### Visual spec (MUI + admin `lightTheme.js`)
- Two-pane: list 340px (G-15 selected bg `#E3E8F0`) / thread flex-grow; collapses to push-nav `<sm`.
- List row ≥72px: 40px Avatar (`primary.main` bg initials), name `body1`, preview/time `body2`/`caption` `text.secondary`(gray500 4.83:1), unread dot `primary.main` (non-text).
- **Status chips — icon+label, NOT color-alone:** Open `badge.primary` bg/text (7.95:1) + circle icon; Pending `#FEF3C7`/`#92400E` (9.73:1, G-08/09) + clock; Closed `badge.neutral` (5.74:1) + check. Radius `BORDER_RADIUS.badge`, `caption`/semibold.
- Thread bubbles = Surface 1 spec. Reply: MUI TextField multiline rows=3, char counter `caption` gray500, send MUI contained primary (`#053582` white 8.59:1), Ctrl/Cmd+Enter, disabled `OPACITY.disabled`.

```
DESKTOP two-pane
┌ LIST 340px ────┬ THREAD ──────────────────────┐
│[●]Somchai 14:32│ Somchai W.  [Open ● icon+lbl]│
│ Need help.. ●(2)│ [Close][Assign]              │
│[●]Maria  13:15 │ ┌ agent gray100/gray900 ──┐  │
│ Pay? [Pending⏱]│ │ Looking into it.        │  │ 13:45
│[●]John   11:00 │ └─────────────────────────┘  │
│ Refund [Closed✓]│   ┌ cust pDark/pLight ──┐    │
│                │   │ When resolved?      │    │ 14:02
│                ├──────────────────────────────┤
│                │ [TextField rows=3]  3/500    │
│                │ [📎][⚡Canned]    [SEND 44]  │
└────────────────┴──────────────────────────────┘
```

---

## Surface 3 — Email-OTP Login (frontend)

Reuses `login.js` shell: `min-h-screen bg-white flex center p-4`, `max-w-md` card, Formik+Yup.

### Flow
`email-entry → [submit] → code-requested(spinner) → code-entry → verifying(auto-submit on 6th digit) → success(SuccessState, countdown redirect)`. Branches: wrong-code/expired/resend/rate-limited.

### State inventory
`email-entry` · `code-requested` · `code-entry` · `verifying` · `success` · `error-wrong-code`(clear+refocus, attempts after 2nd fail) · `error-expired`(request-new + change-email) · `error-email-send-failed` · `error-verify-server`(separate from wrong-code) · `resend-cooldown`(60→120→300s backoff) · `rate-limited`(429, full view swap, password-login fallback).

### Code input — single field (recommended over 6 cells)
`<input type=text inputmode=numeric maxlength=6 autocomplete=one-time-code pattern=[0-9]*>` — native iOS/Android OTP autofill works on single input; 6-cell fragments autocomplete in Safari/Chrome mobile; simpler focus; WCAG 1.3.5. Center, `tracking-widest`(`LETTER_SPACING.wider`), `text-2xl` bold, ~56px. Paste distributes/strips non-numeric silently.

### Edge cases
Paste handling (any cell, truncate>6, fill<6 no-error); `inputmode=numeric` not `type=number`; back from code-entry pre-fills email (`otp_pending_email`); mask `j****@domain.com` (never mask domain); callbackUrl chain from chat guest-gate (`?email=&callbackUrl=&openChat=true`); already-authenticated guard redirects before render.

### Visual spec
Heading `h2`/semibold gray900; subtitle `body` gray500; email input `INPUT_CONFIG`; **error icon `status.error` (icon only) + text `gray700` (8.59:1) — NOT red text**; submit `BUTTON_CONFIG.primary` ~48px; links `brand.secondary` (5.17:1); countdown `small` gray500; resend-disabled gray500 (NOT gray400); success icon `status.success` (icon only) + `gray700` text + `SuccessState` component (green check, countdown bar, reuse from login).

---

## Design-System Reuse Map (summary)

| Element | Token/preset | Source |
|---|---|---|
| FAB / header / outgoing-tint bg | `COLORS.brand.primary` / `primaryDark` / `primaryLight` | designSystem.js |
| Incoming bubble | `COLORS.neutral.gray100` + `gray900` | designSystem.js |
| Timestamps / secondary text | `COLORS.neutral.gray500` (4.83:1 floor) | designSystem.js |
| Error/success TEXT | `COLORS.neutral.gray700` (8.59:1) | designSystem.js |
| Inputs | `INPUT_CONFIG.base/focus/error/borderRadius` | designSystem.js |
| Buttons | `BUTTON_CONFIG.primary/secondary` | designSystem.js |
| Badges/chips | `COLORS.badge.primary/neutral` + `BORDER_RADIUS.badge` | designSystem.js |
| Tap targets | `TOUCH_TARGET.minHeight` 44px | designSystem.js |
| Mobile drawer | `ProfileBottomSheet.js` shell | frontend |
| Desktop dialog | `Modal.js` shell | frontend |
| OTP/auth screens | `login.js` layout + `SuccessState` | frontend |
| CS Dashboard | admin `lightTheme.js` palette + MUI Chip/Avatar/TextField | admin |
| Toast | `react-toastify` ^9.1.1 | frontend package.json |
| Lazy mount | `dynamic(ssr:false)` `_app.js:22` | frontend |

## Token Gaps (15 — propose adding to designSystem.js)

| ID | Token | Value | Why |
|---|---|---|---|
| G-01/02 | `BORDER_RADIUS.chatBubbleOutgoing/Incoming` | `12 12 2 12` / `12 12 12 2` | asymmetric tail not coverable |
| G-03 | `BORDER_RADIUS.chatFab` | `50%` | no circle token |
| G-04 | `BORDER_RADIUS.chatDrawerTop` | `16 16 0 0` | codify ProfileBottomSheet value |
| **G-05** | `COLORS.status.successText` | `#065F46` (9.73:1) | success TEXT (status.success fails) |
| **G-06** | `COLORS.status.errorText` | `#991B1B` (6.30:1) | error TEXT (status.error fails) |
| **G-07** | `COLORS.status.warningText` | `#92400E` (9.73:1) | warning TEXT (status.warning fails) |
| G-08/09 | `COLORS.cs.pendingChipBg/Text` | `#FEF3C7`/`#92400E` | pending chip (no amber chip token) |
| G-10 | `Z_INDEX.chatWidget` | `75` | above `notification`(70)/snackbar conflict |
| G-11..14 | `DIMENSIONS.chatFabSize/PanelWidth/PanelHeight/AgentAvatarSize` | 56/380/560/28px | no chat geometry tokens |
| G-15 | `COLORS.cs.listPaneSelectedBg` | `#E3E8F0` | admin-only, document for CS list |

**G-05/06/07 are not just chat gaps — they fix a platform-wide WCAG failure.**

## Latency Affordances (architecture-agnostic)

Message lifecycle: `COMPOSING → ECHOED(optimistic, opacity 0.5, "Sending…" sr-live) → SENDING(0-3s) → SENT(tick, "Sent") → DELIVERED(double tick) ↘ FAILED(red-50 bg, "Message not sent. Tap to retry.", assertive)`. Client-side `messageId` dedupes server echo. FAILED never before 3s. Manual retry only (no silent auto-retry → dup risk) EXCEPT on network-reconnect. Timestamps client-side local time, reconciled on ack. **Never expose transport term in any string.**

## A11y Checklist (WCAG 2.1 AA, all 3 surfaces)

- **Focus:** launcher `<button>` aria-expanded; open → focus into panel (after 300ms transition) → focus-trap (prefer `inert` on page body) → Esc closes → restore to launcher ref. OTP autofocus first input. Dashboard focus → reply box on select.
- **ARIA:** panel `role=dialog aria-modal aria-labelledby`; message list `role=log aria-live=polite aria-relevant=additions`; incoming reply appends without stealing focus; typing indicator separate `aria-live` span; failed-send `role=alert assertive`; dashboard TWO live regions (list-queue polite + active-conv polite), assertive reserved for session/system errors only.
- **Keyboard:** Enter sends / Shift+Enter newline (widget); Ctrl+Enter sends (dashboard pro convention); Esc closes; tab order Close→list→input→send.
- **OTP:** `autocomplete=one-time-code` mandatory + `inputmode=numeric`; error injected into pre-mounted `role=alert` (don't mount/unmount); resend `aria-label` updates with countdown, polite announce at 60/30/0s only (not every sec).
- **Targets:** all interactive ≥44px (`TOUCH_TARGET`); FAB 56px.
- **Contrast:** all text pairs from safe list; status colors icon-only; chips icon+label (1.4.1).

## Microcopy (key strings — full inventory in agent report; warm-professional, no emoji/exclamation)
- Launcher: "Need help?" / aria "Chat with support" · greeting "Hi there. How can we help you today?"
- Response-time (backend category FAST/NORMAL/SLOW → string): "Typically replies in a few minutes." / "…within 20 minutes." / "…within the hour — or leave your email."
- After-hours: "Our support team is offline right now. Leave a message and we'll reply by {next open, backend-computed tz}."
- OTP: "Check your email" / "We sent a 6-digit code to {email}." / "The code expires in {n} min. Didn't receive it? Check spam first."
- Consent (unchecked, once/session, below input after 1st message): "Keep me updated on travel deals and SmartEnPlus news. I can unsubscribe any time." + "This is optional and separate from messages about your booking." Store version+timestamp+surface (GDPR, EU audience).

## Open Design Questions (owner)
1. OTP expiry minutes — backend-driven string, not hardcoded.
2. Response-time category contract (FAST/NORMAL/SLOW) — backend sends category, frontend maps copy. Never raw queue depth to user.
3. Consent string versioning — versioned asset, not editable inline text.
4. After-hours hours source — backend/shared util + `Intl.DateTimeFormat`, never hardcode "ICT".
5. Online/Away manual toggle on dashboard (drives `cs-after-hours`) — confirm.
6. **Token WCAG fix** — add G-05/06/07 text-tokens (or update hex) to `designSystem.js`; file separate audit issue.

## Related
- [[design-systems]] — token source (`helpers/designSystem.js`)
- [[cs-centralization-stack]] — build stack (Option B / arch)
- [[cs-centralization-doc-review]] — architecture review (over-engineering flag)
- [[smarten-customer-os-thesis]] — parent decision
