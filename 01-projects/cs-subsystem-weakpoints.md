---
name: cs-subsystem-weakpoints
description: Current-state weakpoint audit of the frontend CS chat subsystem (ChatWidget/useChatPolling/guest-token/OTP). 3-agent read-only review 2026-06-23. Feeds the CS centralization work. Source-grounded — overstated agent claims pruned.
metadata:
  type: audit
  status: current
  date: 2026-06-23
  parent: cs-centralization-stack
---

# CS Subsystem — Weakpoints (Current State)

> **3-agent read-only audit 2026-06-23.** Architecture/State + Security/Auth + Error-handling/UX,
> sequential Explore agents. Leader synthesized + **grounded every cited line against source** — agent
> claims that didn't survive verification are listed under [[#Pruned (not real)]] so they aren't re-raised.
> Scope: frontend CS only. This is the **gap map** between today's `ChatWidget` and the target
> [[cs-centralization-design-concept]] (its state inventory names every state this audit finds missing).

## Summary

CS state lives entirely in `components/chat/ChatWidget.js` local `useReducer` — **no Redux, no Context,
no central provider**. Five rounds of guest-403 hotfixes (`cs-guest-403-r2/r3/r5`) patched guest-token +
stale-closure bugs reactively; the *structural* causes remain. Highest-risk themes: (1) auth state can go
stale mid-session, (2) every error path is a silent `console.warn`, (3) no optimistic send so the UI feels
broken on a ≤5s lag. All resolved by the planned centralization + the design concept's state inventory.

## Context

Why now: the hotfix cadence (r2→r5) shows the subsystem is patched per-symptom, not per-cause. This audit
captures the remaining weakpoints once, before more 403-class fires, and grounds them so the centralization
build has a verified punch-list. No code changed in this pass — report only.

## Weakpoints

Severity｜area｜file:line｜impact. Sec items tagged EXPLOIT (needs backend gap to bite) vs FRAGILE.

| Sev | Area | file:line | Impact |
|-----|------|-----------|--------|
| **High** | Arch | `ChatWidget.js:55-79` | No centralized CS state — trapped in widget; polling dead while closed; messages lost on navigation; no cross-component access. Root cause of most below. |
| **High** | Auth | `useChatPolling.js:33,52` FRAGILE | `token` read from closure (`:33`), only in deps at `:52`; guestToken got a ref in r3, token did NOT. On `accessToken` refresh, poll authenticates with stale token until remount. |
| **High** | Auth | `ChatWidget.js:88,96-103` FRAGILE | Session-change race: `session?.accessToken` read once at `:88`; no re-check after async `fetchOrCreateConversation`. Logout/expiry mid-flight → stale creds → 403 class. |
| **High** | Auth | `ChatWidget.js:33-34,113` / `ChatPanel.js:23-24` EXPLOIT | conversationId reused across auth contexts; reducer can hold both `token` + `guestToken`, so both headers ship together. If backend doesn't enforce exclusivity → auth confusion (this IS the 403 class). |
| **High** | Arch | `ChatWidget.js:81-107` | `handleOpen` has no in-flight guard — rapid FAB taps spawn duplicate `fetchOrCreateConversation` calls (race + dup convs). No loading state during 1-2s fetch. |
| **High** | UX | `useChatPolling.js:48`, `ChatPanel.js:33`, `ChatWidget.js:104,114` | All error paths are silent `console.warn` only. No retry, no banner. User sees stale thread / "sent" message that never arrived / NEED_EMAIL form with no reason. |
| **High** | UX | `ChatPanel.js:26-36` | Send has no optimistic echo + no dedup. Sent message appears only on next poll (≤5s). Input clears + button re-enables → user thinks it sent when send may have failed. |
| **Med** | Arch | `ChatWidget.js:37-42` | `ADD_MSGS` blindly appends; no dedup by `msg.id`. Cursor regression / overlapping poll → duplicate bubbles. |
| **Med** | Arch | `ChatWidget.js:41`, `useChatPolling.js:38,44` | Cursor staleness: `nextCursor ?? state.cursor` + `cursor ?? 0`. If API omits `next_cursor`, cursor freezes or resets to 0 → re-fetch from start. |
| **Med** | Arch | `ChatWidget.js:139-140` / `ChatPanel.js:6,23-24` | Auth prop-drilled into render layer — ChatPanel knows the auth scheme; any new scheme touches 3 signatures. |
| **Med** | UX | `useChatPolling.js:59-63` | Visibility listener unthrottled — rapid tab switching fires immediate poll bursts (no debounce/cooldown). |
| **Med** | UX | `csGuestIdentity.js:9-10` | Guest email 24h TTL clears silently. User re-opens, sees NEED_EMAIL form with no explanation → reads as bug. |
| **Med** | UX | `ChatWidget.js:119` | Render guard shows ChatBubble when `status==='open' && !conversationId` — FAB flicker during fetch; spam-clickable (feeds the handleOpen race). |
| **Med** | Sec | `chat-login.js:32-48` FRAGILE | OTP verify: 6-digit code, no client rate-limit/backoff. Brute-force + email-enumeration surface entirely depends on backend throttling. Verify backend enforces. |
| **Low** | Sec | `csGuestIdentity.js:21` FRAGILE | Guest email plain in localStorage — readable by any XSS; no integrity. Auth-adjacent store. |
| **Low** | Sec | `chat-login.js:43` FRAGILE | `err.response?.data?.error` echoed raw into BannerAlert. React-escaped (not XSS), but trusts backend error text. |
| **Low** | Sec | `ChatWidget.js:61`, `ChatGuestForm.js:22`, `chat-login.js:40` FRAGILE | `cs_open_after_login` sessionStorage flag unsigned/client-set — can be planted to auto-open widget (phishing-overlay surface). |
| **Low** | Arch | `pages/_app.js` (chat mount) | ChatWidget mounted globally; widget state not hydrated → lost on hard refresh. |
| **Low** | UX | system-wide | No "agent typing" indicator, no connection-lost / offline banner, no reconnect-recovery. Long agent delay or outage reads as dead chat. |

