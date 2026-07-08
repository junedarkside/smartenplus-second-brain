# OTA Chat — Auth Identity Switch Analysis

**Date:** 2026-07-08  
**Status:** ✅ ALL 10 SCENARIOS PASS 2026-07-08. Fixes merged → develop (FE `436499b0` · AD `1b62ed3`). 4 bugs found + fixed during testing (see Bugs Found section below).  
**Linked notes:** [[ota-chat-realtime-impl-2026-07-08]] · [[cs-guest-identity-best-practices]] · [[chat-supabase-migration-plan]] · [[cs-realtime-be-traffic-design-verdict-2026-07-08]]

---

## Architecture Context

| Layer | Key fact |
|-------|---------|
| **State** | ChatWidget reducer: `token` (Bearer) XOR `guestToken` (guest/OTA) — never both |
| **Transport** | `useChatRealtime` OR `useChatPolling` — keyed on `[enabled, conversationId]` |
| **Cleanup trigger** | `conversationId → null` → realtime channel removed + JWT cleared + polling aborted |
| **BE auth rule** | `request.user.is_authenticated` branch wins; guest-token branch only if unauthenticated |
| **Supabase JWT** | 15-min HS256, claim `conversation_id` enforced by RLS; minted per conv per auth tier |
| **OTA identity** | Stored as guest conv (`identity_type=IDENTITY_GUEST`, `user=None`, `guest_email=email`) |

---

## 6 Identity Switch Scenarios

### 1. Guest → Logged-in (while chat open) ✅ Clean

**Trigger:** `session.accessToken` null→value while `state.guestToken` set + `state.status === open`

**Flow:**
1. `login-while-chatting` effect (ChatWidget line 120-132) fires
2. `clearGuestEmail()` → wipes `cs_guest_email` localStorage
3. `dispatch(RESET)` → state = initialState (conversationId null, messages [], tokens null)
4. Realtime cleanup: `cancelled=true`, timer cleared, `setSupabaseToken(null)`, `removeChannel`
5. Polling cleanup: abort in-flight, clear timer, remove listener
6. Next open → authenticated path → new conv + new Supabase channel with Bearer JWT

**Gap:** OTA localStorage key (`ota_conv_*`) NOT cleared on this path. Irrelevant here (/my-trip only) but worth noting.

---

### 2. Guest → OTA Booking (navigate to /my-trip with active guest session) ⚠️ Wrong conv shown

**Trigger:** User was chatting as normal guest, navigates to `/my-trip?token=...`.

**Flow:**
- `otaToken` becomes non-null on /my-trip
- `handleOpen` guard (line 156-161): `state.conversationId && state.guestToken` → TRUE → dispatches `OPEN`, skips OTA path
- User sees OLD guest conversation, not OTA-bound one

**Root cause:** Early-return guard doesn't check whether existing session is OTA-sourced.

**Severity:** Medium — confusing UX. OTA guest with active normal guest session sees wrong conv.

**Fix path (not implemented):**  
On /my-trip mount, if `otaToken` present and current `guestToken` is NOT from this OTA key (check localStorage), force RESET then re-open via OTA path. Simple `useEffect` on `[otaToken]`.

---

### 3. Logged-in → Guest (session expiry / logout) ⚠️ Realtime silent fail

**Not a native UI flow** — happens via external logout, token expiry, another tab.

**Polling path:**
- Next poll hits BE → `is_authenticated=False` → no Bearer → X-CS-Guest-Token missing → 403 PERMISSION_DENIED
- 403 → `onConversationClosed()` callback → `dispatch(RESET)` → clean

**Realtime path:**
- Token refresh at 14-min mark: `mintSupabaseToken(null, null)` → BE returns 403 (no auth)
- `console.warn` only, NO reset dispatched, NO channel teardown
- Supabase channel stays subscribed but RLS rejects all SELECT/INSERT (JWT expired or null)
- **Silent degradation**: chat panel shows no new messages, send silently fails

**Severity:** Medium — realtime mode doesn't self-heal on auth loss. Polling mode heals automatically.

**Fix path (not implemented):**  
In `refreshToken()` catch block of `useChatRealtime`, if error is 401/403, call `onConversationClosed()`. Currently: `console.warn` only.

