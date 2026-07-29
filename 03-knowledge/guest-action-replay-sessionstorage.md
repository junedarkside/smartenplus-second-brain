# Guest Action Replay via sessionStorage

## Summary
Let a guest-initiated action (that requires auth) auto-complete after login — no re-click. Stash the intent before the login redirect; replay it once on authenticated return.

## Problem
Guest taps a gated button (fav, save, follow) → redirect to login → returns to the same page (via `callbackUrl`) but the action is lost. User must click again. The `callbackUrl` returns the *page* but not the *intent*.

## Pattern
In the shared button component (`BookmarkButton.js`):

1. **Stash before redirect** (unauth branch):
```js
try { sessionStorage.setItem('pendingBookmark', JSON.stringify({ contentType, objectId })); } catch {}
handleUnauthenticated();  // → /account/login?callbackUrl=<page>
```

2. **Replay once on auth return** (mount effect):
```js
const replayedRef = useRef(false);
useEffect(() => {
  if (!session?.accessToken || replayedRef.current) return;
  let pending;
  try { pending = JSON.parse(sessionStorage.getItem('pendingBookmark')); } catch { return; }
  if (!pending || pending.contentType !== contentType || String(pending.objectId) !== String(objectId)) return;
  replayedRef.current = true;
  sessionStorage.removeItem('pendingBookmark');   // clear BEFORE async — one-shot
  createBookmark({ contentType, objectId }).unwrap().catch(e => { if (e?.status !== 409) console.error(e); });
}, [session?.accessToken, contentType, objectId, createBookmark]);
```

## Why it works / guards
- **Match on the full identity** (contentType + objectId) so only the ONE right button on a list of N fires — not all of them.
- **`removeItem` before the async call** so a re-render can't double-fire.
- **`replayedRef`** belt-and-suspenders against re-entry.
- **One-shot, not persistent** — unlike form-state restoration (which persists across many navigations), an intent fires once then is deleted. Do NOT keep the key.
- **409 = already saved = success** (idempotent backend).
- **Silent fill** — the `/check/` query re-runs on auth → button shows the new state. No snackbar needed.

## Tradeoffs
- sessionStorage (not local) — intent dies with the tab, correct for a one-shot.
- Single global key = one pending action at a time. Fine for a tap-then-login flow (user can't queue two).

## Related
- [[session-storage-restoration]] skill (persistent-restore variant — contrast: that keeps the flag; this deletes it)
- [[adr-saved-page-product-favorites]] — shipped here for the fav heart
