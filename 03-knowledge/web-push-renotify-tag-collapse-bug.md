# web-push-renotify-tag-collapse-bug

## Summary

`showNotification()` with a `tag` that matches an existing notification replaces it silently — no banner fires unless `renotify: true` is set.

## Problem

Web Push spec: when a new notification shares a `tag` with an already-displayed (or queued-to-Notification-Center) notification, the old one is replaced. Default `renotify: false` means the replacement is silent — staff never sees the banner for rapid updates from the same conversation.

Symptom: `showNotification()` promise fulfills, `reg.getNotifications()` shows the item in Chrome's list, macOS Notification Center has it parked — but no banner ever pops.

Most confusing during testing: plain notifications (no `tag`) show fine, individual-option tests pass, but the combined real-code call silently fails. Root cause is a previously parked notification from an earlier test with the same tag.

## Fix

Add `renotify: true` on every `showNotification()` call that uses a `tag`:

```javascript
reg.showNotification('New CS message', {
  body: body?.slice(0, 80) || '',
  icon: '/smartenplus.svg',
  tag: `cs-conv-${conversation_id}`,
  renotify: true,          // ← without this, tag-collapsed replacement = no banner
  data: { url: `/cs?conversation_id=${conversation_id}` },
})
```

Applied in two places:
- `admin-dashboard/pages/dashboard/SideList.js` — chat push (Supabase realtime path)
- `admin-dashboard/public/sw.js` — BE ticket push (pywebpush → service worker)

Tag dedup still works: 10 rapid messages from same conv = 1 notification. Each replacement re-alerts. Intended behavior preserved.

## Commit

`63ef3f4` → branch `fix/push-renotify` → merged to `develop` 2026-07-09.

## Related

- [[staff-push-notification-adr]]
- [[macos-notification-testing-gotchas]]