---

### 4. Logged-in → OTA Booking ✅ Works (product ambiguity)

**Trigger:** Logged-in user visits `/my-trip?token=...`.

**Flow:**
- `otaToken` non-null, `session.accessToken` non-null
- `handleOpen`: `otaToken` check runs BEFORE auth check (line 167 before line 183)
- OTA path: POST `{ota_token}` → creates guest conv → returns `guest_token`
- `SET_CONV`: `token=null`, `guestToken=OTA_guest_token`
- `login-while-chatting` effect: `prev=accessToken`, `curr=accessToken` → no transition → no RESET

**Result:** Logged-in user gets OTA guest conv. Auth session and OTA conv coexist — no conflict (BE ownership OK: guest conv owned by guestToken, not by user). ✅ Works but see deferred finding #6 (product decision: should logged-in user see their auth conv instead?).

---

### 5. OTA → Guest (navigate away from /my-trip) ✅ Works

**Trigger:** OTA conv open, user navigates to non-/my-trip page.

**In-session:** `otaToken` becomes null; `state.guestToken` + `state.conversationId` still set. `handleOpen` early-return → OTA conv stays open. Realtime unaffected (conversationId unchanged).

**After page refresh:** Restore effect guard `if (!otaToken || state.conversationId) return` → skips restore (not on /my-trip). User starts fresh (email form) on non-OTA page. OTA conv preserved server-side; accessible again from /my-trip.

**Result:** Correct behavior. ✅

---

### 6. OTA → Logged-in (login while on /my-trip) ✅ No loop (CORRECTED 2026-07-08)

**Trigger:** OTA guest completes login on /my-trip.

**Flow:**
1. `login-while-chatting` effect: `state.guestToken` (OTA) truthy + `session.accessToken` new → `dispatch(RESET)`
2. Realtime channel torn down, state wiped, chat closes (status='closed')
3. **Restore effect does NOT re-fire** — its deps are `[otaToken]` only; otaToken unchanged by login. (Earlier version of this note wrongly claimed auto-restore.)
4. User re-clicks chat bubble → `handleOpen` → OTA path → POST `{ota_token}` → get-or-create idempotent → **same conv, fresh guest_token**
5. `login-while-chatting` effect: `prev=accessToken` already seen → no second RESET

**No loop.** `prevAccessTokenRef` prevents double-fire. One extra click required after login — acceptable. ✅

**Gap:** OTA localStorage key NOT cleared on this path. If different user logs in on same browser after logout, stale key may restore old OTA conv. Low risk (same device = same trust boundary).

---

## Summary Table

| Scenario | Channel torn down? | New channel? | Self-heals? | Bug? |
|---|---|---|---|---|
| Guest → Login | ✅ YES (RESET) | YES (auth) | ✅ | None |
| Guest → OTA | ❌ NO (early return) | NO | ❌ | ⚠️ Wrong conv shown |
| Login → Guest (expiry) | ❌ NO auto-RESET | NO | Polling ✅ / Realtime ❌ | ⚠️ Realtime silent fail |
| Login → OTA | NO if already open / YES fresh | OTA path | ✅ | Product ambiguity only |
| OTA → Guest | NO (conv preserved) | N/A | ✅ | None |
| OTA → Login | ✅ YES (RESET + restore) | Restored | ✅ | None |

---

## Bugs Queued for Audit Team

| ID | Sev | File | Issue | Fix direction |
|----|-----|------|-------|---------------|
| A | MED | `ChatWidget.js` `handleOpen` | Guest→OTA: early-return skips OTA path → wrong conv | `useEffect` on `[otaToken]`: if otaToken present + guestToken NOT from this OTA key → RESET |
| B | MED | `useChatRealtime.js` `refreshToken()` catch | Login→Guest expiry: 401/403 only warns, no reset → realtime silent fail | On 401/403 in catch, call `onConversationClosed()` |
| C | LOW | `ChatWidget.js` OTA→Login | OTA localStorage key not cleared on login transition | Clear `ota_conv_*` key in `login-while-chatting` effect before RESET |

---