## Architectural Theme — Centralization

Nearly every High/Med item is a **symptom of the missing central store**: stale auth (no single source of
truth for creds), lost messages (state dies with the unmounted widget), no optimistic echo / retry / dedup
(no place to hold pending+confirmed message state). The fix is not 18 point-patches — it's the centralization
already designed in [[cs-centralization-design-concept]], whose **state inventory names exactly the states
this audit finds absent** (`sending` optimistic, `error-send-failed` retry, `offline-no-network`,
`reply-received`, `error-history-load-failed`). Hotfixing individually risks a 6th regression round.

## Recommended Next Steps (priority — NO patches in this pass)

1. **Centralize CS state** (store/Context) — fixes #1 and unblocks optimistic send, persistence, dedup, retry. Anchor to [[cs-centralization-design-concept]].
2. **Single auth source + mutual exclusivity** — one of Bearer XOR guest-token, derived live (ref or store), never both; re-derive after async. Kills the 403 class at the root.
3. **Optimistic send + dedup by `msg.id`** — pending→sent→failed states, retry affordance.
4. **Error surfacing** — replace silent `console.warn` with user-visible banner + backoff on poll failure.
5. **Backend-side confirm** — OTP rate-limit + guest-token validation (cross-repo check, see [[cs-api-contract]]).
6. **Test gaps** — no `ChatPanel` test file; no error-path / race / send-failure / visibility-burst coverage in widget+hook tests. (`csGuestIdentity` expiry IS tested.)

## Pruned (not real — don't re-raise)

- "`${submittedEmail}` XSS at chat-login.js:66" — React text node, auto-escaped. Non-issue.
- "1kHz / ~1s OTP brute-force" — speculative throughput; real point is *no client rate-limit*, severity Med not High.
- "ChatGuestForm navigates before guest_token settles" — `:23` pushes `/chat-login` (OTP page), not a conversation flow; no token dropped.

## Related

[[cs-centralization-design-concept]] · [[cs-centralization-doc-review]] · [[cs-p0-measurement-protocol]] · [[cs-api-contract]] · [[cs-design-tokens-audit]] · [[frontend-architecture-audit]]
