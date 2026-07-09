# macos-notification-testing-gotchas

## Summary

3 macOS conditions silently suppress browser push notification banners during local development. All return success to the app — no error to diagnose from.

## Gotchas

### 1. Focus / Do Not Disturb active
Moon icon in menu bar = ALL banners suppressed silently. `showNotification()` resolves, notification delivered to Notification Center only — no visible banner.

**Fix:** Control Center → Focus → disable active mode before testing.

### 2. Notification pileup wedges macOS ncd

After ~15+ undismissed notifications accumulate, macOS notification daemon stops showing new banners — silently.

Diagnostic: `reg.getNotifications()` returns a long list AND `showNotification()` resolves → Chrome delivered it, macOS dropped the banner.

**Fix:**
```javascript
// In browser console — clear all piled notifications
navigator.serviceWorker.ready.then(r => r.getNotifications()).then(l => {
  l.forEach(n => n.close())
  console.log('closed', l.length)
})
```
Then in Terminal:
```bash
killall NotificationCenter  # respawns automatically in ~1s
```

### 3. Tab visibility (by design, not a bug)

`SideList.js:151` guards: `document.visibilityState === 'hidden'`. Testing while AD tab is visible → push never fires (staff sees message live in UI — correct behavior).

**Test correctly:** Cmd+T in the SAME Chrome window (new tab opens, AD tab goes behind). Side-by-side windows or split-screen keeps tab "visible" — no push.

## Diagnostic Sequence

Run in AD console before assuming push is broken:

```javascript
// 1. Permission
console.log(Notification.permission)  // must be 'granted'

// 2. SW registered
navigator.serviceWorker.getRegistrations().then(r => console.log('regs:', r))

// 3. Subscription exists
navigator.serviceWorker.ready.then(r => r.pushManager.getSubscription()).then(s => console.log('sub:', s))

// 4. Pileup check
navigator.serviceWorker.ready.then(r => r.getNotifications()).then(l =>
  console.log('piled:', l.length, l.map(n => n.title)))
```

If step 4 shows 10+ items and new banners aren't appearing → pileup. Run fix above.

## Related

- [[web-push-renotify-tag-collapse-bug]]
- [[staff-push-notification-adr]]