## Implementation Plan (exact edits — executable by any model)

**Repo:** `smartenplus-frontend`. Branch: `fix/ota-chat-auth-switch` off `develop`.  
**Rule:** 3 small edits, 2 files. NO other changes. NO new abstractions.

### Fix A — `components/chat/ChatWidget.js`

Insert new effect AFTER the existing OTA restore effect (the one ending `}, [otaToken]);` around line 118) and BEFORE the `login-while-chatting` effect:

```js
  // Guest→OTA switch: arriving on /my-trip with a non-OTA guest conv in state —
  // reset so the next open goes through the OTA path instead of the old conv.
  // Auth convs (state.token) intentionally untouched — see deferred finding #6.
  useEffect(() => {
    if (!otaToken || !state.conversationId || state.token) return;
    try {
      const key = `ota_conv_${btoa(otaToken).slice(0, 16)}`;
      const stored = localStorage.getItem(key);
      const storedConvId = stored ? JSON.parse(stored).conversationId : null;
      if (state.conversationId !== storedConvId) {
        dispatch({ type: 'RESET' });
      }
    } catch (_) {}
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [otaToken]);
```

Behavior: if current conv IS the OTA conv (id matches stored key) → keep it. Otherwise RESET; user clicks bubble → OTA path opens correct conv.

### Fix B — `hooks/useChatRealtime.js` (2 sub-edits)

**B1.** In `mintSupabaseToken` (line ~14), replace:
```js
  if (!res.ok) throw new Error('supabase-token mint failed');
```
with:
```js
  if (!res.ok) {
    const err = new Error('supabase-token mint failed');
    err.status = res.status;
    throw err;
  }
```
Reason: current error carries no status — catch blocks can't distinguish auth failure from network blip.

**B2.** In `refreshToken()` catch (line ~53-55), replace:
```js
      } catch (err) {
        console.warn('[useChatRealtime] token refresh failed:', err.message);
      }
```
with:
```js
      } catch (err) {
        console.warn('[useChatRealtime] token refresh failed:', err.message);
        // Auth revoked mid-session (logout/expiry) — realtime can't self-heal
        // like polling does (403 → close). Close explicitly.
        if (err.status === 401 || err.status === 403) {
          onConversationClosed?.();
        }
      }
```

Do NOT touch the `setup()` catch — initial-mint failures already leave chat visibly broken (ready stays false) and the restore-TTL guard covers the stale-token case.

### Fix C — `components/chat/ChatWidget.js`

In the `login-while-chatting` effect (line ~120-132), replace:
```js
    if (!prev && curr && state.status === 'open' && state.guestToken) {
      clearGuestEmail();
      dispatch({ type: 'RESET' });
    }
```
with:
```js
    if (!prev && curr && state.status === 'open' && state.guestToken) {
      clearGuestEmail();
      if (otaToken) {
        try { localStorage.removeItem(`ota_conv_${btoa(otaToken).slice(0, 16)}`); } catch (_) {}
      }
      dispatch({ type: 'RESET' });
    }
```
Note: next open on /my-trip re-creates via `ota_token` (get-or-create → same conv, fresh token). No behavior loss.

### Verification

1. `npx eslint components/chat/ChatWidget.js hooks/useChatRealtime.js` → clean
2. Manual: open guest chat on any page → navigate to `/my-trip?token=<valid>` → chat bubble → conv is OTA conv (check AD inbox shows booking chip), NOT old guest conv
3. Manual: open OTA chat → clear session server-side / wait for guest_token expiry → within 14 min realtime closes chat instead of silently hanging
4. Manual: OTA chat open on /my-trip → log in → chat closes → localStorage `ota_conv_*` key gone → click bubble → same OTA conv reopens with fresh token
5. Regression: normal guest OTP flow + logged-in flow unchanged (no edits touch those paths)
6. Existing test suite: `npm test -- __tests__/components/chat/` (note: ChatWidget suite has PRE-EXISTING failure on base — supabase env missing in test env; ignore that one)

### Merge

Commit: `fix(chat): auth identity switch hardening — findings A B C`  
Merge `fix/ota-chat-auth-switch` → `develop` (never main).
